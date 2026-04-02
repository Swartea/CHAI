"""Chapter content generation engine for writing detailed chapter text."""

import uuid
from typing import Optional

from chai.models.chapter_content import (
    ChapterContentType,
    ChapterContentStatus,
    ChapterContentPlan,
    ChapterSectionContent,
    ChapterContentDraft,
    ChapterContentRevision,
    ChapterContentAnalysis,
    ChapterContentTemplate,
    NarrativePoint,
    DialogueStyle,
)
from chai.models.chapter_synopsis import ChapterSynopsis
from chai.models.subplot_foreshadowing import SubplotForeshadowingDesign, Subplot, ForeshadowingElementDetail
from chai.models.climax_ending import ClimaxDesign, EndingDesign, ClimaxEndingSystem
from chai.models.character import Character
from chai.models.world import WorldSetting
from chai.services import AIService


# Standard chapter content templates by type
CHAPTER_TEMPLATES = {
    ChapterContentType.NORMAL: ChapterContentTemplate(
        id="normal_template",
        name="普通章节模板",
        chapter_types=[ChapterContentType.NORMAL],
        section_structure=[
            {"narrative_point": "opening", "name": "开场", "purpose": "建立场景，吸引读者"},
            {"narrative_point": "development", "name": "发展", "purpose": "推进情节"},
            {"narrative_point": "climax", "name": "高潮", "purpose": "冲突或转折"},
            {"narrative_point": "resolution", "name": "收尾", "purpose": "情感余韵"},
        ],
        word_distribution=[0.15, 0.40, 0.25, 0.20],
        pacing_template=["low", "moderate", "high", "moderate"],
        dialogue_ratio=0.3,
        has_hook_ending=True,
        has_scene_breaks=True,
    ),
    ChapterContentType.PROLOGUE: ChapterContentTemplate(
        id="prologue_template",
        name="序章模板",
        chapter_types=[ChapterContentType.PROLOGUE],
        section_structure=[
            {"narrative_point": "opening", "name": "开场", "purpose": "建立氛围"},
            {"narrative_point": "setup", "name": "铺垫", "purpose": "埋下伏笔"},
            {"narrative_point": "development", "name": "发展", "purpose": "悬念推进"},
            {"narrative_point": "climax", "name": "钩子", "purpose": "吸引继续阅读"},
        ],
        word_distribution=[0.20, 0.30, 0.30, 0.20],
        pacing_template=["low", "moderate", "moderate", "high"],
        dialogue_ratio=0.2,
        has_hook_ending=True,
        has_scene_breaks=False,
    ),
    ChapterContentType.EPILOGUE: ChapterContentTemplate(
        id="epilogue_template",
        name="尾声模板",
        chapter_types=[ChapterContentType.EPILOGUE],
        section_structure=[
            {"narrative_point": "resolution", "name": "余韵", "purpose": "情感收尾"},
            {"narrative_point": "development", "name": "交代", "purpose": "交代后事"},
            {"narrative_point": "setup", "name": "展望", "purpose": "展望未来"},
        ],
        word_distribution=[0.30, 0.40, 0.30],
        pacing_template=["moderate", "low", "low"],
        dialogue_ratio=0.25,
        has_hook_ending=False,
        has_scene_breaks=True,
    ),
    ChapterContentType.CLIMAX: ChapterContentTemplate(
        id="climax_template",
        name="高潮章节模板",
        chapter_types=[ChapterContentType.CLIMAX],
        section_structure=[
            {"narrative_point": "setup", "name": "铺垫", "purpose": "积蓄张力"},
            {"narrative_point": "complication", "name": "冲突", "purpose": "矛盾升级"},
            {"narrative_point": "climax", "name": "高潮", "purpose": "爆发点"},
            {"narrative_point": "falling_action", "name": "余波", "purpose": "影响展示"},
        ],
        word_distribution=[0.20, 0.25, 0.35, 0.20],
        pacing_template=["moderate", "high", "climax", "moderate"],
        dialogue_ratio=0.35,
        has_hook_ending=False,
        has_scene_breaks=True,
    ),
    ChapterContentType.BRIDGE: ChapterContentTemplate(
        id="bridge_template",
        name="过渡章节模板",
        chapter_types=[ChapterContentType.BRIDGE],
        section_structure=[
            {"narrative_point": "opening", "name": "承接", "purpose": "承接上文"},
            {"narrative_point": "development", "name": "过渡", "purpose": "平稳过渡"},
            {"narrative_point": "resolution", "name": "伏笔", "purpose": "为下文铺垫"},
        ],
        word_distribution=[0.25, 0.40, 0.35],
        pacing_template=["low", "moderate", "moderate"],
        dialogue_ratio=0.3,
        has_hook_ending=True,
        has_scene_breaks=True,
    ),
    ChapterContentType.TRANSITION: ChapterContentTemplate(
        id="transition_template",
        name="转场章节模板",
        chapter_types=[ChapterContentType.TRANSITION],
        section_structure=[
            {"narrative_point": "resolution", "name": "收尾", "purpose": "结束当前情节"},
            {"narrative_point": "opening", "name": "开场", "purpose": "开启新场景"},
        ],
        word_distribution=[0.45, 0.55],
        pacing_template=["low", "low"],
        dialogue_ratio=0.2,
        has_hook_ending=True,
        has_scene_breaks=False,
    ),
}


