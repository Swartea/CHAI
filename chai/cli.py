"""Command-line interface for CHAI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from chai.models import Novel
from chai.services import AIService, AIConfig
from chai.engines import StoryPlanner, ChapterWriter, Editor
from chai.export import MarkdownExporter, EPUBExporter, PDFExporter
from chai.utils import load_novel, save_novel, create_sample_novel


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CHAI - AI 小说自动化写作系统"""
    pass


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


if __name__ == "__main__":
    cli()
