"""Story outline engine for comprehensive story planning."""

from datetime import datetime
from typing import Optional
import uuid

from chai.models.story_outline import (
    StoryOutline,
    StoryOutlineType,
    OutlineStatus,
    VolumeOutline,
    ChapterOutline,
    SceneOutline,
    PlotThread,
    ForeshadowingElement,
    ForeshadowingType,
    ForeshadowingStatus,
    PlotThreadType,
    TensionLevel,
    ScenePurpose,
    StoryOutlineAnalysis,
)
from chai.models.character_growth_arc import CharacterGrowthArcSystem
from chai.models.character_relationship_network import CharacterRelationshipNetwork
from chai.services import AIService


# Template for Three-Act structure chapters
THREE_ACT_CHAPTERS = [
    # Act 1 - Setup (Chapters 1-6)
    {"act": 1, "name": "建置-引入", "tension": TensionLevel.LOW, "purpose": ScenePurpose.exposition},
    {"act": 1, "name": "建置-世界", "tension": TensionLevel.LOW, "purpose": ScenePurpose.WORLD_BUILDING},
    {"act": 1, "name": "建置-冲突", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.exposition},
    {"act": 1, "name": "催化事件", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    {"act": 1, "name": "反应", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.CHARACTER_DEVELOPMENT},
    {"act": 1, "name": "跨越门槛", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    # Act 2 - Confrontation (Chapters 7-18)
    {"act": 2, "name": "新世界", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.WORLD_BUILDING},
    {"act": 2, "name": "试炼开始", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    {"act": 2, "name": "盟友与敌人", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.RELATIONSHIP},
    {"act": 2, "name": "深层考验", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    {"act": 2, "name": "中点转折", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.COMPLICATION},
    {"act": 2, "name": "虚假胜利", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.rising_action},
    {"act": 2, "name": "全面压迫", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    {"act": 2, "name": "同伴危机", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.CHARACTER_DEVELOPMENT},
    {"act": 2, "name": "内部冲突", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.COMPLICATION},
    {"act": 2, "name": "最低点", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.COMPLICATION},
    {"act": 2, "name": "重新发现", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.CHARACTER_DEVELOPMENT},
    # Act 3 - Resolution (Chapters 19-24)
    {"act": 3, "name": "最终计划", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.rising_action},
    {"act": 3, "name": "高潮准备", "tension": TensionLevel.HIGH, "purpose": ScenePurpose.rising_action},
    {"act": 3, "name": "高潮对决", "tension": TensionLevel.CLIMAX, "purpose": ScenePurpose.CLIMAX},
    {"act": 3, "name": "余波", "tension": TensionLevel.MODERATE, "purpose": ScenePurpose.RESOLUTION},
    {"act": 3, "name": "收尾", "tension": TensionLevel.LOW, "purpose": ScenePurpose.RESOLUTION},
    {"act": 3, "name": "尾声", "tension": TensionLevel.RELEASE, "purpose": ScenePurpose.RESOLUTION},
]


class StoryOutlineEngine:
    """Engine for generating comprehensive story outlines."""

    def __init__(self, ai_service: AIService):
        """Initialize story outline engine with AI service."""
        self.ai_service = ai_service

    async def generate_outline(
        self,
        genre: str,
        theme: str,
        main_characters: list[dict],
        supporting_characters: Optional[list[dict]] = None,
        antagonists: Optional[list[dict]] = None,
        outline_type: StoryOutlineType = StoryOutlineType.THREE_ACT,
        target_chapters: int = 24,
        target_word_count: int = 80000,
        world_setting: Optional[dict] = None,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
        relationship_network: Optional[CharacterRelationshipNetwork] = None,
    ) -> StoryOutline:
        """Generate a comprehensive story outline.

        Args:
            genre: Novel genre
            theme: Central theme
            main_characters: List of main character dicts
            supporting_characters: List of supporting character dicts
            antagonists: List of antagonist dicts
            outline_type: Story structure type
            target_chapters: Target number of chapters
            target_word_count: Target word count
            world_setting: Optional world setting dict
            growth_arcs: Optional character growth arc system
            relationship_network: Optional character relationship network

        Returns:
            Complete StoryOutline object
        """
        outline_id = f"outline_{uuid.uuid4().hex[:8]}"

        # Generate AI-assisted outline data
        ai_outline_data = await self._generate_outline_with_ai(
            genre=genre,
            theme=theme,
            main_characters=main_characters,
            supporting_characters=supporting_characters or [],
            antagonists=antagonists or [],
            outline_type=outline_type,
            world_setting=world_setting,
        )

        # Create plot threads
        plot_threads = await self._create_plot_threads(
            genre=genre,
            theme=theme,
            main_characters=main_characters,
            ai_data=ai_outline_data,
        )

        # Create foreshadowing elements
        foreshadowing = await self._create_foreshadowing(
            ai_data=ai_outline_data,
            target_chapters=target_chapters,
        )

        # Generate chapter outlines
        chapters = await self._generate_chapters(
            outline_id=outline_id,
            genre=genre,
            theme=theme,
            ai_data=ai_outline_data,
            main_characters=main_characters,
            supporting_characters=supporting_characters or [],
            antagonists=antagonists or [],
            plot_threads=plot_threads,
            foreshadowing=foreshadowing,
            target_chapters=target_chapters,
            growth_arcs=growth_arcs,
        )

        # Generate volume outlines
        volumes = self._generate_volumes(
            outline_id=outline_id,
            chapters=chapters,
            target_chapters=target_chapters,
        )

        # Create scene outlines for each chapter
        scenes = await self._generate_scenes(
            chapters=chapters,
            plot_threads=plot_threads,
            foreshadowing=foreshadowing,
        )

        # Build main outline
        outline = StoryOutline(
            id=outline_id,
            title=ai_outline_data.get("title", f"{theme}：故事大纲"),
            genre=genre,
            theme=theme,
            outline_type=outline_type,
            target_word_count=target_word_count,
            target_chapter_count=target_chapters,
            volumes=volumes,
            chapters=chapters,
            scenes=scenes,
            plot_threads=plot_threads,
            foreshadowing_elements=foreshadowing,
            main_character_ids=[c.get("id", f"char_{i}") for i, c in enumerate(main_characters)],
            supporting_character_ids=[
                c.get("id", f"supporting_{i}")
                for i, c in enumerate(supporting_characters or [])
            ],
            antagonist_ids=[
                c.get("id", f"antagonist_{i}") for i, c in enumerate(antagonists or [])
            ],
            world_setting_id=world_setting.get("id") if world_setting else None,
            status=OutlineStatus.COMPLETE,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        return outline

    async def _generate_outline_with_ai(
        self,
        genre: str,
        theme: str,
        main_characters: list[dict],
        supporting_characters: list[dict],
        antagonists: list[dict],
        outline_type: StoryOutlineType,
        world_setting: Optional[dict] = None,
    ) -> dict:
        """Generate outline data using AI."""
        world_info = f"世界观设定：{world_setting.get('name', '待构建')}" if world_setting else "世界观待构建"

        main_char_names = [c.get("name", f"主角{i}") for i, c in enumerate(main_characters)]
        supporting_names = [c.get("name", f"配角{i}") for i, c in enumerate(supporting_characters)]
        antagonist_names = [c.get("name", f"反派{i}") for i, c in enumerate(antagonists)]

        prompt = f"""为{genre}类型小说生成详细的故事大纲。

主题：{theme}
{world_info}

主要角色：
{chr(10).join(f"- {name}" for name in main_char_names)}

配角：
{chr(10).join(f"- {name}" for name in supporting_names)}

反派：
{chr(10).join(f"- {name}" for name in antagonist_names)}

请以JSON格式生成完整大纲，包含：
{{
  "title": "故事标题",
  "logline": "一句话概括故事",
  "synopsis": "200字故事梗概",
  "main_conflict": "核心冲突描述",
  "thematic_statements": ["主题陈述列表"],
  "plot_threads": [
    {{
      "name": "线索名称",
      "type": "main/romantic/subplot/mystery",
      "description": "线索描述",
      "key_events": ["关键事件列表"]
    }}
  ],
  "foreshadowing_plan": [
    {{
      "element": "伏笔元素",
      "type": "direct/indirect/character_based/symbolic",
      "plant_chapter": 种植章节号,
      "payoff_chapter": 回收章节号,
      "description": "如何呈现"
    }}
  ],
  "chapter_summaries": [
    {{
      "chapter": 章节号,
      "title": "章节标题",
      "summary": "章节概要（100字）",
      "key_events": ["关键事件"],
      "characters": ["主要出场角色"],
      "tension_level": "low/moderate/high/climax"
    }}
  ],
  "volume_splits": [
    {{"volume": 1, "start_chapter": 1, "end_chapter": 8, "theme": "第一卷主题"}},
    {{"volume": 2, "start_chapter": 9, "end_chapter": 16, "theme": "第二卷主题"}},
    {{"volume": 3, "start_chapter": 17, "end_chapter": 24, "theme": "第三卷主题"}}
  ],
  "character_arc_milestones": {{
    "角色名": ["关键转折点列表"]
  }}
}}"""
        result = await self.ai_service.generate(prompt)
        return self.ai_service._parse_json(result)

    async def _create_plot_threads(
        self,
        genre: str,
        theme: str,
        main_characters: list[dict],
        ai_data: dict,
    ) -> list[PlotThread]:
        """Create plot threads from AI data."""
        threads = []
        thread_id_counter = 0

        # Main plot thread
        threads.append(PlotThread(
            id=f"thread_{thread_id_counter}",
            name="主线剧情",
            thread_type=PlotThreadType.MAIN,
            description=ai_data.get("main_conflict", f"{theme}的核心冲突"),
            chapters_active=list(range(1, 25)),
            status=OutlineStatus.PENDING,
            current_state="初始状态",
            key_events=ai_data.get("plot_threads", [{}])[0].get("key_events", []) if ai_data.get("plot_threads") else [],
        ))
        thread_id_counter += 1

        # Add romantic thread if characters exist
        if len(main_characters) >= 2:
            threads.append(PlotThread(
                id=f"thread_{thread_id_counter}",
                name="感情线",
                thread_type=PlotThreadType.ROMANTIC,
                description="角色之间的感情发展",
                chapters_active=list(range(3, 22)),
                status=OutlineStatus.PENDING,
                current_state="初始吸引",
                key_events=[],
            ))
            thread_id_counter += 1

        # Add subplot threads from AI data
        for thread_data in ai_data.get("plot_threads", []):
            if thread_data.get("type") in ["subplot", "mystery"]:
                threads.append(PlotThread(
                    id=f"thread_{thread_id_counter}",
                    name=thread_data.get("name", "支线"),
                    thread_type=PlotThreadType(thread_data.get("type", "subplot")),
                    description=thread_data.get("description", ""),
                    chapters_active=list(range(
                        thread_data.get("start_chapter", 5),
                        thread_data.get("end_chapter", 20)
                    )),
                    status=OutlineStatus.PENDING,
                    current_state="",
                    key_events=thread_data.get("key_events", []),
                ))
                thread_id_counter += 1

        return threads

    async def _create_foreshadowing(
        self,
        ai_data: dict,
        target_chapters: int,
    ) -> list[ForeshadowingElement]:
        """Create foreshadowing elements from AI data."""
        elements = []
        element_id_counter = 0

        for foreshadow_data in ai_data.get("foreshadowing_plan", []):
            elements.append(ForeshadowingElement(
                id=f"fore_{element_id_counter}",
                element=foreshadow_data.get("element", ""),
                foreshadowing_type=ForeshadowingType(
                    foreshadow_data.get("type", "indirect")
                ),
                chapter_planted=foreshadow_data.get("plant_chapter", 1),
                description=foreshadow_data.get("description", ""),
                chapter_payoff=foreshadow_data.get("payoff_chapter"),
                payoff_description="",
                status=ForeshadowingStatus.PLANTED,
                subtlety_level=0.6,
            ))
            element_id_counter += 1

        # Add some default foreshadowing if AI didn't provide enough
        if len(elements) < 5:
            elements.extend([
                ForeshadowingElement(
                    id=f"fore_{element_id_counter}",
                    element="神秘符号",
                    foreshadowing_type=ForeshadowingType.SYMBOLIC,
                    chapter_planted=3,
                    description="在场景角落出现的符号",
                    chapter_payoff=18,
                    status=ForeshadowingStatus.PLANTED,
                    subtlety_level=0.8,
                ),
                ForeshadowingElement(
                    id=f"fore_{element_id_counter + 1}",
                    element="角色遗言",
                    foreshadowing_type=ForeshadowingType.DIALOGUE,
                    chapter_planted=5,
                    description="看似随意的一句台词",
                    chapter_payoff=20,
                    status=ForeshadowingStatus.PLANTED,
                    subtlety_level=0.7,
                ),
            ])

        return elements

    async def _generate_chapters(
        self,
        outline_id: str,
        genre: str,
        theme: str,
        ai_data: dict,
        main_characters: list[dict],
        supporting_characters: list[dict],
        antagonists: list[dict],
        plot_threads: list[PlotThread],
        foreshadowing: list[ForeshadowingElement],
        target_chapters: int,
        growth_arcs: Optional[CharacterGrowthArcSystem] = None,
    ) -> list[ChapterOutline]:
        """Generate chapter outlines."""
        chapters = []
        chapter_summaries = ai_data.get("chapter_summaries", [])

        # Use template if AI summaries not available
        if not chapter_summaries:
            template = THREE_ACT_CHAPTERS[:target_chapters]
            for i, chapter_template in enumerate(template):
                chapters.append(ChapterOutline(
                    id=f"{outline_id}_ch_{i + 1}",
                    number=i + 1,
                    title=f"第{i + 1}章",
                    summary=f"{chapter_template['name']}的详细故事",
                    pov_character=main_characters[0].get("name") if main_characters else None,
                    characters_involved=[
                        c.get("name", "") for c in main_characters[:3]
                    ],
                    tension_level=chapter_template["tension"],
                    pacing_notes=f"{chapter_template['purpose'].value}为主",
                    scene_count=3,
                    status=OutlineStatus.PENDING,
                    target_word_count=target_chapters * 3000 // target_chapters,
                ))
        else:
            for summary_data in chapter_summaries:
                chapter_num = summary_data.get("chapter", 1)
                chapter_id = f"{outline_id}_ch_{chapter_num}"

                # Find foreshadowing for this chapter
                planted = [f.id for f in foreshadowing if f.chapter_planted == chapter_num]
                payoffs = [f.id for f in foreshadowing if f.chapter_payoff == chapter_num]

                # Find threads active in this chapter
                active_threads = [
                    t.id for t in plot_threads
                    if chapter_num in t.chapters_active
                ]

                chapters.append(ChapterOutline(
                    id=chapter_id,
                    number=chapter_num,
                    title=summary_data.get("title", f"第{chapter_num}章"),
                    summary=summary_data.get("summary", ""),
                    pov_character=summary_data.get("pov", main_characters[0].get("name") if main_characters else None),
                    characters_involved=summary_data.get("characters", []),
                    tension_level=TensionLevel(summary_data.get("tension_level", "moderate")),
                    pacing_notes="; ".join(summary_data.get("key_events", [])),
                    plot_threads_advanced=active_threads[:3],
                    foreshadowing_planted=planted,
                    foreshadowing_payoffs=payoffs,
                    status=OutlineStatus.PENDING,
                    target_word_count=3000,
                ))

        return chapters

    def _generate_volumes(
        self,
        outline_id: str,
        chapters: list[ChapterOutline],
        target_chapters: int,
    ) -> list[VolumeOutline]:
        """Generate volume outlines by grouping chapters."""
        volumes = []
        chapters_per_volume = target_chapters // 3

        for vol_num in range(3):
            vol_start = vol_num * chapters_per_volume + 1
            vol_end = min((vol_num + 1) * chapters_per_volume, target_chapters)

            volume_chapters = [
                c for c in chapters
                if vol_start <= c.number <= vol_end
            ]

            # Collect key events from chapters
            key_events = []
            for ch in volume_chapters:
                if ch.pacing_notes:
                    key_events.append(ch.pacing_notes)

            volumes.append(VolumeOutline(
                id=f"{outline_id}_vol_{vol_num + 1}",
                number=vol_num + 1,
                title=f"第{vol_num + 1}卷",
                chapter_start=vol_start,
                chapter_end=vol_end,
                description=f"第{vol_num + 1}卷故事概要",
                theme=f"第{vol_num + 1}卷主题",
                central_conflict="本卷核心冲突",
                arc_summary="本卷角色弧线概要",
                key_events=key_events[:5],
                status=OutlineStatus.PENDING,
            ))

        return volumes

    async def _generate_scenes(
        self,
        chapters: list[ChapterOutline],
        plot_threads: list[PlotThread],
        foreshadowing: list[ForeshadowingElement],
    ) -> list[SceneOutline]:
        """Generate scene outlines for each chapter."""
        scenes = []
        scene_id_counter = 0

        for chapter in chapters:
            for scene_num in range(chapter.scene_count):
                scene_id = f"scene_{scene_id_counter}"
                scene_id_counter += 1

                # Find foreshadowing for this scene
                scene_fore = [
                    f.id for f in foreshadowing
                    if f.chapter_planted == chapter.number and scene_num == 0
                ]

                scenes.append(SceneOutline(
                    id=scene_id,
                    number=scene_num + 1,
                    chapter_id=chapter.id,
                    location="场景地点",
                    time_period="白天/夜晚",
                    setting_description="环境描写",
                    characters=chapter.characters_involved[:3],
                    pov_character=chapter.pov_character,
                    scene_purpose=ScenePurpose.rising_action,
                    purpose_description=f"场景目的：推进情节",
                    scene_summary="场景事件概要",
                    key_dialogues=["关键对话1", "关键对话2"],
                    character_actions=["角色动作1", "角色动作2"],
                    mood="中性",
                    emotional_beat="平静",
                    plot_threads_advanced=chapter.plot_threads_advanced[:1],
                    foreshadowing_planted=scene_fore,
                    tension_level=chapter.tension_level,
                    duration_words=1000,
                ))

        return scenes

    async def expand_chapter_outline(
        self,
        chapter_outline: ChapterOutline,
        genre: str,
        theme: str,
        character_details: Optional[list[dict]] = None,
    ) -> ChapterOutline:
        """Expand a chapter outline with more detail.

        Args:
            chapter_outline: Existing chapter outline to expand
            genre: Novel genre
            theme: Central theme
            character_details: Optional character details for dialogue generation

        Returns:
            Expanded chapter outline
        """
        expanded = chapter_outline.model_copy()

        # Expand summary
        expanded.summary = (
            f"第{chapter_outline.number}章详细展开："
            f"{chapter_outline.summary}"
        )

        # Expand scene summaries if empty
        if not expanded.scene_summaries:
            scene_labels = ["开场", "发展", "转折", "高潮", "收尾"]
            expanded.scene_summaries = [
                f"场景{i + 1}：{scene_labels[i % len(scene_labels)]}"
                for i in range(chapter_outline.scene_count)
            ]

        # Expand chapter goals
        if not expanded.chapter_goals:
            expanded.chapter_goals = [
                "建立当前场景",
                "推进主要冲突",
                "为下一章埋下伏笔",
            ]

        expanded.status = OutlineStatus.IN_PROGRESS

        return expanded

    async def analyze_outline(
        self,
        outline: StoryOutline,
    ) -> StoryOutlineAnalysis:
        """Analyze a story outline for quality and consistency.

        Args:
            outline: Story outline to analyze

        Returns:
            StoryOutlineAnalysis with findings
        """
        analysis = StoryOutlineAnalysis(outline_id=outline.id)

        # Analyze pacing
        tension_curve = []
        for ch in outline.chapters:
            tension_curve.append({
                "chapter": ch.number,
                "tension": ch.tension_level.value,
            })

        # Check tension progression
        tension_sequence = [TensionLevel(t["tension"]) for t in tension_curve]
        analysis.tacing_analysis = {
            "has_climax": TensionLevel.CLIMAX in tension_sequence,
            "tension_variance": len(set(tension_sequence)),
            "progression_smooth": self._check_tension_progression(tension_sequence),
        }

        # Analyze plot threads
        analysis.thread_coverage = {
            "total_threads": len(outline.plot_threads),
            "active_chapters": {
                t.id: len(t.chapters_active) for t in outline.plot_threads
            },
        }

        # Find unresolved threads
        analysis.unresolved_threads = [
            t.id for t in outline.plot_threads
            if t.status != OutlineStatus.COMPLETE
        ]

        # Analyze foreshadowing
        planted = [f for f in outline.foreshadowing_elements if f.status == ForeshadowingStatus.PLANTED]
        payed_off = [f for f in outline.foreshadowing_elements if f.status == ForeshadowingStatus.PAYED_OFF]

        analysis.foreshadowing_balance = {
            "total_planted": len(planted),
            "total_paid_off": len(payed_off),
            "ratio": len(payed_off) / len(planted) if planted else 0,
        }

        # Find orphaned foreshadowing (planted but no payoff)
        analysis.orphaned_foreshadowing = [
            f.id for f in planted if f.chapter_payoff is None
        ]

        # Character screen time
        char_appearances = {}
        for ch in outline.chapters:
            for char_id in ch.characters_involved:
                char_appearances[char_id] = char_appearances.get(char_id, 0) + 1
        analysis.character_screen_time = char_appearances

        # Calculate protagonist dominance
        if outline.main_character_ids and char_appearances:
            main_total = sum(
                char_appearances.get(cid, 0)
                for cid in outline.main_character_ids
            )
            total_appearances = sum(char_appearances.values())
            analysis.protagonist_dominance = (
                main_total / total_appearances if total_appearances else 0.5
            )

        # Calculate quality scores
        analysis.coherence_score = self._calculate_coherence(outline, analysis)
        analysis.completeness_score = self._calculate_completeness(outline)

        return analysis

    def _check_tension_progression(self, tensions: list[TensionLevel]) -> bool:
        """Check if tension progression is logical."""
        if not tensions:
            return True

        # Climax should be near the end
        climax_indices = [
            i for i, t in enumerate(tensions) if t == TensionLevel.CLIMAX
        ]
        if climax_indices and climax_indices[-1] < len(tensions) * 0.7:
            return False

        # Should have some tension variation
        if len(set(tensions)) < 3:
            return False

        return True

    def _calculate_coherence(
        self,
        outline: StoryOutline,
        analysis: StoryOutlineAnalysis,
    ) -> float:
        """Calculate coherence score."""
        score = 1.0

        # Penalize for unresolved threads
        if analysis.unresolved_threads:
            score -= 0.1 * len(analysis.unresolved_threads)

        # Penalize for orphaned foreshadowing
        if analysis.orphaned_foreshadowing:
            score -= 0.1 * len(analysis.orphaned_foreshadowing)

        # Penalize for timeline issues
        if analysis.timeline_consistency:
            score -= 0.1 * len(analysis.timeline_consistency)

        return max(0.0, min(1.0, score))

    def _calculate_completeness(self, outline: StoryOutline) -> float:
        """Calculate completeness score."""
        score = 0.0
        max_score = 5.0

        # Has title
        if outline.title:
            score += 0.5

        # Has chapters
        if len(outline.chapters) >= outline.target_chapter_count * 0.8:
            score += 1.0

        # Has plot threads
        if len(outline.plot_threads) >= 2:
            score += 1.0

        # Has foreshadowing
        if len(outline.foreshadowing_elements) >= 3:
            score += 1.0

        # Has volumes
        if len(outline.volumes) >= 1:
            score += 0.5

        # Scenes generated
        if len(outline.scenes) >= len(outline.chapters) * 2:
            score += 1.0

        return score / max_score

    def add_subplot(
        self,
        outline: StoryOutline,
        subplot_name: str,
        subplot_type: PlotThreadType,
        involved_characters: list[str],
        start_chapter: int,
        end_chapter: int,
        key_events: list[str],
    ) -> StoryOutline:
        """Add a new subplot to the outline.

        Args:
            outline: Existing story outline
            subplot_name: Name of the subplot
            subplot_type: Type of subplot
            involved_characters: Character IDs involved
            start_chapter: Starting chapter
            end_chapter: Ending chapter
            key_events: Key events in this subplot

        Returns:
            Updated outline with new subplot
        """
        new_thread = PlotThread(
            id=f"thread_{len(outline.plot_threads)}",
            name=subplot_name,
            thread_type=subplot_type,
            description=f"{subplot_name}的详细描述",
            chapters_active=list(range(start_chapter, end_chapter + 1)),
            status=OutlineStatus.PENDING,
            current_state="",
            key_events=key_events,
        )

        outline.plot_threads.append(new_thread)

        # Update chapter outlines to include this thread
        for chapter in outline.chapters:
            if chapter.number in new_thread.chapters_active:
                chapter.plot_threads_advanced.append(new_thread.id)

        return outline

    def plant_foreshadowing(
        self,
        outline: StoryOutline,
        element: str,
        foreshadowing_type: ForeshadowingType,
        plant_chapter: int,
        plant_location: str,
        payoff_chapter: Optional[int] = None,
        payoff_description: str = "",
        subtlety_level: float = 0.5,
    ) -> StoryOutline:
        """Add foreshadowing to the outline.

        Args:
            outline: Existing story outline
            element: The foreshadowing element
            foreshadowing_type: Type of foreshadowing
            plant_chapter: Chapter to plant the foreshadowing
            plant_location: Where in the chapter
            payoff_chapter: Optional chapter for payoff
            payoff_description: How the payoff occurs
            subtlety_level: How subtle (0-1)

        Returns:
            Updated outline with new foreshadowing
        """
        new_foreshadowing = ForeshadowingElement(
            id=f"fore_{len(outline.foreshadowing_elements)}",
            element=element,
            foreshadowing_type=foreshadowing_type,
            chapter_planted=plant_chapter,
            scene_location=plant_location,
            description=f"如何呈现：{element}",
            chapter_payoff=payoff_chapter,
            payoff_description=payoff_description,
            status=ForeshadowingStatus.PLANTED if not payoff_chapter else ForeshadowingStatus.DEVELOPING,
            subtlety_level=subtlety_level,
        )

        outline.foreshadowing_elements.append(new_foreshadowing)

        # Update chapter outline
        for chapter in outline.chapters:
            if chapter.number == plant_chapter:
                chapter.foreshadowing_planted.append(new_foreshadowing.id)
            if payoff_chapter and chapter.number == payoff_chapter:
                chapter.foreshadowing_payoffs.append(new_foreshadowing.id)

        return outline

    def get_outline_summary(self, outline: StoryOutline) -> str:
        """Get a human-readable summary of the story outline.

        Args:
            outline: Story outline

        Returns:
            Summary string
        """
        lines = [
            f"《{outline.title}》",
            f"类型：{outline.genre}",
            f"主题：{outline.theme}",
            f"",
            f"结构：{outline.outline_type.value}",
            f"目标字数：{outline.target_word_count}字",
            f"目标章节：{outline.target_chapter_count}章",
            f"",
            f"=== 卷数概述 ===",
        ]

        for vol in outline.volumes:
            lines.append(
                f"第{vol.number}卷《{vol.title}》"
                f"(第{vol.chapter_start}-{vol.chapter_end}章)：{vol.description}"
            )

        lines.extend([
            "",
            "=== 章节概览 ===",
        ])

        for ch in outline.chapters[:6]:  # First 6 chapters
            lines.append(
                f"第{ch.number}章 {ch.title}：{ch.summary[:50]}..."
            )

        if len(outline.chapters) > 6:
            lines.append(f"... 共{len(outline.chapters)}章")

        lines.extend([
            "",
            "=== 线索概览 ===",
        ])

        for thread in outline.plot_threads:
            lines.append(
                f"{thread.name}：{thread.description[:50]}..."
                f"(活跃章节: {len(thread.chapters_active)})"
            )

        lines.extend([
            "",
            "=== 伏笔概览 ===",
            f"共{len(outline.foreshadowing_elements)}个伏笔元素",
            f"已回收: {sum(1 for f in outline.foreshadowing_elements if f.status == ForeshadowingStatus.PAYED_OFF)}",
            f"待回收: {sum(1 for f in outline.foreshadowing_elements if f.status == ForeshadowingStatus.PLANTED)}",
        ])

        return "\n".join(lines)

    def export_outline(self, outline: StoryOutline) -> dict:
        """Export story outline as a dictionary.

        Args:
            outline: Story outline to export

        Returns:
            Dictionary representation
        """
        return {
            "id": outline.id,
            "title": outline.title,
            "genre": outline.genre,
            "theme": outline.theme,
            "outline_type": outline.outline_type.value,
            "target_word_count": outline.target_word_count,
            "target_chapter_count": outline.target_chapter_count,
            "volumes": [
                {
                    "id": v.id,
                    "number": v.number,
                    "title": v.title,
                    "chapter_range": f"{v.chapter_start}-{v.chapter_end}",
                    "description": v.description,
                    "theme": v.theme,
                }
                for v in outline.volumes
            ],
            "chapters": [
                {
                    "id": c.id,
                    "number": c.number,
                    "title": c.title,
                    "summary": c.summary,
                    "tension_level": c.tension_level.value,
                    "characters": c.characters_involved,
                }
                for c in outline.chapters
            ],
            "plot_threads": [
                {
                    "id": t.id,
                    "name": t.name,
                    "type": t.thread_type.value,
                    "chapters_active": t.chapters_active,
                }
                for t in outline.plot_threads
            ],
            "foreshadowing": [
                {
                    "id": f.id,
                    "element": f.element,
                    "type": f.foreshadowing_type.value,
                    "plant_chapter": f.chapter_planted,
                    "payoff_chapter": f.chapter_payoff,
                    "status": f.status.value,
                }
                for f in outline.foreshadowing_elements
            ],
            "status": outline.status.value,
            "created_at": outline.created_at,
        }
