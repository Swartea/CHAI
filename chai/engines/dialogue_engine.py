"""Dialogue engine for generating character-consistent dialogue."""

from typing import Optional
from chai.models import Character
from chai.models.dialogue import (
    DialoguePlan, DialogueDraft, DialogueRevision, DialogueAnalysis,
    DialogueTemplate, DialogueExchange, DialogueLine, DialoguePurpose,
    DialogueType, DialogueTone, CharacterDialogueStyle, DialogueExchange,
    CharacterDialogueStyle
)
from chai.services import AIService


class DialogueEngine:
    """Engine for generating character-consistent dialogue."""

    # Pre-built templates for common dialogue situations
    TEMPLATES: dict[str, DialogueTemplate] = {
        "confrontation": DialogueTemplate(
            id="confrontation",
            name="对峙/冲突",
            applicable_purposes=[DialoguePurpose.CONFLICT, DialoguePurpose.TENSION_BUILDING],
            applicable_tones=[DialogueTone.HOSTILE, DialogueTone.TENSE, DialogueTone.IRONIC],
            typical_line_count=12,
            typical_participants=2,
            pacing_pattern="fast",
            tension_curve=["moderate", "high", "critical", "resolution"],
            opening_pattern="Direct challenge or accusation",
            development_pattern="Escalating exchanges with interruptions",
            closing_pattern="Climactic statement or exit",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="deep",
            typical_opening_phrases=[
                "你以为你可以...",
                "我不相信你说的话",
                "这都是你的错"
            ],
            transition_phrases=[
                "别打断我",
                "听我说完",
                "事实是..."
            ],
            closing_phrases=[
                "我们之间完了",
                "你会后悔的",
                "这次我不会再退让"
            ]
        ),
        "romantic": DialogueTemplate(
            id="romantic",
            name="浪漫/亲密",
            applicable_purposes=[DialoguePurpose.EMOTIONAL, DialoguePurpose.ALLIANCE_BUILDING],
            applicable_tones=[DialogueTone.ROMANTIC, DialogueTone.INTIMATE, DialogueTone.JOYFUL],
            typical_line_count=8,
            typical_participants=2,
            pacing_pattern="slow",
            tension_curve=["subtle", "growing", "intimate", "warm"],
            opening_pattern="Soft opening, often with observation",
            development_pattern="Building intimacy through shared moments",
            closing_pattern="Tender declaration or action",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="moderate",
            typical_opening_phrases=[
                "你知道吗...",
                "我一直想告诉你...",
                "你的眼睛像..."
            ],
            transition_phrases=[
                "不只是这样",
                "当我看到你的时候...",
                "我想..."
            ],
            closing_phrases=[
                "我爱你",
                "我会一直在你身边",
                "这是我的真心话"
            ]
        ),
        "revelation": DialogueTemplate(
            id="revelation",
            name="真相揭露",
            applicable_purposes=[DialoguePurpose.REVELATION, DialoguePurpose.PLOT_ADVANCEMENT],
            applicable_tones=[DialogueTone.SUSPICIOUS, DialogueTone.TENSE, DialogueTone.SAD],
            typical_line_count=10,
            typical_participants=2,
            pacing_pattern="moderate",
            tension_curve=["building", "reveal", "shock", "aftermath"],
            opening_pattern="Leading questions or observations",
            development_pattern="Gradual revelation with reactions",
            closing_pattern="Impact statement",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="deep",
            typical_opening_phrases=[
                "你需要知道真相",
                "我一直在隐瞒...",
                "事情不是你想的那样"
            ],
            transition_phrases=[
                "但是这还不是全部",
                "听我说完",
                "当你知道真相后..."
            ],
            closing_phrases=[
                "这就是全部的真相",
                "我说的都是真的",
                "现在你明白了吗"
            ]
        ),
        "negotiation": DialogueTemplate(
            id="negotiation",
            name="谈判/交涉",
            applicable_purposes=[DialoguePurpose.ALLIANCE_BUILDING, DialoguePurpose.MANIPULATION],
            applicable_tones=[DialogueTone.FORMAL, DialogueTone.SUSPICIOUS, DialogueTone.TENSE],
            typical_line_count=14,
            typical_participants=2,
            pacing_pattern="moderate",
            tension_curve=["formal", "testing", "negotiating", "agreement"],
            opening_pattern="Formal greeting and proposition",
            development_pattern="Terms and conditions discussion",
            closing_pattern="Agreement or disagreement",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="moderate",
            typical_opening_phrases=[
                "我们来谈谈条件",
                "我希望我们能达成共识",
                "这是我的提议"
            ],
            transition_phrases=[
                "当然，还有一点...",
                "如果我们能...",
                "那么，你这边..."
            ],
            closing_phrases=[
                "成交",
                "我需要时间考虑",
                "恐怕这不可能"
            ]
        ),
        "information_gathering": DialogueTemplate(
            id="information_gathering",
            name="信息收集/审问",
            applicable_purposes=[DialoguePurpose.INFORMATION_GATHERING, DialoguePurpose.CONFLICT],
            applicable_tones=[DialogueTone.SUSPICIOUS, DialogueTone.TENSE, DialogueTone.FORMAL],
            typical_line_count=12,
            typical_participants=2,
            pacing_pattern="moderate_to_fast",
            tension_curve=["questioning", "pressure", "resistance", "breakthrough"],
            opening_pattern="Direct questions",
            development_pattern="Follow-up questions and challenges",
            closing_pattern="Key information revealed or withheld",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="subtle",
            typical_opening_phrases=[
                "我需要你回答我",
                "最后一次机会",
                "告诉我真相"
            ],
            transition_phrases=[
                "不要撒谎",
                "你知道我总会知道",
                "再给你一次机会"
            ],
            closing_phrases=[
                "终于说实话了",
                "你还想隐瞒什么",
                "看来你不会说了"
            ]
        ),
        "comic_relief": DialogueTemplate(
            id="comic_relief",
            name="喜剧/轻松",
            applicable_purposes=[DialoguePurpose.COMIC_RELIEF, DialoguePurpose.EMOTIONAL],
            applicable_tones=[DialogueTone.JOYFUL, DialogueTone.CASUAL, DialogueTone.IRONIC],
            typical_line_count=8,
            typical_participants=2,
            pacing_pattern="fast",
            tension_curve=["light", "lighter", "humorous", "resolved"],
            opening_pattern="Casual observation or joke",
            development_pattern="Back and forth banter",
            closing_pattern="Final quip or shared laugh",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="subtle",
            typical_opening_phrases=[
                "你知道最可笑的是什么吗...",
                "我刚才在想...",
                "这让我想起..."
            ],
            transition_phrases=[
                "但这还不是最糟的",
                "然后你知道发生了什么吗",
                "说实话..."
            ],
            closing_phrases=[
                "我就是忍不住笑",
                "生活就是这样",
                "至少我们还有这个"
            ]
        ),
        "emotional": DialogueTemplate(
            id="emotional",
            name="情感表达",
            applicable_purposes=[DialoguePurpose.EMOTIONAL, DialoguePurpose.CHARACTER_REVELATION],
            applicable_tones=[DialogueTone.SAD, DialogueTone.JOYFUL, DialogueTone.INTIMATE],
            typical_line_count=8,
            typical_participants=2,
            pacing_pattern="slow",
            tension_curve=["vulnerable", "open", "sharing", "connected"],
            opening_pattern="Soft, vulnerable opening",
            development_pattern="Deep emotional sharing",
            closing_pattern="Emotional connection or resolution",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="moderate",
            typical_opening_phrases=[
                "我从来没有告诉过别人...",
                "有时候我会想...",
                "你了解我的过去"
            ],
            transition_phrases=[
                "但那不是全部",
                "我还想说...",
                "最让我困扰的是..."
            ],
            closing_phrases=[
                "谢谢你愿意听我说",
                "有你在真好",
                "这就是我"
            ]
        ),
        "manipulation": DialogueTemplate(
            id="manipulation",
            name="操纵/欺骗",
            applicable_purposes=[DialoguePurpose.MANIPULATION, DialoguePurpose.CONFLICT],
            applicable_tones=[DialogueTone.SUSPICIOUS, DialogueTone.FORMAL, DialogueTone.IRONIC],
            typical_line_count=10,
            typical_participants=2,
            pacing_pattern="moderate",
            tension_curve=["charming", "persuasive", "revealing", "exit"],
            opening_pattern="Charming or seemingly helpful",
            development_pattern="Gradual manipulation with hidden agenda",
            closing_pattern="Achievement of goal or suspicious exit",
            dialogue_style=DialogueType.DIRECT,
            subtext_depth="deep",
            typical_opening_phrases=[
                "我只是想帮你",
                "相信我",
                "这是一个双赢的机会"
            ],
            transition_phrases=[
                "正如我所说的...",
                "让我解释...",
                "你只需要..."
            ],
            closing_phrases=[
                "你会明白的",
                "我们成交了吗",
                "你会感谢我的"
            ]
        ),
    }

    def __init__(self, ai_service: AIService):
        """Initialize dialogue engine."""
        self.ai_service = ai_service

    def _build_character_dialogue_style(
        self,
        character: Character,
    ) -> CharacterDialogueStyle:
        """Build a character's dialogue style profile from character data."""
        speech_chars = character.speech_characteristics if hasattr(character, 'speech_characteristics') else []
        catchphrases = character.catchphrases if hasattr(character, 'catchphrases') else []
        speech_pattern = character.speech_pattern if hasattr(character, 'speech_pattern') else ""

        return CharacterDialogueStyle(
            speech_pattern=speech_pattern or character.personality_description[:100] if character.personality_description else "",
            vocabulary_level="moderate",
            sentence_structure="mixed",
            formal_or_informal="neutral",
            use_of_honorifics=True,
            accent_dialect=None,
            catchphrases=list(catchphrases),
            filler_words=["嗯", "啊", "这个", "那个"],
            verbal_tics=[],
            speech_quirks=speech_chars,
            emotional_restraint="moderate",
            directness="moderate",
            passive_aggressive=False,
            interruption_tendency="rare",
            listening_quality="attentive",
            response_delay="normal",
        )

    def _get_dialogue_prompt(
        self,
        plan: DialoguePlan,
        characters: list[Character],
    ) -> str:
        """Build the AI prompt for dialogue generation."""
        char_profiles = []
        for i, char_data in enumerate(characters):
            if isinstance(char_data, dict):
                name = char_data.get('name', f'角色{i+1}')
                personality = char_data.get('personality_description', '')
                speech = char_data.get('speech_pattern', '')
            else:
                name = getattr(char_data, 'name', f'角色{i+1}')
                personality = getattr(char_data, 'personality_description', '')
                speech = getattr(char_data, 'speech_pattern', '')

            char_profiles.append(
                f"角色{i+1}: {name}\n"
                f"  性格: {personality[:100] if personality else '未描述'}\n"
                f"  说话风格: {speech[:100] if speech else '正常'}"
            )

        chars_str = "\n".join(char_profiles)

        purpose_descriptions = {
            DialoguePurpose.INFORMATION_GATHERING: "信息交流/审问",
            DialoguePurpose.CONFLICT: "冲突/对峙",
            DialoguePurpose.ALLIANCE_BUILDING: "建立信任/结盟",
            DialoguePurpose.REVELATION: "揭露秘密/真相",
            DialoguePurpose.EMOTIONAL: "情感表达",
            DialoguePurpose.MANIPULATION: "操纵/欺骗",
            DialoguePurpose.TENSION_BUILDING: "制造紧张",
            DialoguePurpose.COMIC_RELIE: "喜剧/轻松",
            DialoguePurpose.PLOT_ADVANCEMENT: "推进剧情",
            DialoguePurpose.CHARACTER_REVELATION: "展现角色",
        }

        prompt = f"""为以下场景生成角色对话：

角色信息：
{chars_str}

场景情况：{plan.situation}
对话主题：{plan.topic}
对话目的：{purpose_descriptions.get(plan.purpose, str(plan.purpose))}
关系类型：{plan.relationship_type}
关系历史：{plan.relationship_history}

起始情绪：{plan.starting_emotion}
结束情绪：{plan.ending_emotion}
目标行数：{plan.target_line_count}
目标字数：{plan.target_word_count}

语气：{plan.target_tone.value if plan.target_tone else 'normal'}
张力：{plan.tension_level}
节奏：{plan.pacing}

剧情要点：{', '.join(plan.plot_points_to_cover) if plan.plot_points_to_cover else '无特定要求'}
待揭示信息：{', '.join(plan.information_to_reveal) if plan.information_to_reveal else '无特定要求'}

要求：
1. 对话必须符合每个角色的性格和说话风格
2. 避免所有角色使用相同的口吻
3. 适当加入语气词、停顿描写
4. 对话要有潜台词/言外之意（可选）
5. 张力要逐渐升级
6. 直接输出对话，不要解释"""
        return prompt

    async def generate_dialogue(
        self,
        scene_id: str,
        characters: list[Character],
        purpose: DialoguePurpose,
        topic: str,
        situation: str,
        relationship_type: str = "neutral",
        relationship_history: str = "",
        starting_emotion: str = "neutral",
        ending_emotion: str = "neutral",
        target_line_count: int = 10,
        target_word_count: int = 500,
        dialogue_type: DialogueType = DialogueType.DIRECT,
        target_tone: DialogueTone = DialogueTone.CASUAL,
        tension_level: str = "moderate",
        pacing: str = "moderate",
        plot_points_to_cover: Optional[list[str]] = None,
        information_to_reveal: Optional[list[str]] = None,
        secrets_to_keep: Optional[list[str]] = None,
        include_subtext: bool = True,
        include_gestures: bool = True,
        previous_dialogue_context: Optional[str] = None,
    ) -> DialogueDraft:
        """Generate dialogue for a scene.

        Args:
            scene_id: Scene identifier
            characters: List of characters participating
            purpose: Primary purpose of dialogue
            topic: Main topic of conversation
            situation: Situation/context description
            relationship_type: Relationship between speakers
            relationship_history: History between characters
            starting_emotion: Starting emotional state
            ending_emotion: Ending emotional state
            target_line_count: Target number of dialogue lines
            target_word_count: Target total word count
            dialogue_type: Preferred dialogue type
            target_tone: Target overall tone
            tension_level: Tension: low, moderate, high, climactic
            pacing: Pacing: slow, moderate, fast
            plot_points_to_cover: Plot points to convey
            information_to_reveal: Information to reveal
            secrets_to_keep: Secrets that should not be revealed
            include_subtext: Whether to include subtext
            include_gestures: Whether to include gesture descriptions
            previous_dialogue_context: Previous dialogue for continuity

        Returns:
            Generated dialogue draft
        """
        # Build plan
        plan_id = f"dialogue_{scene_id}"
        char_dicts = []
        for char in characters:
            char_dicts.append({
                'name': char.name,
                'personality_description': char.personality_description,
                'speech_pattern': char.speech_pattern,
                'speech_characteristics': char.speech_characteristics if hasattr(char, 'speech_characteristics') else [],
                'catchphrases': char.catchphrases if hasattr(char, 'catchphrases') else [],
            })

        plan = DialoguePlan(
            id=plan_id,
            scene_id=scene_id,
            characters=char_dicts,
            speaker_count=len(characters),
            purpose=purpose,
            topic=topic,
            situation=situation,
            dialogue_type=dialogue_type,
            target_tone=target_tone,
            tension_level=tension_level,
            pacing=pacing,
            target_line_count=target_line_count,
            target_word_count=target_word_count,
            plot_points_to_cover=plot_points_to_cover or [],
            information_to_reveal=information_to_reveal or [],
            secrets_to_keep=secrets_to_keep or [],
            relationship_type=relationship_type,
            relationship_history=relationship_history,
            starting_emotion=starting_emotion,
            ending_emotion=ending_emotion,
            include_subtext=include_subtext,
            include_gestures=include_gestures,
        )

        # Generate dialogue via AI
        prompt = self._get_dialogue_prompt(plan, characters)
        context_hint = ""
        if previous_dialogue_context:
            context_hint = f"\n前情提要：{previous_dialogue_context[-200:]}..."

        full_prompt = prompt + context_hint

        result = await self.ai_service.generate(full_prompt, temperature=0.7)

        # Parse the result into exchanges
        exchanges = self._parse_dialogue_result(
            result=result,
            plan=plan,
            characters=characters,
        )

        # Build draft
        combined_text = self._combine_dialogue(exchanges)

        draft = DialogueDraft(
            id=f"draft_{plan_id}",
            plan_id=plan_id,
            scene_id=scene_id,
            exchanges=exchanges,
            combined_text=combined_text,
            total_line_count=sum(len(e.lines) for e in exchanges),
            total_word_count=len(combined_text),
            status="draft",
        )

        # Calculate initial quality scores
        draft = self._score_draft(draft, plan)

        return draft

    def _parse_dialogue_result(
        self,
        result: str,
        plan: DialoguePlan,
        characters: list[Character],
    ) -> list[DialogueExchange]:
        """Parse AI-generated dialogue into structured exchanges."""
        exchanges = []
        lines = result.strip().split('\n')

        exchange_id = f"exchange_{plan.id}"
        current_lines = []
        current_speaker = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to identify speaker
            speaker_name = None
            dialogue_content = line

            # Check for speaker markers like "角色1：" or "小明："
            for char in characters:
                if char.name + "：" in line:
                    speaker_name = char.name
                    dialogue_content = line.split("：", 1)[1]
                    break
                elif char.name + ":" in line:
                    speaker_name = char.name
                    dialogue_content = line.split(":", 1)[1]
                    break

            # Also check for numbered speakers
            if not speaker_name:
                for i, char in enumerate(characters):
                    if f"角色{i+1}：" in line:
                        speaker_name = char.name
                        dialogue_content = line.split("：", 1)[1]
                        break
                    elif f"角色{i+1}:" in line:
                        speaker_name = char.name
                        dialogue_content = line.split(":", 1)[1]
                        break

            if speaker_name and dialogue_content:
                # Find character ID
                speaker_id = None
                for char in characters:
                    if char.name == speaker_name:
                        speaker_id = char.id
                        break
                if not speaker_id:
                    speaker_id = speaker_name

                dialogue_line = DialogueLine(
                    id=f"line_{len(current_lines)}",
                    speaker_id=speaker_id,
                    speaker_name=speaker_name,
                    content=dialogue_content.strip(),
                    dialogue_type=plan.dialogue_type,
                    tone=plan.target_tone,
                    purpose=plan.purpose,
                    word_count=len(dialogue_content),
                )
                current_lines.append(dialogue_line)

        # Create exchange from lines
        if current_lines:
            exchange = DialogueExchange(
                id=exchange_id,
                scene_id=plan.scene_id,
                participants=[char.id for char in characters],
                participant_names=[char.name for char in characters],
                lines=current_lines,
                purpose=plan.purpose,
                topic=plan.topic,
                power_dynamic="equal",
                emotional_tone=plan.target_tone,
                total_word_count=sum(l.word_count for l in current_lines),
            )
            exchanges.append(exchange)

        return exchanges

    def _combine_dialogue(self, exchanges: list[DialogueExchange]) -> str:
        """Combine exchanges into a single dialogue text."""
        combined_lines = []
        for exchange in exchanges:
            for line in exchange.lines:
                if line.content:
                    combined_lines.append(f"{line.speaker_name}：{line.content}")

        return "\n".join(combined_lines)

    def _score_draft(
        self,
        draft: DialogueDraft,
        plan: DialoguePlan,
    ) -> DialogueDraft:
        """Calculate quality scores for the draft."""
        # Simple heuristic scoring
        # Naturalness based on line count vs target
        line_ratio = len(draft.exchanges) * sum(len(e.lines) for e in draft.exchanges) / max(1, plan.target_line_count)
        naturalness = min(1.0, line_ratio * 0.8)

        # Character voice score based on variety
        char_names = set()
        for ex in draft.exchanges:
            for line in ex.lines:
                char_names.add(line.speaker_name)
        voice_variety = len(char_names) / max(1, plan.speaker_count)
        character_voice = min(1.0, voice_variety * 0.9)

        # Purpose fulfillment based on content
        purpose_fulfillment = 0.7  # Default assumption

        draft.naturalness_score = naturalness
        draft.character_voice_score = character_voice
        draft.purpose_fulfillment_score = purpose_fulfillment

        # Check for plot advancement
        if plan.plot_points_to_cover or plan.information_to_reveal:
            draft.has_plot_advancement = True

        return draft

    async def revise_dialogue(
        self,
        draft: DialogueDraft,
        revision_notes: list[str],
    ) -> DialogueRevision:
        """Revise dialogue based on notes."""
        # Generate revised dialogue
        prompt = f"""请根据以下意见修改对话：

原文：
{draft.combined_text}

修改意见：
{chr(10).join(f"- {note}" for note in revision_notes)}

要求：
1. 按照意见进行修改
2. 保持角色性格一致性
3. 不要大幅删减或添加内容
4. 直接输出修改后的对话，不要解释"""

        revised_text = await self.ai_service.generate(prompt, temperature=0.5)

        # Parse revised exchanges
        # For simplicity, we keep the same structure but update content
        revised_exchanges = []
        for exchange in draft.exchanges:
            new_lines = []
            for line in exchange.lines:
                new_content = revised_text
                # Try to find content for this speaker
                for l in revised_text.split('\n'):
                    if line.speaker_name in l:
                        if '：' in l:
                            new_content = l.split('：', 1)[1]
                            break
                        elif ':' in l:
                            new_content = l.split(':', 1)[1]
                            break

                new_lines.append(DialogueLine(
                    id=line.id,
                    speaker_id=line.speaker_id,
                    speaker_name=line.speaker_name,
                    content=new_content.strip() if new_content else line.content,
                    dialogue_type=line.dialogue_type,
                    tone=line.tone,
                    purpose=line.purpose,
                    word_count=len(new_content) if new_content else line.word_count,
                ))
            revised_exchanges.append(DialogueExchange(
                id=exchange.id,
                scene_id=exchange.scene_id,
                participants=exchange.participants,
                participant_names=exchange.participant_names,
                lines=new_lines,
                purpose=exchange.purpose,
                topic=exchange.topic,
                power_dynamic=exchange.power_dynamic,
                emotional_tone=exchange.emotional_tone,
                total_word_count=sum(l.word_count for l in new_lines),
            ))

        return DialogueRevision(
            original_draft=draft,
            revision_notes=revision_notes,
            revised_exchanges=revised_exchanges,
            quality_score=0.8,
        )

    def analyze_dialogue(
        self,
        draft: DialogueDraft,
    ) -> DialogueAnalysis:
        """Analyze dialogue quality."""
        issues = []
        recommendations = []

        # Check line count variety
        speaker_lines = {}
        for ex in draft.exchanges:
            for line in ex.lines:
                if line.speaker_name not in speaker_lines:
                    speaker_lines[line.speaker_name] = 0
                speaker_lines[line.speaker_name] += 1

        # Check for dominance
        if speaker_lines:
            max_lines = max(speaker_lines.values())
            min_lines = min(speaker_lines.values())
            if max_lines > min_lines * 3:
                issues.append("某个角色对话过多，可能造成不平衡")

        # Check for catchphrase usage
        catchphrase_count = 0
        for ex in draft.exchanges:
            for line in ex.lines:
                if line.is_catchphrase:
                    catchphrase_count += 1

        # Naturalness based on word count
        avg_line_length = draft.total_word_count / max(1, draft.total_line_count)
        if avg_line_length < 5:
            issues.append("对话行过短，可能显得不自然")
            recommendations.append("增加每行的内容长度")
        elif avg_line_length > 100:
            issues.append("对话行过长，可能显得不自然")
            recommendations.append("拆分过长的对话行")

        # Flow score
        flow_score = min(1.0, draft.total_line_count / 10)

        # Build analysis
        character_consistency = {}
        for name in speaker_lines:
            character_consistency[name] = 0.7  # Default

        analysis = DialogueAnalysis(
            draft_id=draft.id,
            character_voice_consistency=character_consistency,
            speech_pattern_adherence=0.75,
            naturalness_score=draft.naturalness_score,
            dialogue_flow_score=flow_score,
            purpose_clarity=0.7,
            information_transfer=0.7,
            emotional_authenticity=0.7,
            subtext_effectiveness=0.6 if draft.total_line_count > 5 else 0.3,
            situation_appropriateness=0.8,
            relationship_consistency=0.75,
            overall_quality_score=(draft.naturalness_score + flow_score) / 2,
            critical_issues=[i for i in issues if "可能" not in i],
            minor_issues=[i for i in issues if "可能" in i],
            recommendations=recommendations,
        )

        return analysis

    def get_template(self, template_name: str) -> Optional[DialogueTemplate]:
        """Get a dialogue template by name."""
        return self.TEMPLATES.get(template_name)

    def get_all_templates(self) -> dict[str, DialogueTemplate]:
        """Get all available dialogue templates."""
        return self.TEMPLATES.copy()

    async def generate_from_template(
        self,
        template_name: str,
        scene_id: str,
        characters: list[Character],
        situation: str,
        topic: str,
        **kwargs,
    ) -> DialogueDraft:
        """Generate dialogue from a template.

        Args:
            template_name: Name of template to use
            scene_id: Scene identifier
            characters: Characters participating
            situation: Situation description
            topic: Topic of conversation
            **kwargs: Override template values

        Returns:
            Generated dialogue draft
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Extract kwargs with defaults from template
        purpose = kwargs.get('purpose', template.applicable_purposes[0] if template.applicable_purposes else DialoguePurpose.PLOT_ADVANCEMENT)
        target_tone = kwargs.get('target_tone', template.applicable_tones[0] if template.applicable_tones else DialogueTone.CASUAL)
        target_line_count = kwargs.get('target_line_count', template.typical_line_count)
        pacing = kwargs.get('pacing', template.pacing_pattern)

        return await self.generate_dialogue(
            scene_id=scene_id,
            characters=characters,
            purpose=purpose,
            topic=topic,
            situation=situation,
            target_line_count=target_line_count,
            target_word_count=target_line_count * 50,
            target_tone=target_tone,
            pacing=pacing,
            relationship_type=kwargs.get('relationship_type', 'neutral'),
            starting_emotion=kwargs.get('starting_emotion', 'neutral'),
            ending_emotion=kwargs.get('ending_emotion', 'neutral'),
        )

    def export_draft(self, draft: DialogueDraft) -> dict:
        """Export draft to dictionary format."""
        return {
            "draft_id": draft.id,
            "plan_id": draft.plan_id,
            "scene_id": draft.scene_id,
            "exchanges": [
                {
                    "id": ex.id,
                    "purpose": ex.purpose.value,
                    "lines": [
                        {
                            "speaker": line.speaker_name,
                            "content": line.content,
                            "tone": line.tone.value,
                        }
                        for line in ex.lines
                    ],
                }
                for ex in draft.exchanges
            ],
            "combined_text": draft.combined_text,
            "total_line_count": draft.total_line_count,
            "total_word_count": draft.total_word_count,
            "naturalness_score": draft.naturalness_score,
            "character_voice_score": draft.character_voice_score,
            "status": draft.status,
        }