class ChapterContentEngine:
    """Engine for generating detailed chapter content."""

    def __init__(self, ai_service: AIService):
        """Initialize chapter content engine with AI service."""
        self.ai_service = ai_service

    async def generate_content(
        self,
        synopsis: ChapterSynopsis,
        world_setting: Optional[WorldSetting] = None,
        characters: Optional[list[Character]] = None,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
        climax_ending_system: Optional[ClimaxEndingSystem] = None,
        previous_chapter_summary: Optional[str] = None,
        previous_chapter_content: Optional[str] = None,
    ) -> ChapterContentDraft:
        """Generate chapter content from synopsis.

        Args:
            synopsis: Chapter synopsis to expand
            world_setting: World setting for context
            characters: Character list for voice consistency
            subplot_design: Subplot and foreshadowing design
            climax_ending_system: Climax and ending system for climax chapters
            previous_chapter_summary: Previous chapter summary for continuity
            previous_chapter_content: Previous chapter content for style matching

        Returns:
            ChapterContentDraft with generated content
        """
        draft_id = f"draft_{uuid.uuid4().hex[:8]}"

        # Determine chapter type
        chapter_type = self._determine_chapter_type(synopsis)

        # Get template
        template = CHAPTER_TEMPLATES.get(
            chapter_type,
            CHAPTER_TEMPLATES[ChapterContentType.NORMAL]
        )

        # Build content plan
        plan = self._build_content_plan(
            synopsis=synopsis,
            chapter_type=chapter_type,
            template=template,
            subplot_design=subplot_design,
            climax_ending_system=climax_ending_system,
            previous_chapter_summary=previous_chapter_summary,
        )

        # Generate section content
        section_contents = await self._generate_sections(
            plan=plan,
            world_setting=world_setting,
            characters=characters,
            template=template,
        )

        # Combine into full content
        full_content = self._combine_sections(section_contents)

        # Calculate word count
        word_count = self._count_chinese_words(full_content)

        # Build draft
        draft = ChapterContentDraft(
            id=draft_id,
            plan_id=plan.id,
            chapter_number=synopsis.chapter_number,
            title=synopsis.title,
            content=full_content,
            section_contents=section_contents,
            word_count=word_count,
            meets_target=template.min_word_count <= word_count <= template.max_word_count,
            status=ChapterContentStatus.COMPLETE,
        )

        return draft

    def _determine_chapter_type(self, synopsis: ChapterSynopsis) -> ChapterContentType:
        """Determine chapter type from synopsis."""
        if synopsis.is_prologue:
            return ChapterContentType.PROLOGUE
        if synopsis.is_epilogue:
            return ChapterContentType.EPILOGUE
        if synopsis.is_climax_chapter:
            return ChapterContentType.CLIMAX
        if synopsis.is_bridge:
            return ChapterContentType.BRIDGE
        return ChapterContentType.NORMAL

    def _build_content_plan(
        self,
        synopsis: ChapterSynopsis,
        chapter_type: ChapterContentType,
        template: ChapterContentTemplate,
        subplot_design: Optional[SubplotForeshadowingDesign],
        climax_ending_system: Optional[ClimaxEndingSystem],
        previous_chapter_summary: Optional[str],
    ) -> ChapterContentPlan:
        """Build content plan from synopsis."""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        # Determine target word count based on chapter type
        if chapter_type == ChapterContentType.CLIMAX:
            target = 4000
        elif chapter_type == ChapterContentType.PROLOGUE:
            target = 2500
        else:
            target = synopsis.word_count_target or 3000

        # Build sections from template
        sections = []
        for i, section_def in enumerate(template.section_structure):
            section = ChapterSectionContent(
                id=f"{plan_id}_sec_{i + 1}",
                narrative_point=NarrativePoint(section_def["narrative_point"]),
                order=i + 1,
                purpose=section_def["purpose"],
                location=synopsis.primary_location if i == 0 else "",
                time_period=synopsis.time_setting if i == 0 else "",
            )
            sections.append(section)

        # Get subplot IDs relevant to this chapter
        subplot_ids = []
        foreshadowing_to_plant = []
        foreshadowing_to_payoff = []

        if subplot_design:
            for subplot in subplot_design.subplots:
                if str(synopsis.chapter_number) in str(subplot.related_chapters):
                    subplot_ids.append(subplot.id)

            for element in subplot_design.foreshadowing_elements:
                if element.planting_chapter == synopsis.chapter_number:
                    foreshadowing_to_plant.append(element.id)
                if element.payoff_chapter == synopsis.chapter_number:
                    foreshadowing_to_payoff.append(element.id)

        # Get climax elements if climax chapter
        climax_element_ids = []
        if chapter_type == ChapterContentType.CLIMAX and climax_ending_system:
            for design in climax_ending_system.climax_designs:
                if design.chapter_range[0] <= synopsis.chapter_number <= design.chapter_range[1]:
                    climax_element_ids.append(design.id)

        plan = ChapterContentPlan(
            id=plan_id,
            chapter_synopsis_id=synopsis.id,
            chapter_number=synopsis.chapter_number,
            title=synopsis.title,
            chapter_type=chapter_type,
            sections=sections,
            target_word_count=target,
            min_word_count=int(target * 0.8),
            max_word_count=int(target * 1.2),
            pov_character=synopsis.pov_character,
            pov_third_person=True,
            characters_present=synopsis.characters_present,
            primary_location=synopsis.primary_location,
            time_setting=synopsis.time_setting,
            plot_points_to_cover=synopsis.plot_point_ids,
            subplot_ids=subplot_ids,
            foreshadowing_to_plant=foreshadowing_to_plant,
            foreshadowing_to_payoff=foreshadowing_to_payoff,
            is_climax_chapter=chapter_type == ChapterContentType.CLIMAX,
            climax_element_ids=climax_element_ids,
            emotional_arc=synopsis.chapter_emotional_arc,
            pacing_notes=synopsis.pacing_notes,
            status=ChapterContentStatus.PENDING,
            previous_chapter_summary=previous_chapter_summary,
        )

        return plan

    async def _generate_sections(
        self,
        plan: ChapterContentPlan,
        world_setting: Optional[WorldSetting],
        characters: Optional[list[Character]],
        template: ChapterContentTemplate,
    ) -> list[ChapterSectionContent]:
        """Generate content for each section."""
        sections = []
        world_info = world_setting.model_dump() if world_setting else {}
        char_info = [c.model_dump() for c in (characters or [])]

        for i, section in enumerate(plan.sections):
            section_word_target = int(
                plan.target_word_count * template.word_distribution[i]
            )

            # Build prompt for this section
            prompt = self._build_section_prompt(
                section=section,
                plan=plan,
                template=template,
                world_info=world_info,
                char_info=char_info,
                word_target=section_word_target,
            )

            # Generate content
            content = await self.ai_service.generate(prompt, temperature=0.75)

            # Update section with content
            section.content = content
            section.word_count = self._count_chinese_words(content)
            section.characters_present = plan.characters_present
            section.pov_character = plan.pov_character
            section.location = plan.primary_location
            section.time_period = plan.time_setting

            # Add tension level from template
            if i < len(template.pacing_template):
                section.tension_level = template.pacing_template[i]

            sections.append(section)

        return sections

    def _build_section_prompt(
        self,
        section: ChapterSectionContent,
        plan: ChapterContentPlan,
        template: ChapterContentTemplate,
        world_info: dict,
        char_info: list[dict],
        word_target: int,
    ) -> str:
        """Build prompt for section generation."""
        char_names = []
        for cid in plan.characters_present[:5]:
            for c in char_info:
                if c.get("id") == cid:
                    char_names.append(c.get("name", cid))
                    break

        prompt = f"""生成第{plan.chapter_number}章的「{section.purpose}」部分。

章节类型：{plan.chapter_type.value}
章节标题：{plan.title}
叙事位置：{section.narrative_point.value}
部分目的：{section.purpose}

{f"POV角色：{plan.pov_character}" if plan.pov_character else ""}
出场角色：{', '.join(char_names) if char_names else '主要角色'}
{f"主要场景：{plan.primary_location}" if plan.primary_location else ""}
{f"时间设定：{plan.time_setting}" if plan.time_setting else ""}

"""

        if plan.emotional_arc:
            prompt += f"本章情感弧线：{plan.emotional_arc}\n"

        if plan.is_climax_chapter:
            prompt += "这是本章的高潮章节，需要有强烈的情感冲击和冲突爆发。\n"

        if plan.foreshadowing_to_plant:
            prompt += f"本章需要埋下的伏笔：{', '.join(plan.foreshadowing_to_plant)}\n"

        if plan.foreshadowing_to_payoff:
            prompt += f"本章需要回收的伏笔：{', '.join(plan.foreshadowing_to_payoff)}\n"

        if plan.previous_chapter_summary:
            prompt += f"前章概要：{plan.previous_chapter_summary}\n"

        prompt += f"""
写作要求：
- 目标字数：{word_target}字
- 对话比例：{int(template.dialogue_ratio * 100)}%
- 描述密度：{template.description_density}
- 使用中文写作
- 叙事视角：第三人称
- 保持角色性格一致
"""

        if plan.is_climax_chapter:
            prompt += "- 高潮部分要有足够的张力和情感冲击\n"

        if template.has_hook_ending and section.narrative_point == NarrativePoint.RESOLUTION:
            prompt += "- 结尾要有钩子，吸引读者继续阅读\n"

        return prompt

    def _combine_sections(self, sections: list[ChapterSectionContent]) -> str:
        """Combine sections into full chapter content."""
        parts = []
        for section in sections:
            if section.content:
                parts.append(section.content)

        return "\n\n".join(parts)

    def _count_chinese_words(self, text: str) -> int:
        """Count Chinese words (characters as words)."""
        if not text:
            return 0
        # Count Chinese characters and words
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = sum(len(w) for w in re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words

    async def revise_content(
        self,
        draft: ChapterContentDraft,
        revision: ChapterContentRevision,
        world_setting: Optional[WorldSetting] = None,
        characters: Optional[list[Character]] = None,
    ) -> ChapterContentDraft:
        """Revise chapter content based on revision notes.

        Args:
            draft: Draft to revise
            revision: Revision notes
            world_setting: World setting for context
            characters: Character list

        Returns:
            Revised draft
        """
        # Build revision prompt
        prompt = f"""修订以下章节内容。

章节标题：{draft.title}
章节内容：
{draft.content}

修订类型：{revision.revision_type}
问题描述：
{chr(10).join(f"- {issue}" for issue in revision.issues)}

需要修改的部分：
{chr(10).join(f"- {change}" for change in revision.changes_needed)}

请直接输出修订后的完整章节内容，保持原有风格和其他部分不变。"""

        # Generate revised content
        revised_content = await self.ai_service.generate(prompt, temperature=0.7)

        # Update draft
        draft.content = revised_content
        draft.word_count = self._count_chinese_words(revised_content)
        draft.status = ChapterContentStatus.REVISED
        draft.revision_notes.extend(revision.changes_needed)

        return draft

    async def analyze_content(
        self,
        draft: ChapterContentDraft,
        plan: ChapterContentPlan,
        subplot_design: Optional[SubplotForeshadowingDesign] = None,
    ) -> ChapterContentAnalysis:
        """Analyze chapter content quality.

        Args:
            draft: Draft to analyze
            plan: Original content plan
            subplot_design: Subplot design for foreshadowing analysis

        Returns:
            ChapterContentAnalysis
        """
        analysis = ChapterContentAnalysis(draft_id=draft.id)

        # Word count analysis
        if plan.target_word_count > 0:
            analysis.word_count_ratio = draft.word_count / plan.target_word_count

        # Check for key structural elements
        content = draft.content
        analysis.has_clear_opening = len(content) > 0 and content[0] not in ['"', "「", "」"]
        analysis.has_climax = any(keyword in content for keyword in ['突然', '然而', '就在此时', '没想到'])

        # Foreshadowing analysis
        if subplot_design:
            planted = len(plan.foreshadowing_to_plant)
            paid_off = len(plan.foreshadowing_to_payoff)
            analysis.foreshadowing_planted_count = planted
            analysis.foreshadowing_payoff_count = paid_off
            if planted > 0:
                analysis.foreshadowing_balance = min(1.0, paid_off / planted)
            else:
                analysis.foreshadowing_balance = 1.0

        # Calculate overall quality score
        scores = []
        if analysis.word_count_ratio > 0.8 and analysis.word_count_ratio < 1.2:
            scores.append(1.0)
        else:
            scores.append(max(0.0, 1.0 - abs(analysis.word_count_ratio - 1.0)))

        if analysis.has_clear_opening:
            scores.append(1.0)
        if analysis.has_climax:
            scores.append(1.0)

        analysis.overall_quality_score = sum(scores) / len(scores) if scores else 0.5

        # Identify issues
        if analysis.word_count_ratio < 0.7:
            analysis.critical_issues.append("章节字数过少，可能内容不够充实")
        elif analysis.word_count_ratio > 1.3:
            analysis.critical_issues.append("章节字数过多，可能需要精简")

        if not analysis.has_climax and plan.is_climax_chapter:
            analysis.critical_issues.append("高潮章节缺少明显的高潮点")

        return analysis

    def get_template(
        self,
        chapter_type: ChapterContentType,
    ) -> ChapterContentTemplate:
        """Get chapter content template by type."""
        return CHAPTER_TEMPLATES.get(
            chapter_type,
            CHAPTER_TEMPLATES[ChapterContentType.NORMAL]
        )

    def export_draft(self, draft: ChapterContentDraft) -> dict:
        """Export draft as dictionary."""
        return {
            "id": draft.id,
            "chapter_number": draft.chapter_number,
            "title": draft.title,
            "content": draft.content,
            "word_count": draft.word_count,
            "meets_target": draft.meets_target,
            "status": draft.status.value,
            "coherence_score": draft.coherence_score,
            "pacing_score": draft.pacing_score,
            "has_plot_advancement": draft.has_plot_advancement,
            "has_character_development": draft.has_character_development,
        }