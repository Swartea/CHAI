"""Command-line interface for CHAI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from chai.models import Novel
from chai.services import AIService, AIConfig
from chai.engines import StoryPlanner, ChapterWriter, Editor, BookDeconstructor, WorldBuilder
from chai.export import MarkdownExporter, EPUBExporter, PDFExporter
from chai.utils import load_novel, save_novel, create_sample_novel
from chai.db import get_default_db


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CHAI - AI 小说自动化写作系统"""
    pass


@cli.command()
@click.option("--genre", default="玄幻", help="小说类型")
@click.option("--theme", required=True, help="小说主题")
@click.option("--output", "-o", default="output", help="输出目录")
def build_world(genre: str, theme: str, output: str):
    """生成完整的世界观设定（地理、政治、文化、历史、魔法/异能系统）"""
    click.echo(f"正在生成世界观：{genre} - {theme}")

    try:
        ai_service = AIService()
        builder = WorldBuilder(ai_service)

        click.echo("正在生成地理环境...")
        click.echo("正在生成政治结构...")
        click.echo("正在生成文化元素...")
        click.echo("正在生成历史背景...")
        if builder._uses_magic_system(genre):
            click.echo("正在生成魔法/异能系统...")
        click.echo("正在生成社会结构...")

        world = asyncio.run(builder.build_world(genre, theme))

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        import json
        world_file = output_path / "world_setting.json"
        with open(world_file, "w", encoding="utf-8") as f:
            json.dump(world.model_dump(), f, ensure_ascii=False, indent=2)

        click.echo(f"\n世界观生成完成！")
        click.echo(f"  世界名称: {world.name}")
        click.echo(f"  类型: {world.genre}")
        click.echo(f"  地理: {len(world.geography.get('continents', []))} 大陆, {len(world.geography.get('countries', []))} 国家")
        click.echo(f"  政治: {len(world.politics.get('governments', []))} 政府, {len(world.politics.get('factions', []))} 势力")
        click.echo(f"  文化: {len(world.culture.get('religions', []))} 宗教, {len(world.culture.get('traditions', []))} 传统")
        click.echo(f"  历史: {len(world.history.get('eras', []))} 时代, {len(world.history.get('major_events', []))} 重大事件")
        if world.magic_system:
            click.echo(f"  魔法系统: {world.magic_system.name} ({world.magic_system.system_type})")
        if world.social_structure:
            click.echo(f"  社会结构: {len(world.social_structure.classes)} 阶层, {len(world.social_structure.factions)} 势力")
        click.echo(f"\n已保存到 {world_file}")

    except ValueError as e:
        click.echo(f"错误: {e}", err=True)
        click.echo("提示: 请设置 ANTHROPIC_API_KEY 环境变量", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--genre", default="玄幻", help="小说类型")
@click.option("--theme", required=True, help="小说主题")
@click.option("--output", "-o", default="output", help="输出目录")
def create(genre: str, theme: str, output: str):
    """创建新小说项目"""
    click.echo(f"创建{genre}类型小说，主题：{theme}")

    try:
        ai_service = AIService()
        planner = StoryPlanner(ai_service)

        click.echo("正在生成世界观...")
        world = asyncio.run(planner.create_world(genre, theme))

        click.echo("正在生成角色...")
        characters = asyncio.run(planner.create_characters(world, genre))

        click.echo("正在生成大纲...")
        plot = asyncio.run(planner.create_plot_outline(world, characters, genre, theme))

        novel = Novel(
            id="novel_1",
            title=f"{theme}：{world.name}",
            genre=genre,
            world_setting=world,
            characters=characters,
            plot_outline=plot,
        )

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        save_novel(novel, output_path / "novel.json")

        click.echo(f"小说项目已保存到 {output_path / 'novel.json'}")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("novel_file", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="输出目录")
def write(novel_file: str, output: str):
    """根据大纲写作"""
    click.echo("开始写作...")

    try:
        novel = load_novel(novel_file)
        ai_service = AIService()
        writer = ChapterWriter(ai_service)

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        asyncio.run(writer.write_novel(novel))

        save_novel(novel, output_path / "novel_written.json")
        click.echo(f"写作完成，保存到 {output_path / 'novel_written.json'}")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("novel_file", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="输出目录")
def proofread(novel_file: str, output: str):
    """校对小说"""
    click.echo("开始校对...")

    try:
        novel = load_novel(novel_file)
        ai_service = AIService()
        editor = Editor(ai_service)

        asyncio.run(editor.proofread_novel(novel))

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        save_novel(novel, output_path / "novel_proofread.json")
        click.echo(f"校对完成，保存到 {output_path / 'novel_proofread.json'}")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("novel_file", type=click.Path(exists=True))
@click.option("--format", "-f", multiple=True, default=["markdown"], help="导出格式: markdown, epub, pdf")
@click.option("--output", "-o", default="output", help="输出目录")
def export(novel_file: str, format: tuple, output: str):
    """导出小说"""
    try:
        novel = load_novel(novel_file)
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        if "markdown" in format:
            md_exporter = MarkdownExporter()
            md_path = output_path / f"{novel.title}.md"
            md_exporter.export_to_file(novel, md_path)
            click.echo(f"Markdown 导出: {md_path}")

        if "epub" in format:
            epub_exporter = EPUBExporter()
            epub_path = output_path / f"{novel.title}.epub"
            epub_exporter.export_to_file(novel, epub_path)
            click.echo(f"EPUB 导出: {epub_path}")

        if "pdf" in format:
            pdf_exporter = PDFExporter()
            pdf_path = output_path / f"{novel.title}.pdf"
            pdf_exporter.export_to_file(novel, pdf_path)
            click.echo(f"PDF 导出: {pdf_path}")

    except ImportError as e:
        click.echo(f"缺少依赖: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--genre", default="玄幻", help="小说类型")
@click.option("--theme", required=True, help="小说主题")
@click.option("--output", "-o", default="output", help="输出目录")
@click.option("--no-proofread", is_flag=True, default=False, help="跳过校对")
def run(genre: str, theme: str, output: str, no_proofread: bool):
    """运行完整的自动化写作流程（规划→写作→校对）"""
    from chai.engines import NovelEngine

    click.echo(f"启动 CHAI 全流程写作: {genre} - {theme}")

    try:
        ai_service = AIService()
        engine = NovelEngine(ai_service)

        novel = asyncio.run(
            engine.run_full_workflow(
                genre=genre,
                theme=theme,
                proofread=not no_proofread,
            )
        )

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        save_novel(novel, output_path / "novel_complete.json")
        click.echo(f"完成！保存到 {output_path / 'novel_complete.json'}")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
def init():
    """创建示例小说项目"""
    try:
        novel = create_sample_novel()
        save_novel(novel, "sample_novel.json")
        click.echo("示例小说已创建: sample_novel.json")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--genre", default="", help="小说类型筛选")
@click.option("--limit", default=50, help="返回数量")
def list_templates(genre: str, limit: int):
    """列出已存储的拆书模板"""
    try:
        db = get_default_db()
        stats = db.get_stats()
        click.echo(f"数据库统计:")
        click.echo(f"  角色模板: {stats['character_templates']}")
        click.echo(f"  情节模式: {stats['plot_patterns']}")
        click.echo(f"  世界观模板: {stats['world_templates']}")
        click.echo(f"  拆书结果: {stats['deconstruction_results']}")

        if genre:
            click.echo(f"\n类型 '{genre}' 的模板:")
            chars = db.get_character_templates(genre=genre, limit=limit)
            for c in chars:
                click.echo(f"  [角色] {c.name} ({c.template_type.value}) - 使用{c.usage_count}次")
            plots = db.get_plot_patterns(genre=genre, limit=limit)
            for p in plots:
                click.echo(f"  [情节] {p.name} ({p.pattern_type.value}) - 使用{p.usage_count}次")
            worlds = db.get_world_templates(genre=genre, limit=limit)
            for w in worlds:
                click.echo(f"  [世界观] {w.name} ({w.template_type.value}) - 使用{w.usage_count}次")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--entry-id", default=None, help="番茄热词榜词条ID")
@click.option("--entry-name", default=None, help="番茄热词榜词条名称")
@click.option("--genre", default="", help="小说类型筛选（用于热门书籍）")
@click.option("--max-books", default=5, help="最多拆解书籍数量")
def deconstruct(entry_id: str, entry_name: str, genre: str, max_books: int):
    """拆解番茄小说热门书籍，提取模板"""
    async def _run():
        try:
            ai_service = AIService()
        except ValueError:
            click.echo("错误: 请设置 ANTHROPIC_API_KEY 环境变量", err=True)
            sys.exit(1)

        async with BookDeconstructor(ai_service) as deconstructor:
            if entry_id or entry_name:
                click.echo(f"正在从热词榜拆解书籍: {entry_name or entry_id}")
                results = await deconstructor.deconstruct_from_hot_list(
                    entry_id=entry_id,
                    entry_name=entry_name,
                    max_books=max_books,
                )
            else:
                click.echo(f"正在拆解热门书籍 (类型: {genre or '全部'})")
                results = await deconstructor.deconstruct_popular_books(
                    genre=genre,
                    limit=max_books,
                )

            click.echo(f"\n拆解完成！共处理 {len(results)} 本书:")
            for result in results:
                click.echo(f"  - {result.source.book_title}")
                click.echo(f"    角色模板: {len(result.character_templates)}")
                click.echo(f"    情节模式: {len(result.plot_patterns)}")
                click.echo(f"    世界观: {'有' if result.world_template else '无'}")
                click.echo(f"    状态: {result.status}")

    asyncio.run(_run())


@cli.command()
@click.option("--genre", required=True, help="小说类型")
@click.option("--theme", required=True, help="小说主题")
@click.option("--output", "-o", default="output", help="输出目录")
def generate_from_templates(genre: str, theme: str, output: str):
    """基于拆书模板生成小说大纲"""
    async def _run():
        try:
            ai_service = AIService()
        except ValueError:
            click.echo("错误: 请设置 ANTHROPIC_API_KEY 环境变量", err=True)
            sys.exit(1)

        deconstructor = BookDeconstructor(ai_service)
        try:
            click.echo(f"正在基于模板生成大纲: {genre} - {theme}")
            outline = await deconstructor.generate_outline_with_templates(
                genre=genre,
                theme=theme,
            )
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)

            import json
            outline_file = output_path / "outline_from_templates.json"
            with open(outline_file, "w", encoding="utf-8") as f:
                json.dump(outline, f, ensure_ascii=False, indent=2)
            click.echo(f"大纲已保存到 {outline_file}")
        finally:
            await deconstructor.close()

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
