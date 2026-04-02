"""Chapter writing engine."""

from typing import Optional
from chai.models import Novel, Chapter, Volume, Scene, SceneType
from chai.services import AIService


class ChapterWriter:
    """Engine for generating chapter content."""

    def __init__(self, ai_service: AIService):
        """Initialize chapter writer with AI service."""
        self.ai_service = ai_service

    async def write_chapter(
        self,
        novel: Novel,
        chapter_number: int,
        chapter_outline: dict,
        previous_chapter: Optional[Chapter] = None,
    ) -> Chapter:
        """Write a single chapter."""
        chapter_summary = previous_chapter.summary if previous_chapter else None

        content = await self.ai_service.generate_chapter(
            chapter_outline=chapter_outline,
            world_setting=novel.world_setting.model_dump() if novel.world_setting else {},
            characters=[c.model_dump() for c in novel.characters],
            previous_chapter_summary=chapter_summary,
        )

        chapter = Chapter(
            id=f"ch_{chapter_number}",
            number=chapter_number,
            title=chapter_outline.get("title", f"第{chapter_number}章"),
            summary=chapter_outline.get("summary", ""),
            content=content,
            word_count=len(content),
            target_word_count=novel.target_chapter_word_count[1]
                if novel.target_chapter_word_count else 3000,
            status="complete",
        )

        return chapter

    async def write_scene(
        self,
        novel: Novel,
        scene_outline: dict,
        scene_type: SceneType = SceneType.NARRATIVE,
    ) -> str:
        """Write a single scene of a specific type.

        Args:
            novel: The novel object
            scene_outline: Scene outline dict with location, characters, purpose
            scene_type: Type of scene (dialogue, action, description, etc.)

        Returns:
            Generated scene content
        """
        prompt = self._build_scene_prompt(novel, scene_outline, scene_type)
        return await self.ai_service.generate(prompt, temperature=0.75)

    def _build_scene_prompt(
        self,
        novel: Novel,
        scene_outline: dict,
        scene_type: SceneType,
    ) -> str:
        """Build prompt for scene generation based on scene type."""
        base = f"""生成一个{scene_outline.get('location', '未知地点')}的场景。

场景类型：{scene_type.value}
场景目的：{scene_outline.get('purpose', '')}
涉及角色：{', '.join(scene_outline.get('character_names', []))}
氛围：{scene_outline.get('mood', '中性')}

"""

        if scene_type == SceneType.DIALOGUE:
            base += """要求：
- 以对话为主，体现角色性格
- 对话自然流畅，符合角色设定
- 配合适当的动作和表情描写
- 控制字数在300-500字
"""
        elif scene_type == SceneType.ACTION:
            base += """要求：
- 以动作描写为主
- 动作连贯，节奏紧凑
- 配合环境描写
- 控制字数在300-500字
"""
        elif scene_type == SceneType.DESCRIPTION:
            base += """要求：
- 以环境/氛围描写为主
- 细节丰富，有画面感
- 为情节发展铺垫
- 控制字数在300-500字
"""
        elif scene_type == SceneType.REFLECTION:
            base += """要求：
- 以内心活动为主
- 展现角色心理变化
- 与情节发展呼应
- 控制字数在300-500字
"""
        else:  # NARRATIVE
            base += """要求：
- 叙事为主，平衡描写与情节
- 场景描写生动
- 情节推进自然
- 控制字数在300-500字
"""

        base += f"\n世界观背景：{novel.world_setting.name if novel.world_setting else '未知'}"
        return base

    async def write_chapter_with_scenes(
        self,
        novel: Novel,
        chapter_number: int,
        chapter_outline: dict,
        scene_plan: list[dict],
        previous_chapter: Optional[Chapter] = None,
    ) -> Chapter:
        """Write a chapter by generating scenes individually and combining.

        Args:
            novel: The novel object
            chapter_number: Chapter number
            chapter_outline: Chapter outline dict
            scene_plan: List of scene outlines to generate
            previous_chapter: Previous chapter for continuity

        Returns:
            Complete Chapter with scenes
        """
        scenes = []
        previous_scene_summary = None

        for i, scene_outline in enumerate(scene_plan):
            scene_type = SceneType(scene_outline.get("type", "narrative"))
            scene_content = await self.write_scene(novel, scene_outline, scene_type)

            scene = Scene(
                id=f"scene_{chapter_number}_{i}",
                number=i + 1,
                scene_type=scene_type,
                location=scene_outline.get("location", ""),
                time_period=scene_outline.get("time_period", ""),
                characters=scene_outline.get("character_ids", []),
                content=scene_content,
                mood=scene_outline.get("mood", ""),
                purpose=scene_outline.get("purpose", ""),
            )
            scenes.append(scene)

            # Update summary for continuity
            if scene_content:
                previous_scene_summary = scene_content[-200:] if len(scene_content) > 200 else scene_content

        # Combine scenes into chapter content
        combined_content = "\n\n".join(s.content for s in scenes)

        chapter = Chapter(
            id=f"ch_{chapter_number}",
            number=chapter_number,
            title=chapter_outline.get("title", f"第{chapter_number}章"),
            summary=chapter_outline.get("summary", ""),
            content=combined_content,
            word_count=len(combined_content),
            target_word_count=novel.target_chapter_word_count[1]
                if novel.target_chapter_word_count else 3000,
            scenes=scenes,
            status="complete",
        )

        return chapter

    async def write_volume(
        self,
        novel: Novel,
        volume: Volume,
        start_chapter: int,
    ) -> Volume:
        """Write all chapters in a volume."""
        previous_chapter = None

        for i, chapter_outline in enumerate(volume.chapters):
            chapter = await self.write_chapter(
                novel=novel,
                chapter_number=start_chapter + i,
                chapter_outline=chapter_outline.model_dump()
                    if hasattr(chapter_outline, 'model_dump') else chapter_outline,
                previous_chapter=previous_chapter,
            )
            volume.chapters[i] = chapter
            previous_chapter = chapter

        return volume

    async def write_novel(self, novel: Novel) -> Novel:
        """Write entire novel chapter by chapter."""
        previous_chapter = None
        all_chapters = []

        for volume in novel.volumes:
            for i, chapter_outline in enumerate(volume.chapters):
                chapter = await self.write_chapter(
                    novel=novel,
                    chapter_number=len(all_chapters) + 1,
                    chapter_outline=chapter_outline.model_dump()
                        if hasattr(chapter_outline, 'model_dump') else chapter_outline,
                    previous_chapter=previous_chapter,
                )
                all_chapters.append(chapter)
                previous_chapter = chapter

        total_words = sum(c.word_count for c in all_chapters)
        print(f"Written {len(all_chapters)} chapters, {total_words} total words")

        return novel
