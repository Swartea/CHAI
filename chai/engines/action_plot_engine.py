"""Action and plot advancement engine for dynamic scene writing."""

from typing import Optional
from chai.models import Character
from chai.models.action_plot import (
    ActionPlotPlan, ActionPlotDraft, ActionPlotRevision, ActionPlotAnalysis,
    ActionPlotTemplate, ActionSequence, ActionBeat, PlotArcAdvancement,
    PlotAdvancementBeat, ActionType, ActionIntensity, ActionPhase,
    PlotAdvancementType, PlotBeatType, PacingType,
)
from chai.services import AIService


class ActionPlotEngine:
    """Engine for generating action sequences and plot advancement."""

    # Pre-built templates for common action-plot situations
    TEMPLATES: dict[str, ActionPlotTemplate] = {
        "combat_clash": ActionPlotTemplate(
            id="combat_clash",
            name="战斗冲突",
            applicable_action_types=[ActionType.COMBAT, ActionType.CONFRONTATION],
            applicable_plot_types=[PlotAdvancementType.MAIN_PLOT, PlotAdvancementType.TURNING_POINT],
            typical_beat_count=7,
            typical_action_ratio=0.8,
            pacing_pattern=PacingType.CRESCENDO,
            intensity_curve=[
                ActionIntensity.LOW, ActionIntensity.MODERATE, ActionIntensity.HIGH,
                ActionIntensity.EXTREME, ActionIntensity.CLIMACTIC,
                ActionIntensity.HIGH, ActionIntensity.MODERATE
            ],
            starting_tension=0.4,
            peak_tension=0.95,
            ending_tension=0.5,
            opening_pattern="Setup combat situation, establish stakes",
            development_pattern="Escalating exchanges, tactical maneuvers",
            climax_pattern="Final clash, decisive blow",
            closing_pattern="Aftermath, consequences revealed",
            action_detail_level="detailed",
            dialogue_in_action=False,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "对峙",
                "拔剑/准备",
                "第一波攻击"
            ],
            typical_climax_beats=[
                "致命一击",
                "关键时刻",
                "逆转"
            ],
            typical_closing_beats=[
                "胜利/失败",
                "伤势",
                "战后余波"
            ]
        ),
        "chase_escape": ActionPlotTemplate(
            id="chase_escape",
            name="追逐逃亡",
            applicable_action_types=[ActionType.CHASE, ActionType.ESCAPE],
            applicable_plot_types=[PlotAdvancementType.MAIN_PLOT, PlotAdvancementType.BREAKTHROUGH],
            typical_beat_count=6,
            typical_action_ratio=0.9,
            pacing_pattern=PacingType.FAST,
            intensity_curve=[
                ActionIntensity.MODERATE, ActionIntensity.HIGH, ActionIntensity.EXTREME,
                ActionIntensity.HIGH, ActionIntensity.MODERATE, ActionIntensity.LOW
            ],
            starting_tension=0.5,
            peak_tension=0.9,
            ending_tension=0.3,
            opening_pattern="Chase begins, pursuer revealed",
            development_pattern="Close calls, obstacles overcome",
            climax_pattern="Final sprint, decisive moment",
            closing_pattern="Escape achieved or captured",
            action_detail_level="moderate",
            dialogue_in_action=False,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "发现追兵",
                "拼命逃跑"
            ],
            typical_climax_beats=[
                "绝境",
                "最后挣扎"
            ],
            typical_closing_beats=[
                "甩开追兵",
                "暂时安全"
            ]
        ),
        "revelation_climax": ActionPlotTemplate(
            id="revelation_climax",
            name="真相揭露",
            applicable_action_types=[ActionType.REVELATION, ActionType.CONFRONTATION],
            applicable_plot_types=[PlotAdvancementType.REVELATION, PlotAdvancementType.TURNING_POINT],
            typical_beat_count=5,
            typical_action_ratio=0.3,
            pacing_pattern=PacingType.BUILDING,
            intensity_curve=[
                ActionIntensity.LOW, ActionIntensity.MODERATE, ActionIntensity.HIGH,
                ActionIntensity.EXTREME, ActionIntensity.HIGH
            ],
            starting_tension=0.3,
            peak_tension=0.95,
            ending_tension=0.6,
            opening_pattern="Tension builds, hints dropped",
            development_pattern="Questions, denials, evidence mounting",
            climax_pattern="The reveal, truth exposed",
            closing_pattern="Reactions, consequences begin",
            action_detail_level="brief",
            dialogue_in_action=True,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "质问",
                "否认"
            ],
            typical_climax_beats=[
                "揭露真相",
                "震撼反应"
            ],
            typical_closing_beats=[
                "沉默",
                "爆发"
            ]
        ),
        "negotiation_high_stakes": ActionPlotTemplate(
            id="negotiation_high_stakes",
            name="高风险谈判",
            applicable_action_types=[ActionType.NEGOTIATION, ActionType.CONFRONTATION],
            applicable_plot_types=[PlotAdvancementType.DECISION, PlotAdvancementType.RELATIONSHIP_CHANGE],
            typical_beat_count=6,
            typical_action_ratio=0.2,
            pacing_pattern=PacingType.MODERATE,
            intensity_curve=[
                ActionIntensity.MODERATE, ActionIntensity.HIGH, ActionIntensity.EXTREME,
                ActionIntensity.HIGH, ActionIntensity.MODERATE, ActionIntensity.MODERATE
            ],
            starting_tension=0.4,
            peak_tension=0.85,
            ending_tension=0.5,
            opening_pattern="Parties state positions",
            development_pattern="Back and forth, concessions, demands",
            climax_pattern="Final offer, decision point",
            closing_pattern="Agreement or breakdown",
            action_detail_level="brief",
            dialogue_in_action=True,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "开场陈述",
                "立场声明"
            ],
            typical_climax_beats=[
                "最后通牒",
                "艰难抉择"
            ],
            typical_closing_beats=[
                "握手言和",
                "谈判破裂"
            ]
        ),
        "rescue_mission": ActionPlotTemplate(
            id="rescue_mission",
            name="营救行动",
            applicable_action_types=[ActionType.RESCUE, ActionType.COMBAT],
            applicable_plot_types=[PlotAdvancementType.MAIN_PLOT, PlotAdvancementType.BREAKTHROUGH],
            typical_beat_count=7,
            typical_action_ratio=0.75,
            pacing_pattern=PacingType.CRESCENDO,
            intensity_curve=[
                ActionIntensity.LOW, ActionIntensity.MODERATE, ActionIntensity.HIGH,
                ActionIntensity.EXTREME, ActionIntensity.CLIMACTIC,
                ActionIntensity.HIGH, ActionIntensity.MODERATE
            ],
            starting_tension=0.3,
            peak_tension=0.95,
            ending_tension=0.4,
            opening_pattern="Approach target, overcome obstacles",
            development_pattern="Infiltrate, fight guards, locate target",
            climax_pattern="Confront antagonist, rescue moment",
            closing_pattern="Escape with rescued, aftermath",
            action_detail_level="detailed",
            dialogue_in_action=False,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "潜入",
                "避开巡逻"
            ],
            typical_climax_beats=[
                "击败守卫",
                "救出目标"
            ],
            typical_closing_beats=[
                "撤离",
                "追击"
            ]
        ),
        "betrayal_revelation": ActionPlotTemplate(
            id="betrayal_revelation",
            name="背叛揭露",
            applicable_action_types=[ActionType.BETRAYAL, ActionType.CONFRONTATION],
            applicable_plot_types=[PlotAdvancementType.REVELATION, PlotAdvancementType.TURNING_POINT],
            typical_beat_count=5,
            typical_action_ratio=0.4,
            pacing_pattern=PacingType.BUILDING,
            intensity_curve=[
                ActionIntensity.LOW, ActionIntensity.MODERATE, ActionIntensity.HIGH,
                ActionIntensity.EXTREME, ActionIntensity.HIGH
            ],
            starting_tension=0.3,
            peak_tension=0.98,
            ending_tension=0.7,
            opening_pattern="Trust established, shadow of doubt",
            development_pattern="Evidence mounting, denial",
            climax_pattern="Betrayal exposed, confrontation",
            closing_pattern="Emotional fallout, new alliance or isolation",
            action_detail_level="moderate",
            dialogue_in_action=True,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "信任时刻",
                "异常迹象"
            ],
            typical_climax_beats=[
                "背叛揭露",
                "愤怒质问"
            ],
            typical_closing_beats=[
                "决裂",
                "新的决心"
            ]
        ),
        "sacrifice_moment": ActionPlotTemplate(
            id="sacrifice_moment",
            name="牺牲时刻",
            applicable_action_types=[ActionType.SACRIFICE, ActionType.COMBAT],
            applicable_plot_types=[PlotAdvancementType.TURNING_POINT, PlotAdvancementType.CHARACTER_DEVELOPMENT],
            typical_beat_count=5,
            typical_action_ratio=0.6,
            pacing_pattern=PacingType.CRESCENDO,
            intensity_curve=[
                ActionIntensity.MODERATE, ActionIntensity.HIGH, ActionIntensity.EXTREME,
                ActionIntensity.CLIMACTIC, ActionIntensity.LOW
            ],
            starting_tension=0.5,
            peak_tension=0.98,
            ending_tension=0.2,
            opening_pattern="Situation desperate, sacrifice considered",
            development_pattern="Resolution forms, goodbye moments",
            climax_pattern="The sacrifice itself",
            closing_pattern="Impact on others, legacy",
            action_detail_level="detailed",
            dialogue_in_action=True,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "绝境",
                "内心挣扎"
            ],
            typical_climax_beats=[
                "挺身而出",
                "牺牲"
            ],
            typical_closing_beats=[
                "悲伤与敬意",
                "继承遗志"
            ]
        ),
        "triumph_victory": ActionPlotTemplate(
            id="triumph_victory",
            name="胜利时刻",
            applicable_action_types=[ActionType.TRIUMPH, ActionType.COMBAT],
            applicable_plot_types=[PlotAdvancementType.MAIN_PLOT, PlotAdvancementType.BREAKTHROUGH],
            typical_beat_count=4,
            typical_action_ratio=0.5,
            pacing_pattern=PacingType.DENouement,
            intensity_curve=[
                ActionIntensity.HIGH, ActionIntensity.EXTREME, ActionIntensity.HIGH, ActionIntensity.MODERATE
            ],
            starting_tension=0.7,
            peak_tension=0.95,
            ending_tension=0.3,
            opening_pattern="Final push, turning point",
            development_pattern="Victory achieved, enemy falls",
            climax_pattern="Celebration, recognition",
            closing_pattern="Reflection, new challenges ahead",
            action_detail_level="moderate",
            dialogue_in_action=True,
            internal_thought_in_action=True,
            typical_opening_beats=[
                "最后一击",
                "敌人投降"
            ],
            typical_climax_beats=[
                "胜利宣言",
                "拥抱"
            ],
            typical_closing_beats=[
                "庆祝",
                "新的旅程"
            ]
        ),
    }

    def __init__(self, ai_service: AIService):
        """Initialize action plot engine."""
        self.ai_service = ai_service

    def _build_action_sequence_prompt(
        self,
        plan: ActionPlotPlan,
        characters: list[Character],
        template: Optional[ActionPlotTemplate] = None,
    ) -> str:
        """Build prompt for action sequence generation."""
        char_profiles = []
        for i, char in enumerate(characters):
            if isinstance(char, dict):
                name = char.get('name', f'角色{i+1}')
                personality = char.get('personality_description', '')
                skills = char.get('skills', [])
            else:
                name = getattr(char, 'name', f'角色{i+1}')
                personality = getattr(char, 'personality_description', '')
                skills = getattr(char, 'skills', [])

            char_profiles.append(
                f"角色{i+1}: {name}\n"
                f"  性格: {personality[:100] if personality else '未描述'}\n"
                f"  技能: {', '.join([str(s) for s in skills[:3]]) if skills else '普通'}"
            )

        chars_str = "\n".join(char_profiles)

        action_type_str = plan.primary_action_type.value
        target_intensity = plan.target_intensity.value
        target_tension = plan.target_tension
        target_beats = plan.target_action_count

        stakes = plan.stakes_description or "未明确"

        prompt = f"""为以下场景生成紧张刺激的动作描写：

角色信息：
{chars_str}

动作类型：{action_type_str}
目标强度：{target_intensity}
目标张力：{target_tension:.0%}
目标节拍数：{target_beats}
赌注：{stakes}

平衡：动作{plan.balance_action_plot*100:.0}% vs 情节{(1-plan.balance_action_plot)*100:.0}%
节奏类型：{plan.pacing_type.value}

要求：
1. 动作描写要紧张刺激、有画面感
2. 注重动作细节，不要过于简洁
3. 穿插人物心理活动
4. 张力要逐步升级，到达高潮后回落
5. 每个角色的行动要有区分度
6. 直接输出动作描写内容，不要解释"""
        return prompt

    def _build_plot_advancement_prompt(
        self,
        plan: ActionPlotPlan,
        characters: list[Character],
    ) -> str:
        """Build prompt for plot advancement generation."""
        char_profiles = []
        for i, char in enumerate(characters):
            if isinstance(char, dict):
                name = char.get('name', f'角色{i+1}')
                goals = char.get('goals', '')
            else:
                name = getattr(char, 'name', f'角色{i+1}')
                goals = getattr(char, 'goals', '')

            char_profiles.append(f"角色{i+1}: {name} - 目标: {goals[:50] if goals else '未设定'}")

        chars_str = "\n".join(char_profiles)

        plot_type = plan.primary_plot_type.value
        target_beats = plan.target_plot_count
        stakes = plan.stakes_description or "未明确"

        prompt = f"""为以下场景生成情节推进描写：

角色目标：
{chars_str}

情节类型：{plot_type}
目标节拍数：{target_beats}
赌注：{stakes}

要求：
1. 情节推进要清晰、有逻辑
2. 展现角色的决策过程
3. 适当埋伏笔，为后续铺垫
4. 每个情节点要有因果关系
5. 直接输出情节推进内容，不要解释"""
        return prompt

    def _build_combined_prompt(
        self,
        action_content: str,
        plot_content: str,
        plan: ActionPlotPlan,
        balance: float,
    ) -> str:
        """Build prompt for combining action and plot."""
        prompt = f"""将以下动作描写和情节推进内容有机融合：

【动作描写】
{action_content}

【情节推进】
{plot_content}

平衡比例：动作{balance*100:.0}% vs 情节{(1-balance)*100:.0}%
节奏：{plan.pacing_type.value}

要求：
1. 将动作和情节融合为流畅的叙事
2. 在动作中穿插必要的情节交代
3. 通过动作展现人物性格和关系变化
4. 保持张力和节奏
5. 直接输出整合后的内容，不要解释"""
        return prompt

    async def generate(
        self,
        scene_id: str,
        characters: list[Character],
        primary_action_type: ActionType,
        primary_plot_type: PlotAdvancementType,
        stakes_description: str = "",
        target_intensity: ActionIntensity = ActionIntensity.MODERATE,
        target_tension: float = 0.5,
        target_action_count: int = 5,
        target_plot_count: int = 3,
        balance_action_plot: float = 0.5,
        pacing_type: PacingType = PacingType.MODERATE,
        include_dialogue: bool = True,
        include_description: bool = True,
        previous_context: Optional[str] = None,
    ) -> ActionPlotDraft:
        """Generate action and plot advancement content.

        Args:
            scene_id: Scene identifier
            characters: Characters involved
            primary_action_type: Primary type of action
            primary_plot_type: Primary type of plot advancement
            stakes_description: What's at stake
            target_intensity: Target intensity level
            target_tension: Target tension 0-1
            target_action_count: Target number of action beats
            target_plot_count: Target number of plot beats
            balance_action_plot: Balance 0=action, 1=plot
            pacing_type: Overall pacing
            include_dialogue: Include dialogue
            include_description: Include scene description
            previous_context: Previous scene context for continuity

        Returns:
            Generated action plot draft
        """
        plan_id = f"actionplot_{scene_id}"

        # Create plan
        plan = ActionPlotPlan(
            id=plan_id,
            scene_id=scene_id,
            primary_action_type=primary_action_type,
            primary_plot_type=primary_plot_type,
            target_intensity=target_intensity,
            target_tension=target_tension,
            target_action_count=target_action_count,
            target_plot_count=target_plot_count,
            balance_action_plot=balance_action_plot,
            pacing_type=pacing_type,
            include_dialogue=include_dialogue,
            include_description=include_description,
            stakes_description=stakes_description,
        )

        # Get template if available
        template = self._get_matching_template(primary_action_type, primary_plot_type)

        # Generate action content
        action_prompt = self._build_action_sequence_prompt(plan, characters, template)
        context_hint = ""
        if previous_context:
            context_hint = f"\n前情：{previous_context[-150:]}..."
        action_result = await self.ai_service.generate(action_prompt + context_hint, temperature=0.75)

        # Generate plot content
        plot_prompt = self._build_plot_advancement_prompt(plan, characters)
        plot_result = await self.ai_service.generate(plot_prompt + context_hint, temperature=0.7)

        # Combine
        combined_prompt = self._build_combined_prompt(action_result, plot_result, plan, balance_action_plot)
        combined_result = await self.ai_service.generate(combined_prompt, temperature=0.7)

        # Create draft
        draft = ActionPlotDraft(
            id=f"draft_{plan_id}",
            plan_id=plan_id,
            scene_id=scene_id,
            action_content=action_result.strip(),
            plot_content=plot_result.strip(),
            combined_content=combined_result.strip(),
            action_word_count=len(action_result),
            plot_word_count=len(plot_result),
            total_word_count=len(combined_result),
            status="draft",
        )

        # Score the draft
        draft = self._score_draft(draft, plan, template)

        return draft

    def _get_matching_template(
        self,
        action_type: ActionType,
        plot_type: PlotAdvancementType,
    ) -> Optional[ActionPlotTemplate]:
        """Get template matching the action and plot types."""
        for template in self.TEMPLATES.values():
            if action_type in template.applicable_action_types:
                return template
        return None

    def _score_draft(
        self,
        draft: ActionPlotDraft,
        plan: ActionPlotPlan,
        template: Optional[ActionPlotTemplate],
    ) -> ActionPlotDraft:
        """Calculate quality scores for the draft."""
        # Action coherence based on word count vs target
        action_ratio = draft.action_word_count / max(1, plan.target_action_count * 100)
        draft.action_coherence_score = min(1.0, action_ratio * 0.8)

        # Plot coherence
        plot_ratio = draft.plot_word_count / max(1, plan.target_plot_count * 100)
        draft.plot_coherence_score = min(1.0, plot_ratio * 0.8)

        # Pacing score
        draft.pacing_score = 0.7  # Default

        # Tension score
        tension_fit = 1.0 - abs(draft.tension_score - plan.target_tension)
        draft.tension_score = tension_fit

        # Excitement based on action content
        draft.excitement_score = min(1.0, draft.action_word_count / 500 * 0.8)

        # Flags
        draft.has_climactic_moment = draft.tension_score > 0.7
        draft.advances_plot = draft.plot_coherence_score > 0.5
        draft.has_stakes_clarity = len(plan.stakes_description) > 0

        return draft

    async def revise(
        self,
        draft: ActionPlotDraft,
        revision_notes: list[str],
    ) -> ActionPlotRevision:
        """Revise action plot content based on notes."""
        prompt = f"""请根据以下意见修改动作与情节推进内容：

原文：
{draft.combined_content}

修改意见：
{chr(10).join(f"- {note}" for note in revision_notes)}

要求：
1. 按照意见进行修改
2. 保持紧张感和节奏
3. 不要大幅删减或添加内容
4. 直接输出修改后的内容，不要解释"""

        revised = await self.ai_service.generate(prompt, temperature=0.5)

        return ActionPlotRevision(
            original_draft=draft,
            revision_notes=revision_notes,
            revised_content=revised.strip(),
            quality_score=0.8,
        )

    def analyze(
        self,
        draft: ActionPlotDraft,
    ) -> ActionPlotAnalysis:
        """Analyze action plot quality."""
        issues = []
        recommendations = []

        # Action analysis
        if draft.action_word_count < 200:
            issues.append("动作描写过少，不够紧张刺激")
            recommendations.append("增加动作细节和打斗描写")
        elif draft.action_word_count > 2000:
            issues.append("动作描写过长，可能影响节奏")
            recommendations.append("精简动作描写，突出关键瞬间")

        # Plot analysis
        if draft.plot_word_count < 100:
            issues.append("情节推进内容过少")
            recommendations.append("增加角色决策和情节转折")

        # Balance
        action_ratio = draft.action_word_count / max(1, draft.total_word_count)
        if action_ratio < 0.2:
            issues.append("动作描写比例过低")
        elif action_ratio > 0.9:
            issues.append("动作描写比例过高，缺乏情节推进")

        # Tension
        if draft.tension_score < 0.5:
            issues.append("张力不足")
            recommendations.append("增加更多冲突和悬念")

        # Build analysis
        action_coherence = draft.action_coherence_score
        plot_coherence = draft.plot_coherence_score
        overall = (action_coherence + plot_coherence + draft.pacing_score + draft.tension_score) / 4

        return ActionPlotAnalysis(
            draft_id=draft.id,
            action_coherence=action_coherence,
            action_pacing=draft.pacing_score,
            action_clarity=0.7,
            combat真实性=0.6,
            tension_progression=draft.tension_score,
            plot_coherence=plot_coherence,
            plot_pacing=draft.pacing_score,
            character_decision_clarity=0.7,
            stakes_clarity=0.6 if draft.has_stakes_clarity else 0.3,
            foreshadowing_effectiveness=0.5,
            action_plot_balance=1.0 - abs(action_ratio - 0.5) * 2,
            dialogue_integration=0.6,
            description_integration=0.6,
            overall_quality_score=overall,
            critical_issues=[i for i in issues if "过少" in i or "过低" in i],
            minor_issues=[i for i in issues if i not in [j for j in issues if "过少" in j or "过低" in j]],
            recommendations=recommendations,
        )

    def get_template(self, template_name: str) -> Optional[ActionPlotTemplate]:
        """Get a template by name."""
        return self.TEMPLATES.get(template_name)

    def get_all_templates(self) -> dict[str, ActionPlotTemplate]:
        """Get all available templates."""
        return self.TEMPLATES.copy()

    async def generate_from_template(
        self,
        template_name: str,
        scene_id: str,
        characters: list[Character],
        stakes_description: str = "",
        **kwargs,
    ) -> ActionPlotDraft:
        """Generate action plot from a template.

        Args:
            template_name: Name of template to use
            scene_id: Scene identifier
            characters: Characters involved
            stakes_description: What's at stake
            **kwargs: Override template values

        Returns:
            Generated action plot draft
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        action_type = kwargs.get('action_type', template.applicable_action_types[0])
        plot_type = kwargs.get('plot_type', template.applicable_plot_types[0])
        intensity = kwargs.get('intensity', ActionIntensity.MODERATE)
        pacing = kwargs.get('pacing', template.pacing_pattern)

        return await self.generate(
            scene_id=scene_id,
            characters=characters,
            primary_action_type=action_type,
            primary_plot_type=plot_type,
            stakes_description=stakes_description,
            target_intensity=intensity,
            target_tension=template.peak_tension,
            target_action_count=kwargs.get('target_action_count', template.typical_beat_count),
            target_plot_count=kwargs.get('target_plot_count', max(2, template.typical_beat_count // 2)),
            balance_action_plot=kwargs.get('balance', 1.0 - template.typical_action_ratio),
            pacing_type=pacing,
        )

    def export_draft(self, draft: ActionPlotDraft) -> dict:
        """Export draft to dictionary format."""
        return {
            "draft_id": draft.id,
            "scene_id": draft.scene_id,
            "combined_content": draft.combined_content,
            "action_content": draft.action_content,
            "plot_content": draft.plot_content,
            "action_word_count": draft.action_word_count,
            "plot_word_count": draft.plot_word_count,
            "total_word_count": draft.total_word_count,
            "action_coherence_score": draft.action_coherence_score,
            "plot_coherence_score": draft.plot_coherence_score,
            "tension_score": draft.tension_score,
            "has_climactic_moment": draft.has_climactic_moment,
            "advances_plot": draft.advances_plot,
            "status": draft.status,
        }