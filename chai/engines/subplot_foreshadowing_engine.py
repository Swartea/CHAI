"""Subplot and foreshadowing design engine for comprehensive story crafting."""

from datetime import datetime
from typing import Optional
import uuid

from chai.models.subplot_foreshadowing import (
    SubplotType,
    SubplotStatus,
    SubplotImportance,
    SubplotConnection,
    ForeshadowingTechnique,
    ForeshadowingStrength,
    ForeshadowingPattern,
    ForeshadowingPlanting,
    ForeshadowingPayoff,
    SubplotChapterBeat,
    SubplotArc,
    Subplot,
    ForeshadowingElementDetail,
    SubplotForeshadowingSystem,
    SubplotAnalysis,
    ForeshadowingAnalysis,
    SubplotForeshadowingDesign,
)
from chai.services import AIService


# Template subplot structures by type
SUBPLOT_TEMPLATES = {
    SubplotType.ROMANTIC: {
        "stages": ["相遇", "吸引", "误会", "加深", "危机", "突破", "圆满"],
        "tension_curve": [0.2, 0.4, 0.6, 0.5, 0.8, 0.9, 1.0],
    },
    SubplotType.RIVALRY: {
        "stages": ["对立", "摩擦", "升级", "决战", "胜负", "余波"],
        "tension_curve": [0.3, 0.4, 0.7, 1.0, 0.8, 0.3],
    },
    SubplotType.REDEMPTION: {
        "stages": ["堕落", "觉醒", "挣扎", "弥补", "考验", "救赎"],
        "tension_curve": [0.5, 0.3, 0.6, 0.4, 0.8, 1.0],
    },
    SubplotType.MYSTERY: {
        "stages": ["发现", "调查", "线索", "迷雾", "突破", "真相"],
        "tension_curve": [0.2, 0.4, 0.5, 0.6, 0.8, 1.0],
    },
    SubplotType.GROWTH: {
        "stages": ["起点", "挫折", "学习", "应用", "挑战", "突破"],
        "tension_curve": [0.2, 0.5, 0.3, 0.5, 0.8, 1.0],
    },
    SubplotType.BETRAYAL: {
        "stages": ["信任", "裂痕", "暴露", "对抗", "后果", "重建"],
        "tension_curve": [0.1, 0.4, 0.9, 0.8, 0.6, 0.4],
    },
    SubplotType.CONSPIRACY: {
        "stages": ["平静", "异常", "发现", "追踪", "对抗", "揭露"],
        "tension_curve": [0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
    },
    SubplotType.SACRIFICE: {
        "stages": ["美好", "危机", "抉择", "牺牲", "影响", "铭记"],
        "tension_curve": [0.2, 0.6, 0.9, 1.0, 0.5, 0.3],
    },
}

# Foreshadowing templates by technique
FORESIGHTING_TEMPLATES = {
    ForeshadowingTechnique.DIRECT_HINT: {
        "plant_methods": ["角色对话", "旁白描述", "文字记录"],
        "subtlety": 0.2,
    },
    ForeshadowingTechnique.CHEKHOVS_GUN: {
        "plant_methods": ["引入并提及", "暂时不用", "关键时刻"],
        "subtlety": 0.4,
    },
    ForeshadowingTechnique.DRAMATIC_IRONY: {
        "plant_methods": ["读者知情", "角色不知", "对比呈现"],
        "subtlety": 0.3,
    },
    ForeshadowingTechnique.ATMOSPHERIC_HINT: {
        "plant_methods": ["环境描写", "天气暗示", "氛围营造"],
        "subtlety": 0.7,
    },
    ForeshadowingTechnique.SYMBOLIC: {
        "plant_methods": ["物品象征", "颜色暗示", "自然意象"],
        "subtlety": 0.6,
    },
    ForeshadowingTechnique.OBJECT_SYMBOL: {
        "plant_methods": ["物品象征", "颜色暗示", "自然意象"],
        "subtlety": 0.6,
    },
}


class SubplotForeshadowingEngine:
    """Engine for designing and managing subplots and foreshadowing."""

    def __init__(self, ai_service: AIService):
        """Initialize the engine with AI service."""
        self.ai_service = ai_service

    async def generate_subplot(
        self,
        subplot_name: str,
        subplot_type: SubplotType,
        primary_characters: list[str],
        start_chapter: int,
        end_chapter: int,
        main_story_context: Optional[str] = None,
        importance: SubplotImportance = SubplotImportance.MODERATE,
    ) -> Subplot:
        """Generate a complete subplot.

        Args:
            subplot_name: Name of the subplot
            subplot_type: Type of subplot
            primary_characters: Character IDs involved
            start_chapter: Starting chapter
            end_chapter: Ending chapter
            main_story_context: Optional context from main story
            importance: Importance level

        Returns:
            Complete Subplot object
        """
        subplot_id = f"subplot_{uuid.uuid4().hex[:8]}"
        template = SUBPLOT_TEMPLATES.get(
            subplot_type,
            {"stages": ["开始", "发展", "高潮", "结束"], "tension_curve": [0.3, 0.6, 1.0, 0.4]}
        )

        # Generate AI-assisted content
        ai_content = await self._generate_subplot_content(
            subplot_name=subplot_name,
            subplot_type=subplot_type,
            primary_characters=primary_characters,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            main_story_context=main_story_context,
        )

        # Calculate chapter beats
        chapter_beats = self._generate_chapter_beats(
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            template=template,
            ai_content=ai_content,
        )

        # Find peak chapter (highest tension)
        tension_values = [beat.tension_level for beat in chapter_beats]
        peak_idx = tension_values.index(max(tension_values)) if tension_values else 0
        peak_chapter = chapter_beats[peak_idx].chapter if chapter_beats else start_chapter

        # Build subplot arc
        arc = SubplotArc(
            id=f"{subplot_id}_arc",
            name=subplot_name,
            subplot_type=subplot_type,
            primary_characters=primary_characters,
            introduction=ai_content.get("introduction", f"{subplot_name}的开始"),
            rising_action=ai_content.get("rising_action", []),
            climax=ai_content.get("climax", f"{subplot_name}的高潮"),
            falling_action=ai_content.get("falling_action", []),
            resolution=ai_content.get("resolution", f"{subplot_name}的解决"),
            chapter_beats=chapter_beats,
            thematic_connection=ai_content.get("thematic_connection", ""),
            emotional_tone=ai_content.get("emotional_tone", "中性"),
        )

        subplot = Subplot(
            id=subplot_id,
            name=subplot_name,
            subplot_type=subplot_type,
            importance=importance,
            estimated_word_count=self._estimate_word_count(start_chapter, end_chapter, importance),
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            peak_chapter=peak_chapter,
            involved_characters=primary_characters,
            primary_conflict=ai_content.get("primary_conflict", ""),
            connection_to_main=SubplotConnection.PARALLEL,
            main_story_dependency=ai_content.get("dependency", ""),
            arc=arc,
            status=SubplotStatus.PLANNED,
            foreshadowing_elements=[],
            coherence_score=0.8,
            reader_satisfaction=0.75,
        )

        return subplot

    async def generate_foreshadowing(
        self,
        name: str,
        foreshadows: str,
        technique: ForeshadowingTechnique,
        plant_chapter: int,
        payoff_chapter: int,
        linked_subplot_id: Optional[str] = None,
        related_characters: Optional[list[str]] = None,
        pattern_type: Optional[ForeshadowingPattern] = None,
    ) -> ForeshadowingElementDetail:
        """Generate a foreshadowing element.

        Args:
            name: Descriptive name
            foreshadows: What event it foreshadows
            technique: Foreshadowing technique
            plant_chapter: Chapter to plant
            payoff_chapter: Chapter to payoff
            linked_subplot_id: Optional linked subplot
            related_characters: Characters connected
            pattern_type: Optional pattern classification

        Returns:
            ForeshadowingElementDetail object
        """
        foreshadowing_id = f"fore_{uuid.uuid4().hex[:8]}"
        template = FORESIGHTING_TEMPLATES.get(
            technique,
            {"plant_methods": ["描述"], "subtlety": 0.5}
        )

        # Generate presentation method
        presentation = await self._generate_presentation(
            technique=technique,
            plant_chapter=plant_chapter,
            foreshadows=foreshadows,
        )

        # Calculate reinforcement chapters (1-2 chapters before payoff)
        reinforcement = []
        if payoff_chapter - plant_chapter > 3:
            reinforcement = [
                (plant_chapter + payoff_chapter) // 2,
                payoff_chapter - 2,
            ]

        planting = ForeshadowingPlanting(
            technique=technique,
            chapter=plant_chapter,
            scene_location=presentation.get("location", ""),
            presentation_method=presentation.get("method", ""),
            supporting_context=presentation.get("context", ""),
            subtlety_level=template.get("subtlety", 0.5),
            reinforcement_chapters=[r for r in reinforcement if r > plant_chapter],
        )

        payoff = ForeshadowingPayoff(
            chapter=payoff_chapter,
            payoff_type=presentation.get("payoff_type", "revelation"),
            payoff_method=presentation.get("payoff_method", ""),
            emotional_impact=presentation.get("impact", ""),
            connection_strength=ForeshadowingStrength.MODERATE,
            reader_awareness=1.0 - template.get("subtlety", 0.5),
        )

        foreshadowing = ForeshadowingElementDetail(
            id=foreshadowing_id,
            name=name,
            element=presentation.get("element", foreshadows),
            foreshadowing_type=technique,
            pattern_type=pattern_type,
            planting=planting,
            payoff=payoff,
            foreshadows=foreshadows,
            related_characters=related_characters or [],
            thematic_significance=presentation.get("thematic", ""),
            linked_subplot_id=linked_subplot_id,
            is_planted=False,
            is_paid_off=False,
        )

        return foreshadowing

    async def generate_complete_design(
        self,
        story_id: str,
        title: str,
        total_chapters: int,
        genre: str,
        main_characters: list[dict],
        existing_subplots: Optional[list[Subplot]] = None,
        main_story_beats: Optional[list[dict]] = None,
    ) -> SubplotForeshadowingDesign:
        """Generate a complete subplot and foreshadowing design.

        Args:
            story_id: Story ID
            title: Design title
            total_chapters: Total number of chapters
            genre: Story genre
            main_characters: List of main character dicts
            existing_subplots: Optional existing subplots
            main_story_beats: Optional main story beats

        Returns:
            Complete SubplotForeshadowingDesign
        """
        design_id = f"design_{uuid.uuid4().hex[:8]}"

        # Generate subplots
        subplots = existing_subplots or []
        if not subplots:
            subplots = await self._generate_default_subplots(
                genre=genre,
                main_characters=main_characters,
                total_chapters=total_chapters,
            )

        # Generate foreshadowing elements
        foreshadowing = await self._generate_foreshadowing_elements(
            subplots=subplots,
            total_chapters=total_chapters,
            main_characters=main_characters,
            main_story_beats=main_story_beats,
        )

        # Build system
        system = SubplotForeshadowingSystem(
            id=f"{design_id}_system",
            story_id=story_id,
            subplots=subplots,
            foreshadowing_elements=foreshadowing,
            subplot_distribution=self._calculate_distribution(subplots, total_chapters),
            foreshadowing_density=self._calculate_foreshadowing_density(foreshadowing, total_chapters),
            overall_coherence=0.8,
            payoff_ratio=0.85,
        )

        # Analyze
        subplot_analyses = await self._analyze_subplots(subplots)
        foreshadowing_analysis = await self._analyze_foreshadowing(foreshadowing, total_chapters)

        # Generate summary
        summary = self._generate_design_summary(subplots, foreshadowing)

        design = SubplotForeshadowingDesign(
            id=design_id,
            story_id=story_id,
            title=title,
            system=system,
            subplot_analyses=subplot_analyses,
            foreshadowing_analysis=foreshadowing_analysis,
            main_story_beats=[b.get("id", "") for b in (main_story_beats or [])],
            character_arcs=[c.get("id", "") for c in main_characters],
            design_summary=summary,
            key_subplots=[s.id for s in subplots if s.importance == SubplotImportance.MAJOR],
            key_foreshadowing=[f.id for f in foreshadowing if f.pattern_type == ForeshadowingPattern.EARLY_PLANT_LATE_PAYOFF],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        return design

    async def add_subplot_to_design(
        self,
        design: SubplotForeshadowingDesign,
        subplot: Subplot,
    ) -> SubplotForeshadowingDesign:
        """Add a subplot to existing design.

        Args:
            design: Existing design
            subplot: Subplot to add

        Returns:
            Updated design
        """
        design.system.subplots.append(subplot)

        # Update distribution
        design.system.subplot_distribution = self._calculate_distribution(
            design.system.subplots,
            max(ch.end_chapter for ch in design.system.subplots) if design.system.subplots else 24
        )

        # Re-analyze
        design.subplot_analyses = await self._analyze_subplots(design.system.subplots)
        design.updated_at = datetime.now().isoformat()

        return design

    async def add_foreshadowing_to_design(
        self,
        design: SubplotForeshadowingDesign,
        foreshadowing: ForeshadowingElementDetail,
    ) -> SubplotForeshadowingDesign:
        """Add foreshadowing to existing design.

        Args:
            design: Existing design
            foreshadowing: Foreshadowing to add

        Returns:
            Updated design
        """
        design.system.foreshadowing_elements.append(foreshadowing)

        # Update density
        total_chapters = max(
            ch.end_chapter for ch in design.system.subplots
        ) if design.system.subplots else 24
        design.system.foreshadowing_density = self._calculate_foreshadowing_density(
            design.system.foreshadowing_elements,
            total_chapters,
        )

        # Re-analyze
        design.foreshadowing_analysis = await self._analyze_foreshadowing(
            design.system.foreshadowing_elements,
            total_chapters,
        )
        design.updated_at = datetime.now().isoformat()

        return design

    async def plant_foreshadowing_in_chapter(
        self,
        design: SubplotForeshadowingDesign,
        foreshadowing_id: str,
        chapter: int,
    ) -> SubplotForeshadowingDesign:
        """Mark foreshadowing as planted in a specific chapter.

        Args:
            design: Design to update
            foreshadowing_id: Foreshadowing ID
            chapter: Chapter where planted

        Returns:
            Updated design
        """
        for fore in design.system.foreshadowing_elements:
            if fore.id == foreshadowing_id:
                fore.planting.chapter = chapter
                fore.is_planted = True
                break

        design.updated_at = datetime.now().isoformat()
        return design

    async def payoff_foreshadowing_in_chapter(
        self,
        design: SubplotForeshadowingDesign,
        foreshadowing_id: str,
        chapter: int,
        payoff_method: str = "",
    ) -> SubplotForeshadowingDesign:
        """Mark foreshadowing as paid off in a specific chapter.

        Args:
            design: Design to update
            foreshadowing_id: Foreshadowing ID
            chapter: Chapter of payoff
            payoff_method: How it was paid off

        Returns:
            Updated design
        """
        for fore in design.system.foreshadowing_elements:
            if fore.id == foreshadowing_id:
                fore.payoff.chapter = chapter
                fore.payoff.payoff_method = payoff_method
                fore.is_paid_off = True
                break

        # Update ratio
        total = len(design.system.foreshadowing_elements)
        paid_off = sum(1 for f in design.system.foreshadowing_elements if f.is_paid_off)
        design.system.payoff_ratio = paid_off / total if total > 0 else 0.0

        design.updated_at = datetime.now().isoformat()
        return design

    def link_foreshadowing_to_subplot(
        self,
        design: SubplotForeshadowingDesign,
        foreshadowing_id: str,
        subplot_id: str,
    ) -> SubplotForeshadowingDesign:
        """Link a foreshadowing element to a subplot.

        Args:
            design: Design to update
            foreshadowing_id: Foreshadowing ID
            subplot_id: Subplot ID

        Returns:
            Updated design
        """
        for fore in design.system.foreshadowing_elements:
            if fore.id == foreshadowing_id:
                fore.linked_subplot_id = subplot_id
                break

        for subplot in design.system.subplots:
            if subplot.id == subplot_id:
                subplot.foreshadowing_elements.append(foreshadowing_id)
                break

        design.updated_at = datetime.now().isoformat()
        return design

    async def analyze_subplot(
        self,
        subplot: Subplot,
        design: SubplotForeshadowingDesign,
    ) -> SubplotAnalysis:
        """Analyze a specific subplot.

        Args:
            subplot: Subplot to analyze
            design: Full design context

        Returns:
            SubplotAnalysis
        """
        # Calculate screen time ratio
        total_chapters = subplot.end_chapter - subplot.start_chapter + 1
        screen_time_ratio = total_chapters / 24  # Assuming 24 chapter story

        # Analyze integration
        main_beats_affected = []
        for beat in design.foreshadowing_analysis.orphaned_elements:
            if beat in [f.id for f in design.system.foreshadowing_elements]:
                for f in design.system.foreshadowing_elements:
                    if f.id == beat and f.linked_subplot_id == subplot.id:
                        main_beats_affected.append(beat)

        # Find potential conflicts
        conflicts = []
        for other in design.system.subplots:
            if other.id != subplot.id:
                # Check overlap
                if (subplot.start_chapter < other.end_chapter and
                    subplot.end_chapter > other.start_chapter):
                    # Check shared characters
                    shared = set(subplot.involved_characters) & set(other.involved_characters)
                    if shared:
                        conflicts.append(f"与{other.name}在章节重叠，且共享角色{shared}")

        analysis = SubplotAnalysis(
            subplot_id=subplot.id,
            main_story_integration={
                "connected_beats": main_beats_affected,
                "dependency_level": len(subplot.main_story_dependency) > 0,
            },
            pacing_impact={
                "subplot_tension_curve": [b.tension_level for b in subplot.arc.chapter_beats],
                "peak_at_chapter": subplot.peak_chapter,
            },
            character_development={
                "chars_involved": len(subplot.involved_characters),
                "growth_stages": len(subplot.arc.rising_action) + 1,
            },
            relationship_evolution=[
                {"stage": beat.beat_description, "changes": beat.relationship_changes}
                for beat in subplot.arc.chapter_beats if beat.relationship_changes
            ],
            screen_time_ratio=screen_time_ratio,
            reader_engagement=subplot.reader_satisfaction,
            potential_conflicts=conflicts,
            recommendations=await self._generate_subplot_recommendations(subplot),
        )

        return analysis

    async def analyze_foreshadowing_system(
        self,
        design: SubplotForeshadowingDesign,
        total_chapters: int,
    ) -> ForeshadowingAnalysis:
        """Analyze the complete foreshadowing system.

        Args:
            design: Design to analyze
            total_chapters: Total chapters in story

        Returns:
            ForeshadowingAnalysis
        """
        return await self._analyze_foreshadowing(
            design.system.foreshadowing_elements,
            total_chapters,
        )

    def get_design_summary(self, design: SubplotForeshadowingDesign) -> str:
        """Get human-readable summary of design.

        Args:
            design: Design to summarize

        Returns:
            Summary string
        """
        lines = [
            f"《{design.title}》支线与伏笔设计",
            f"",
            f"=== 支线剧情 ({len(design.system.subplots)}条) ===",
        ]

        for subplot in design.system.subplots:
            lines.append(
                f"• {subplot.name}({subplot.subplot_type.value}) "
                f"第{subplot.start_chapter}-{subplot.end_chapter}章 "
                f"重要性:{subplot.importance.value}"
            )

        lines.extend([
            "",
            f"=== 伏笔设计 ({len(design.system.foreshadowing_elements)}个) ===",
        ])

        for fore in design.system.foreshadowing_elements:
            payoff_status = "已回收" if fore.is_paid_off else f"第{fore.payoff.chapter}章待回收"
            lines.append(
                f"• {fore.name}: {fore.foreshadowing_type.value} "
                f"第{fore.planting.chapter}章种植 → {payoff_status}"
            )

        lines.extend([
            "",
            f"=== 伏笔回收率: {design.system.payoff_ratio:.0%} ===",
        ])

        return "\n".join(lines)

    def export_design(self, design: SubplotForeshadowingDesign) -> dict:
        """Export design as dictionary.

        Args:
            design: Design to export

        Returns:
            Dictionary representation
        """
        return {
            "id": design.id,
            "story_id": design.story_id,
            "title": design.title,
            "subplots": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.subplot_type.value,
                    "importance": s.importance.value,
                    "chapters": f"{s.start_chapter}-{s.end_chapter}",
                    "characters": s.involved_characters,
                    "status": s.status.value,
                }
                for s in design.system.subplots
            ],
            "foreshadowing": [
                {
                    "id": f.id,
                    "name": f.name,
                    "technique": f.foreshadowing_type.value,
                    "plant_chapter": f.planting.chapter,
                    "payoff_chapter": f.payoff.chapter,
                    "is_paid_off": f.is_paid_off,
                    "linked_subplot": f.linked_subplot_id,
                }
                for f in design.system.foreshadowing_elements
            ],
            "metrics": {
                "overall_coherence": design.system.overall_coherence,
                "payoff_ratio": design.system.payoff_ratio,
            },
            "created_at": design.created_at,
            "updated_at": design.updated_at,
        }

    # Helper methods

    async def _generate_subplot_content(
        self,
        subplot_name: str,
        subplot_type: SubplotType,
        primary_characters: list[str],
        start_chapter: int,
        end_chapter: int,
        main_story_context: Optional[str] = None,
    ) -> dict:
        """Generate AI-assisted subplot content."""
        prompt = f"""为{subplot_type.value}类型的支线剧情生成详细内容。

支线名称：{subplot_name}
涉及角色：{', '.join(primary_characters)}
活跃章节：第{start_chapter}章至第{end_chapter}章
{"主剧情背景：" + main_story_context if main_story_context else "无特定主剧情背景"}

请以JSON格式生成：
{{
  "introduction": "支线引入描述",
  "rising_action": ["关键事件1", "关键事件2"],
  "climax": "支线高潮事件",
  "falling_action": ["关键事件A", "关键事件B"],
  "resolution": "支线解决描述",
  "primary_conflict": "主要冲突",
  "thematic_connection": "与主题的关联",
  "emotional_tone": "情感基调",
  "dependency": "对主线的依赖"
}}"""

        try:
            result = await self.ai_service.generate(prompt)
            return self.ai_service._parse_json(result)
        except Exception:
            return {
                "introduction": f"{subplot_name}开始",
                "rising_action": ["事件1", "事件2"],
                "climax": f"{subplot_name}达到高潮",
                "falling_action": ["事件A"],
                "resolution": f"{subplot_name}得到解决",
                "primary_conflict": "核心冲突",
                "thematic_connection": "与成长主题相关",
                "emotional_tone": "紧张",
                "dependency": "",
            }

    async def _generate_presentation(
        self,
        technique: ForeshadowingTechnique,
        plant_chapter: int,
        foreshadows: str,
    ) -> dict:
        """Generate how foreshadowing is presented."""
        prompt = f"""为第{plant_chapter}章设计一处{subplot_foreshadowing_engine}类型的伏笔。

伏笔内容：{foreshadows}

请以JSON格式生成：
{{
  "element": "伏笔呈现的具体元素",
  "location": "出现的场景位置",
  "method": "呈现方式",
  "context": "周围上下文",
  "payoff_type": "回收类型(revelation/consequence/echo)",
  "payoff_method": "回收方式",
  "impact": "对读者的情感冲击",
  "thematic": "主题意义"
}}"""

        try:
            result = await self.ai_service.generate(prompt)
            return self.ai_service._parse_json(result)
        except Exception:
            return {
                "element": f"关于{foreshadows}的暗示",
                "location": "场景角落",
                "method": "间接描写",
                "context": "自然融入场景",
                "payoff_type": "revelation",
                "payoff_method": "揭示真相",
                "impact": "恍然大悟",
                "thematic": "命运交织",
            }

    def _generate_chapter_beats(
        self,
        start_chapter: int,
        end_chapter: int,
        template: dict,
        ai_content: dict,
    ) -> list[SubplotChapterBeat]:
        """Generate chapter beats for subplot."""
        beats = []
        tension_curve = template.get("tension_curve", [])
        tension_map = {
            0.1: "low", 0.2: "low", 0.3: "low",
            0.4: "moderate", 0.5: "moderate",
            0.6: "moderate", 0.7: "high",
            0.8: "high", 0.9: "high",
            1.0: "climax",
        }

        num_beats = end_chapter - start_chapter + 1
        for i, chapter in enumerate(range(start_chapter, end_chapter + 1)):
            tension_idx = int(i * len(tension_curve) / num_beats) if num_beats > 0 else 0
            tension_idx = min(tension_idx, len(tension_curve) - 1)
            tension_value = tension_curve[tension_idx] if tension_curve else 0.5

            beat = SubplotChapterBeat(
                chapter=chapter,
                beat_description=f"第{chapter}章情节",
                character_states={},
                relationship_changes={},
                tension_level=tension_map.get(tension_value, "moderate"),
                subplot_progress=tension_value,
            )
            beats.append(beat)

        return beats

    async def _generate_default_subplots(
        self,
        genre: str,
        main_characters: list[dict],
        total_chapters: int,
    ) -> list[Subplot]:
        """Generate default subplots based on genre and characters."""
        subplots = []
        char_ids = [c.get("id", f"char_{i}") for i, c in enumerate(main_characters[:3])]

        # Romance subplot if multiple characters
        if len(main_characters) >= 2:
            romance = await self.generate_subplot(
                subplot_name="感情线",
                subplot_type=SubplotType.ROMANTIC,
                primary_characters=char_ids[:2],
                start_chapter=3,
                end_chapter=22,
                importance=SubplotImportance.MAJOR,
            )
            subplots.append(romance)

        # Friendship subplot
        if len(main_characters) >= 2:
            friendship = await self.generate_subplot(
                subplot_name="友情线",
                subplot_type=SubplotType.FRIENDSHIP,
                primary_characters=char_ids[:2],
                start_chapter=2,
                end_chapter=20,
                importance=SubplotImportance.MODERATE,
            )
            subplots.append(friendship)

        # Mystery subplot
        mystery = await self.generate_subplot(
            subplot_name="悬疑线",
            subplot_type=SubplotType.MYSTERY,
            primary_characters=[char_ids[0]],
            start_chapter=1,
            end_chapter=total_chapters,
            importance=SubplotImportance.MAJOR,
        )
        subplots.append(mystery)

        return subplots

    async def _generate_foreshadowing_elements(
        self,
        subplots: list[Subplot],
        total_chapters: int,
        main_characters: list[dict],
        main_story_beats: Optional[list[dict]] = None,
    ) -> list[ForeshadowingElementDetail]:
        """Generate foreshadowing elements linked to subplots."""
        foreshadowing = []

        # Early plant, late payoff pattern
        early_plant = await self.generate_foreshadowing(
            name="开篇预兆",
            foreshadows="主线结局的关键要素",
            technique=ForeshadowingTechnique.SYMBOLIC,
            plant_chapter=1,
            payoff_chapter=total_chapters,
            pattern_type=ForeshadowingPattern.EARLY_PLANT_LATE_PAYOFF,
            related_characters=[c.get("id", "") for c in main_characters[:1]],
        )
        foreshadowing.append(early_plant)

        # Mid-story plant
        mid_plant = await self.generate_foreshadowing(
            name="中期暗示",
            foreshadows="剧情转折",
            technique=ForeshadowingTechnique.ATMOSPHERIC_HINT,
            plant_chapter=total_chapters // 3,
            payoff_chapter=total_chapters * 2 // 3,
            pattern_type=ForeshadowingPattern.MULTI_STAGE_REVEAL,
        )
        foreshadowing.append(mid_plant)

        # Subplot-related foreshadowing
        for subplot in subplots:
            if subplot.peak_chapter and subplot.peak_chapter > subplot.start_chapter + 2:
                subplot_fore = await self.generate_foreshadowing(
                    name=f"{subplot.name}伏笔",
                    foreshadows=f"{subplot.name}的高潮事件",
                    technique=ForeshadowingTechnique.DRAMATIC_IRONY,
                    plant_chapter=subplot.start_chapter,
                    payoff_chapter=subplot.peak_chapter,
                    linked_subplot_id=subplot.id,
                    pattern_type=ForeshadowingPattern.PARALLEL_STRUCTURE,
                )
                foreshadowing.append(subplot_fore)

        return foreshadowing

    def _calculate_distribution(
        self,
        subplots: list[Subplot],
        total_chapters: int,
    ) -> dict:
        """Calculate subplot chapter distribution."""
        distribution = {i: [] for i in range(1, total_chapters + 1)}

        for subplot in subplots:
            for chapter in range(subplot.start_chapter, subplot.end_chapter + 1):
                if chapter in distribution:
                    distribution[chapter].append(subplot.id)

        return distribution

    def _calculate_foreshadowing_density(
        self,
        foreshadowing: list[ForeshadowingElementDetail],
        total_chapters: int,
    ) -> dict:
        """Calculate foreshadowing density per chapter."""
        density = {i: 0 for i in range(1, total_chapters + 1)}

        for fore in foreshadowing:
            if fore.planting.chapter in density:
                density[fore.planting.chapter] += 1
            if fore.payoff.chapter in density:
                density[fore.payoff.chapter] += 1

        return density

    async def _analyze_subplots(
        self,
        subplots: list[Subplot],
    ) -> list[SubplotAnalysis]:
        """Analyze all subplots."""
        analyses = []

        for subplot in subplots:
            analysis = SubplotAnalysis(
                subplot_id=subplot.id,
                main_story_integration={
                    "connected_beats": [],
                    "dependency_level": len(subplot.main_story_dependency) > 0,
                },
                pacing_impact={
                    "subplot_tension_curve": [b.tension_level for b in subplot.arc.chapter_beats],
                    "peak_at_chapter": subplot.peak_chapter,
                },
                character_development={
                    "chars_involved": len(subplot.involved_characters),
                    "growth_stages": len(subplot.arc.rising_action) + 1,
                },
                relationship_evolution=[],
                screen_time_ratio=(subplot.end_chapter - subplot.start_chapter + 1) / 24,
                reader_engagement=subplot.reader_satisfaction,
                potential_conflicts=[],
                recommendations=[],
            )
            analyses.append(analysis)

        return analyses

    async def _analyze_foreshadowing(
        self,
        foreshadowing: list[ForeshadowingElementDetail],
        total_chapters: int,
    ) -> ForeshadowingAnalysis:
        """Analyze foreshadowing system."""
        # Coverage by chapter
        coverage = {i: 0 for i in range(1, total_chapters + 1)}
        for fore in foreshadowing:
            if 1 <= fore.planting.chapter <= total_chapters:
                coverage[fore.planting.chapter] += 1

        # Find gaps
        gaps = [ch for ch, count in coverage.items() if count == 0]

        # Pattern distribution
        patterns = {}
        for fore in foreshadowing:
            if fore.pattern_type:
                pattern_name = fore.pattern_type.value
                patterns[pattern_name] = patterns.get(pattern_name, 0) + 1

        # Orphaned elements
        orphaned = [f.id for f in foreshadowing if not f.linked_subplot_id and not f.is_paid_off]

        analysis = ForeshadowingAnalysis(
            coverage_by_chapter=coverage,
            coverage_gaps=gaps,
            pattern_distribution=patterns,
            effectiveness_scores={},
            payoff_timing={},
            delayed_payoffs=[],
            rushed_payoffs=[],
            subplot_connections={},
            orphaned_elements=orphaned,
            overall_balance=self._calculate_balance(foreshadowing, total_chapters),
            reader_experience={},
        )

        return analysis

    def _calculate_balance(
        self,
        foreshadowing: list[ForeshadowingElementDetail],
        total_chapters: int,
    ) -> float:
        """Calculate foreshadowing balance score."""
        if not foreshadowing:
            return 0.0

        # Check if foreshadowing is distributed evenly
        planting_chapters = [f.planting.chapter for f in foreshadowing]
        if not planting_chapters:
            return 0.0

        # Ideal: plant roughly 1 per 3-4 chapters
        ideal_density = total_chapters / 4
        actual_count = len(foreshadowing)

        ratio = min(actual_count, ideal_density) / max(actual_count, ideal_density)
        return ratio

    def _generate_design_summary(
        self,
        subplots: list[Subplot],
        foreshadowing: list[ForeshadowingElementDetail],
    ) -> str:
        """Generate design summary."""
        major_subplots = [s for s in subplots if s.importance == SubplotImportance.MAJOR]
        paid_off = sum(1 for f in foreshadowing if f.is_paid_off)

        return (
            f"设计包含{len(subplots)}条支线（其中{len(major_subplots)}条重要支线）"
            f"和{len(foreshadowing)}个伏笔元素（已回收{paid_off}个）。"
        )

    def _estimate_word_count(
        self,
        start_chapter: int,
        end_chapter: int,
        importance: SubplotImportance,
    ) -> int:
        """Estimate word count for subplot."""
        chapter_count = end_chapter - start_chapter + 1
        base_words_per_chapter = {
            SubplotImportance.MINOR: 500,
            SubplotImportance.MODERATE: 800,
            SubplotImportance.MAJOR: 1200,
            SubplotImportance.CRITICAL: 1500,
        }
        return chapter_count * base_words_per_chapter.get(importance, 800)

    async def _generate_subplot_recommendations(
        self,
        subplot: Subplot,
    ) -> list[str]:
        """Generate improvement recommendations for subplot."""
        recommendations = []

        if subplot.coherence_score < 0.7:
            recommendations.append("建议加强支线内部逻辑连贯性")

        if len(subplot.involved_characters) < 2:
            recommendations.append("建议增加支线涉及的角色数量以提高互动性")

        if subplot.peak_chapter and subplot.peak_chapter - subplot.start_chapter < 3:
            recommendations.append("建议拉长支线上升期以增加张力")

        if not subplot.foreshadowing_elements:
            recommendations.append("建议为支线添加伏笔元素以增加深度")

        return recommendations
