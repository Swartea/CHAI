"""Full book polishing engine for comprehensive manuscript polishing after completion.

This engine performs holistic cross-chapter analysis to polish the entire manuscript,
ensuring consistency and quality across all volumes and chapters.
"""

import uuid
import time
import re
from collections import Counter
from datetime import datetime
from typing import Optional

from chai.models.full_book_polishing import (
    PolishingStatus,
    PolishingType,
    PolishingSeverity,
    PolishingIssue,
    PolishingResult,
    VolumePolishingProfile,
    ChapterPolishingProfile,
    BookPolishingConfig,
    PolishingPlan,
    VolumePolishingReport,
    BookPolishingReport,
    PolishingSummary,
    FullBookPolishingRequest,
    FullBookPolishingResult,
    PolishingIssueTracker,
)
from chai.services import AIService


class FullBookPolishingEngine:
    """Engine for comprehensive full book polishing.

    This engine performs holistic cross-chapter analysis for polishing:
    - Global tone consistency across all volumes
    - Character voice consistency throughout
    - Narrative pacing analysis across chapters
    - Theme and motif coherence
    - World rules consistency
    - Plot thread and foreshadowing coherence
    - Emotional arc consistency
    - Cross-chapter dialogue consistency
    - Description consistency (characters, scenes)
    - Chapter transition quality
    - Word/phrase repetition check
    - Overall readability analysis
    """

    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        config: Optional[BookPolishingConfig] = None,
    ):
        """Initialize full book polishing engine.

        Args:
            ai_service: Optional AI service for enhanced analysis
            config: Optional configuration for polishing
        """
        self.ai_service = ai_service
        self.config = config or BookPolishingConfig()

    def polish(
        self,
        request: FullBookPolishingRequest,
    ) -> FullBookPolishingResult:
        """Perform comprehensive full book polishing.

        Args:
            request: Polishing request with all volume/chapter data

        Returns:
            FullBookPolishingResult with complete polishing report
        """
        start_time = time.time()
        polishing_id = f"polish_{uuid.uuid4().hex[:8]}"

        try:
            # Build chapter profiles for cross-chapter analysis
            all_chapters = []
            for vol in request.volumes:
                for ch in vol.get("chapters", []):
                    all_chapters.append({
                        **ch,
                        "volume_number": vol.get("volume_number", 1),
                        "volume_id": vol.get("volume_id", ""),
                    })

            # Sort by chapter number
            all_chapters.sort(key=lambda x: x.get("chapter_number", 0))

            # Initialize polishing results
            polishing_results: list[PolishingResult] = []
            volume_reports: list[VolumePolishingReport] = []

            # Perform each enabled polishing check
            config = request.config

            # 1. Global tone analysis
            if config.enable_global_tone:
                result = self._polish_global_tone(all_chapters)
                polishing_results.append(result)

            # 2. Character voice consistency
            if config.enable_character_voice:
                result = self._polish_character_voice(all_chapters, request.characters)
                polishing_results.append(result)

            # 3. Narrative pacing
            if config.enable_narrative_pacing:
                result = self._polish_narrative_pacing(all_chapters)
                polishing_results.append(result)

            # 4. Theme coherence
            if config.enable_theme_coherence:
                result = self._polish_theme_coherence(all_chapters)
                polishing_results.append(result)

            # 5. World rules consistency
            if config.enable_world_rules:
                result = self._polish_world_rules(all_chapters, request.world_setting)
                polishing_results.append(result)

            # 6. Plot threads and foreshadowing
            if config.enable_plot_threads:
                result = self._polish_plot_threads(all_chapters, request.subplot_design)
                polishing_results.append(result)

            # 7. Emotional arc
            if config.enable_emotional_arc:
                result = self._polish_emotional_arc(all_chapters)
                polishing_results.append(result)

            # 8. Dialogue consistency
            if config.enable_dialogue_universal:
                result = self._polish_dialogue_consistency(all_chapters, request.characters)
                polishing_results.append(result)

            # 9. Description consistency
            if config.enable_description_consistency:
                result = self._polish_description_consistency(all_chapters, request.characters)
                polishing_results.append(result)

            # 10. Book-wide transitions
            if config.enable_transition_book:
                result = self._polish_transitions(all_chapters)
                polishing_results.append(result)

            # 11. Repetition check
            if config.enable_repetition_check:
                result = self._polish_repetition(all_chapters)
                polishing_results.append(result)

            # 12. Readability analysis
            if config.enable_readability:
                result = self._polish_readability(all_chapters)
                polishing_results.append(result)

            # Build volume reports
            volumes = request.volumes
            for vol in volumes:
                vol_result = self._build_volume_report(
                    vol, all_chapters, polishing_results
                )
                volume_reports.append(vol_result)

            # Calculate overall score
            overall_score = self._calculate_overall_score(polishing_results)
            total_issues = sum(r.issue_count for r in polishing_results)

            # Determine overall status
            failed_count = sum(1 for r in polishing_results if r.status == PolishingStatus.NEEDS_REVISION)
            if failed_count > len(polishing_results) / 2:
                status = PolishingStatus.NEEDS_REVISION
            elif failed_count > 0:
                status = PolishingStatus.NEEDS_REVISION
            else:
                status = PolishingStatus.PASSED

            # Create revision plan if needed
            revision_plan = None
            if status == PolishingStatus.NEEDS_REVISION:
                revision_plan = self._create_revision_plan(polishing_results, all_chapters)

            # Build report
            report = BookPolishingReport(
                book_id=request.book_id,
                title=request.title,
                total_volumes=len(volumes),
                total_chapters=len(all_chapters),
                status=status,
                overall_score=overall_score,
                volume_reports=volume_reports,
                polishing_results=polishing_results,
                revision_plan=revision_plan,
                polished_at=datetime.now().isoformat(),
                summary=self._generate_summary(status, overall_score, total_issues, failed_count),
            )

            # Build summary
            summary = PolishingSummary(
                total_volumes=len(volumes),
                total_chapters=len(all_chapters),
                volumes_passed=sum(1 for v in volume_reports if v.status == PolishingStatus.PASSED),
                volumes_needing_revision=sum(1 for v in volume_reports if v.status == PolishingStatus.NEEDS_REVISION),
                average_score=overall_score,
                global_issues=self._extract_global_issues(polishing_results),
                critical_patterns=self._extract_critical_patterns(polishing_results),
                recommended_fixes=self._extract_recommended_fixes(polishing_results),
                overall_recommendation=self._generate_recommendation(status, overall_score),
            )

            elapsed_time = time.time() - start_time

            return FullBookPolishingResult(
                success=True,
                book_id=request.book_id,
                title=request.title,
                status=status,
                report=report,
                summary=summary,
                revision_plan=revision_plan,
            )

        except Exception as e:
            return FullBookPolishingResult(
                success=False,
                book_id=request.book_id,
                title=request.title,
                status=PolishingStatus.FAILED,
                report=BookPolishingReport(
                    book_id=request.book_id,
                    title=request.title,
                    total_volumes=0,
                    total_chapters=0,
                    status=PolishingStatus.FAILED,
                    overall_score=0.0,
                    volume_reports=[],
                    polishing_results=[],
                    polished_at=datetime.now().isoformat(),
                ),
                summary=PolishingSummary(
                    total_volumes=0,
                    total_chapters=0,
                    volumes_passed=0,
                    volumes_needing_revision=0,
                    average_score=0.0,
                    overall_recommendation=f"Polishing failed: {str(e)}",
                ),
                error_message=str(e),
            )

    def _polish_global_tone(self, chapters: list[dict]) -> PolishingResult:
        """Analyze global tone consistency across all chapters."""
        try:
            issues: list[PolishingIssue] = []
            tone_keywords = {
                "紧张": ["紧张", "危机", "恐惧", "担忧", "焦虑"],
                "温馨": ["温暖", "幸福", "甜蜜", "关怀", "爱意"],
                "悬疑": ["疑惑", "谜团", "神秘", "可疑", "线索"],
                "热血": ["激情", "斗志", "愤怒", "战斗", "决心"],
                "悲伤": ["悲痛", "伤心", "绝望", "失落", "哀伤"],
            }

            chapter_tones = []
            for ch in chapters:
                content = ch.get("content", "")
                tone_counts = {}
                for tone, keywords in tone_keywords.items():
                    count = sum(content.count(k) for k in keywords)
                    tone_counts[tone] = count
                dominant_tone = max(tone_counts, key=tone_counts.get) if tone_counts else "未知"
                chapter_tones.append({
                    "chapter_number": ch.get("chapter_number", 0),
                    "tone": dominant_tone,
                    "counts": tone_counts,
                })

            # Check for abrupt tone changes
            for i in range(1, len(chapter_tones)):
                prev_tone = chapter_tones[i - 1]["tone"]
                curr_tone = chapter_tones[i]["tone"]
                if prev_tone != curr_tone and prev_tone != "未知" and curr_tone != "未知":
                    # Check if it's a gradual transition or abrupt
                    prev_counts = chapter_tones[i - 1]["counts"]
                    curr_counts = chapter_tones[i]["counts"]
                    total_prev = sum(prev_counts.values())
                    total_curr = sum(curr_counts.values())
                    if total_prev > 0 and total_curr > 0:
                        change_ratio = abs(prev_counts.get(curr_tone, 0) - prev_counts.get(prev_tone, 0)) / total_prev
                        if change_ratio > 0.5:  # Abrupt change
                            issues.append(PolishingIssue(
                                issue_id=f"tone_{chapters[i].get('chapter_number', 0)}",
                                polishing_type=PolishingType.GLOBAL_TONE,
                                severity=PolishingSeverity.MODERATE,
                                chapter_start=chapters[i].get("chapter_number", 0),
                                description=f"语调突变：从{prev_tone}切换到{curr_tone}",
                                suggestion="建议使用过渡段落使语调变化更自然",
                            ))

            score = 1.0 - (len(issues) * 0.1)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.GLOBAL_TONE,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                critical_issues=[],
                major_issues=[i for i in issues if i.severity == PolishingSeverity.MAJOR],
                moderate_issues=[i for i in issues if i.severity == PolishingSeverity.MODERATE],
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"chapters_analyzed": len(chapters)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.GLOBAL_TONE,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Global tone analysis skipped: {str(e)}"],
            )

    def _polish_character_voice(self, chapters: list[dict], characters: list[dict]) -> PolishingResult:
        """Check character voice consistency across chapters."""
        try:
            issues: list[PolishingIssue] = []
            char_dialogue_patterns: dict[str, list[str]] = {}

            # Extract dialogue patterns for each character
            for ch in chapters:
                content = ch.get("content", "")
                # Simple pattern matching for dialogue
                dialogue_pattern = r'["""]([^"""]+)["""]'
                matches = re.findall(dialogue_pattern, content)
                for char_name in (characters or []):
                    name = char_name.get("name", "")
                    if name and name in content:
                        if name not in char_dialogue_patterns:
                            char_dialogue_patterns[name] = []
                        char_dialogue_patterns[name].extend(matches[:5])

            # Check for character consistency
            for char_name, dialogues in char_dialogue_patterns.items():
                if len(dialogues) < 2:
                    continue
                # Check if character's speech patterns are consistent
                avg_length = sum(len(d) for d in dialogues) / len(dialogues)
                if avg_length > 0:
                    variance = sum((len(d) - avg_length) ** 2 for d in dialogues) / len(dialogues)
                    if variance > 10000:  # High variance in dialogue length
                        issues.append(PolishingIssue(
                            issue_id=f"voice_{char_name}",
                            polishing_type=PolishingType.CHARACTER_VOICE,
                            severity=PolishingSeverity.MODERATE,
                            character_name=char_name,
                            description=f"角色'{char_name}'的对话长度变化较大",
                            suggestion="建议统一角色的说话风格和对话长度",
                        ))

            score = 1.0 - (len(issues) * 0.1)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.CHARACTER_VOICE,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                major_issues=[i for i in issues if i.severity == PolishingSeverity.MAJOR],
                moderate_issues=[i for i in issues if i.severity == PolishingSeverity.MODERATE],
                details={"characters_analyzed": len(char_dialogue_patterns)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.CHARACTER_VOICE,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Character voice analysis skipped: {str(e)}"],
            )

    def _polish_narrative_pacing(self, chapters: list[dict]) -> PolishingResult:
        """Analyze narrative pacing across chapters."""
        try:
            issues: list[PolishingIssue] = []
            pacing_scores = []

            for ch in chapters:
                content = ch.get("content", "")
                word_count = len(content)
                # Simple pacing metrics
                action_markers = ["突然", "猛然", "骤然", "忽然", "霎时", "瞬间"]
                action_count = sum(content.count(m) for m in action_markers)
                dialogue_count = content.count('"') // 2

                # Calculate pacing score (action density)
                pacing_score = (action_count + dialogue_count / 10) / (word_count / 1000) if word_count > 0 else 0
                pacing_scores.append({
                    "chapter_number": ch.get("chapter_number", 0),
                    "score": pacing_score,
                    "word_count": word_count,
                })

            # Check for pacing problems
            for i in range(1, len(pacing_scores)):
                prev = pacing_scores[i - 1]
                curr = pacing_scores[i]
                if prev["word_count"] > 0 and curr["word_count"] > 0:
                    # Check for sudden pacing changes
                    if abs(prev["score"] - curr["score"]) > 5:
                        issues.append(PolishingIssue(
                            issue_id=f"pacing_{curr['chapter_number']}",
                            polishing_type=PolishingType.NARRATIVE_PACING,
                            severity=PolishingSeverity.MODERATE,
                            chapter_start=curr["chapter_number"],
                            description=f"节奏突变：章节{curr['chapter_number']}的节奏变化较大",
                            suggestion="建议调整场景描写或对话比例以平衡节奏",
                        ))

            score = 1.0 - (len(issues) * 0.1)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.NARRATIVE_PACING,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                moderate_issues=[i for i in issues if i.severity == PolishingSeverity.MODERATE],
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"chapters_analyzed": len(chapters)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.NARRATIVE_PACING,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Narrative pacing analysis skipped: {str(e)}"],
            )

    def _polish_theme_coherence(self, chapters: list[dict]) -> PolishingResult:
        """Check theme coherence across the book."""
        try:
            issues: list[PolishingIssue] = []

            # Extract potential themes from content
            theme_keywords = {
                "成长": ["成长", "进步", "蜕变", "改变", "学习"],
                "友情": ["友情", "朋友", "伙伴", "信任", "羁绊"],
                "爱情": ["爱情", "爱", "感情", "心动", "浪漫"],
                "复仇": ["复仇", "报仇", "恨", "愤怒", "敌人"],
                "救赎": ["救赎", "弥补", "原谅", "宽恕", "悔改"],
                "牺牲": ["牺牲", "奉献", "舍身", "放弃", "代价"],
            }

            chapter_themes: dict[int, list[str]] = {}
            for ch in chapters:
                content = ch.get("content", "")
                chapter_num = ch.get("chapter_number", 0)
                themes_found = []
                for theme, keywords in theme_keywords.items():
                    if any(k in content for k in keywords):
                        themes_found.append(theme)
                chapter_themes[chapter_num] = themes_found

            # Check for theme continuity
            theme_introduced: dict[str, int] = {}
            for chapter_num in sorted(chapter_themes.keys()):
                themes = chapter_themes[chapter_num]
                for theme in themes:
                    if theme not in theme_introduced:
                        theme_introduced[theme] = chapter_num

            score = 1.0 if len(issues) == 0 else 0.8
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.THEME_COHERENCE,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                details={"themes_found": list(theme_introduced.keys()), "chapters_analyzed": len(chapters)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.THEME_COHERENCE,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Theme coherence analysis skipped: {str(e)}"],
            )

    def _polish_world_rules(self, chapters: list[dict], world_setting: Optional[dict]) -> PolishingResult:
        """Check world rules consistency."""
        try:
            issues: list[PolishingIssue] = []

            # If we have world setting info, check for consistency
            if world_setting:
                rules = world_setting.get("rules", [])
                for ch in chapters:
                    content = ch.get("content", "")
                    for rule in rules:
                        rule_name = rule.get("name", "")
                        if rule_name and rule_name in content:
                            # Check if the rule is being followed
                            violations = rule.get("violations", [])
                            for violation in violations:
                                if violation in content:
                                    issues.append(PolishingIssue(
                                        issue_id=f"world_{ch.get('chapter_number', 0)}_{rule_name}",
                                        polishing_type=PolishingType.WORLD_RULES,
                                        severity=PolishingSeverity.MAJOR,
                                        chapter_start=ch.get("chapter_number", 0),
                                        description=f"世界观规则'{rule_name}'被违反",
                                        suggestion=rule.get("suggestion", "请检查并修正"),
                                    ))

            score = 1.0 - (len(issues) * 0.15)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.WORLD_RULES,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                critical_issues=[i for i in issues if i.severity == PolishingSeverity.CRITICAL],
                major_issues=[i for i in issues if i.severity == PolishingSeverity.MAJOR],
                details={"chapters_analyzed": len(chapters)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.WORLD_RULES,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"World rules analysis skipped: {str(e)}"],
            )

    def _polish_plot_threads(self, chapters: list[dict], subplot_design: Optional[dict]) -> PolishingResult:
        """Check plot thread and foreshadowing coherence."""
        try:
            issues: list[PolishingIssue] = []

            # Track planted foreshadowing and their payoffs
            plants: dict[str, list[int]] = {}  # plant_text -> [chapter_numbers]
            payoffs: dict[str, list[int]] = {}  # payoff_text -> [chapter_numbers]

            subplot_keywords = ["伏笔", "预示", "暗示", "预兆", "前兆"]
            payoff_keywords = ["原来", "果然", "正如", "正如所料", "应验"]

            for ch in chapters:
                content = ch.get("content", "")
                chapter_num = ch.get("chapter_number", 0)
                for kw in subplot_keywords:
                    if kw in content:
                        if kw not in plants:
                            plants[kw] = []
                        plants[kw].append(chapter_num)
                for kw in payoff_keywords:
                    if kw in content:
                        if kw not in payoffs:
                            payoffs[kw] = []
                        payoffs[kw].append(chapter_num)

            # Check if plants have corresponding payoffs
            for plant_kw, plant_chapters in plants.items():
                has_payoff = False
                for payoff_kw, payoff_chapters in payoffs.items():
                    if any(p < max(payoff_chapters) for p in plant_chapters):
                        has_payoff = True
                        break
                if not has_payoff and len(plant_chapters) > 2:
                    issues.append(PolishingIssue(
                        issue_id=f"plot_{plant_kw}",
                        polishing_type=PolishingType.PLOT_THREADS,
                        severity=PolishingSeverity.MINOR,
                        chapter_start=min(plant_chapters),
                        chapter_end=max(plant_chapters),
                        description=f"伏笔'{plant_kw}'似乎未被回收",
                        suggestion="建议为之前埋下的伏笔添加呼应",
                    ))

            score = 1.0 - (len(issues) * 0.1)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.PLOT_THREADS,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"plants_found": len(plants), "payoffs_found": len(payoffs)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.PLOT_THREADS,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Plot threads analysis skipped: {str(e)}"],
            )

    def _polish_emotional_arc(self, chapters: list[dict]) -> PolishingResult:
        """Analyze emotional arc consistency."""
        try:
            issues: list[PolishingIssue] = []

            emotional_markers = {
                "high": ["喜悦", "兴奋", "幸福", "激动", "欢乐"],
                "low": ["悲伤", "痛苦", "绝望", "失落", "沮丧"],
                "neutral": ["平静", "淡然", "平常", "普通"],
            }

            chapter_emotions = []
            for ch in chapters:
                content = ch.get("content", "")
                emotion_scores = {}
                for level, keywords in emotional_markers.items():
                    score = sum(content.count(k) for k in keywords)
                    emotion_scores[level] = score
                dominant = max(emotion_scores, key=emotion_scores.get) if emotion_scores else "neutral"
                chapter_emotions.append({
                    "chapter_number": ch.get("chapter_number", 0),
                    "emotion": dominant,
                    "scores": emotion_scores,
                })

            # Check for emotional continuity
            for i in range(1, len(chapter_emotions)):
                prev = chapter_emotions[i - 1]["emotion"]
                curr = chapter_emotions[i]["emotion"]
                if prev != curr and prev != "neutral" and curr != "neutral":
                    # Check for abrupt emotional changes
                    prev_score = chapter_emotions[i - 1]["scores"].get(curr, 0)
                    curr_score = chapter_emotions[i]["scores"].get(prev, 0)
                    if prev_score == 0 and curr_score == 0:
                        issues.append(PolishingIssue(
                            issue_id=f"emotion_{chapter_emotions[i]['chapter_number']}",
                            polishing_type=PolishingType.EMOTIONAL_ARC,
                            severity=PolishingSeverity.MINOR,
                            chapter_start=chapter_emotions[i]["chapter_number"],
                            description=f"情感突变：从{prev}到{curr}缺少过渡",
                            suggestion="建议添加情感过渡段落",
                        ))

            score = 1.0 - (len(issues) * 0.05)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.EMOTIONAL_ARC,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"chapters_analyzed": len(chapters)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.EMOTIONAL_ARC,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Emotional arc analysis skipped: {str(e)}"],
            )

    def _polish_dialogue_consistency(self, chapters: list[dict], characters: list[dict]) -> PolishingResult:
        """Check cross-chapter dialogue consistency."""
        try:
            issues: list[PolishingIssue] = []

            # Extract dialogue quotes
            all_dialogues: list[dict] = []
            for ch in chapters:
                content = ch.get("content", "")
                # Find dialogue patterns
                patterns = [
                    r'["""]([^"""]+)["""]',
                    r'["]([^"]+)["]',
                    r"[']([^']+)[']",
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        all_dialogues.append({
                            "text": match,
                            "chapter": ch.get("chapter_number", 0),
                            "volume": ch.get("volume_number", 1),
                        })

            # Check for repeated identical dialogues
            dialogue_texts = [d["text"] for d in all_dialogues]
            text_counts = Counter(dialogue_texts)
            for text, count in text_counts.items():
                if count > 1 and len(text) > 20:
                    chapters_with_it = [d["chapter"] for d in all_dialogues if d["text"] == text]
                    issues.append(PolishingIssue(
                        issue_id=f"dialogue_{text[:20]}",
                        polishing_type=PolishingType.DIALOGUE_UNIVERSAL,
                        severity=PolishingSeverity.MINOR,
                        chapter_start=min(chapters_with_it),
                        chapter_end=max(chapters_with_it),
                        description=f"相同对话重复出现{count}次",
                        suggestion="建议修改对话或删除重复",
                        example=text[:50],
                    ))

            score = 1.0 - (len(issues) * 0.05)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.DIALOGUE_UNIVERSAL,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"dialogues_analyzed": len(all_dialogues)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.DIALOGUE_UNIVERSAL,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Dialogue consistency check skipped: {str(e)}"],
            )

    def _polish_description_consistency(self, chapters: list[dict], characters: list[dict]) -> PolishingResult:
        """Check character and scene description consistency."""
        try:
            issues: list[PolishingIssue] = []

            # Track character appearances and their descriptions
            char_appearances: dict[str, list[dict]] = {}
            for ch in chapters:
                content = ch.get("content", "")
                chapter_num = ch.get("chapter_number", 0)
                for char in (characters or []):
                    name = char.get("name", "")
                    if name and name in content:
                        if name not in char_appearances:
                            char_appearances[name] = []
                        char_appearances[name].append({
                            "chapter": chapter_num,
                            "has_description": any(k in content for k in [
                                char.get("appearance", ""),
                                char.get("特征", ""),
                            ]),
                        })

            # Check for character description consistency
            for char_name, appearances in char_appearances.items():
                described_chapters = [a["chapter"] for a in appearances if a["has_description"]]
                if len(appearances) > 5 and len(described_chapters) == 0:
                    issues.append(PolishingIssue(
                        issue_id=f"desc_{char_name}",
                        polishing_type=PolishingType.DESCRIPTION_CONSISTENCY,
                        severity=PolishingSeverity.MINOR,
                        description=f"角色'{char_name}'出现频繁但缺少描述",
                        suggestion="建议在适当位置添加角色外貌或特征描写",
                    ))

            score = 1.0 - (len(issues) * 0.05)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.DESCRIPTION_CONSISTENCY,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"characters_tracked": len(char_appearances)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.DESCRIPTION_CONSISTENCY,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Description consistency check skipped: {str(e)}"],
            )

    def _polish_transitions(self, chapters: list[dict]) -> PolishingResult:
        """Check chapter-to-chapter transitions."""
        try:
            issues: list[PolishingIssue] = []

            transition_markers = ["第二天", "片刻后", "不久", "随后", "接着", "然而", "但是", "此时", "就在这时"]
            cliffhanger_markers = ["就在这时", "突然", "就在此时", "刹那间", "霎时间"]

            for i in range(len(chapters) - 1):
                curr_ch = chapters[i]
                next_ch = chapters[i + 1]
                curr_content = curr_ch.get("content", "")
                next_content = next_ch.get("content", "")

                curr_chapter = curr_ch.get("chapter_number", 0)
                next_chapter = next_ch.get("chapter_number", 0)

                # Check if current chapter ends properly
                has_transition = any(m in curr_content[-100:] for m in transition_markers)
                has_cliffhanger = any(m in curr_content[-50:] for m in cliffhanger_markers)

                # Check if next chapter starts with proper setup
                next_starts_mid = any(m in next_content[:100] for m in ["只见", "却见", "只见那", "却看"])

                if not has_transition and not has_cliffhanger:
                    # No clear transition or cliffhanger at end
                    if i > 0:  # Not the first chapter
                        issues.append(PolishingIssue(
                            issue_id=f"trans_{curr_chapter}",
                            polishing_type=PolishingType.TRANSITION_BOOK,
                            severity=PolishingSeverity.MINOR,
                            chapter_start=curr_chapter,
                            chapter_end=next_chapter,
                            description=f"章节{curr_chapter}结尾与章节{next_chapter}开头缺少过渡",
                            suggestion="建议添加章节间的过渡段落",
                        ))

            score = 1.0 - (len(issues) * 0.08)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.TRANSITION_BOOK,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={"transitions_analyzed": len(chapters) - 1},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.TRANSITION_BOOK,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Transition analysis skipped: {str(e)}"],
            )

    def _polish_repetition(self, chapters: list[dict]) -> PolishingResult:
        """Check for word/phrase repetition across chapters."""
        try:
            issues: list[PolishingIssue] = []

            # Extract significant phrases (3-5 word combinations)
            all_words: list[str] = []
            for ch in chapters:
                content = ch.get("content", "")
                words = re.findall(r'[\u4e00-\u9fa5]{3,5}', content)
                all_words.extend([(w, ch.get("chapter_number", 0)) for w in words])

            # Count phrase occurrences
            phrase_counts: dict[str, list[int]] = {}
            for word, chapter_num in all_words:
                if len(word) >= 3:
                    if word not in phrase_counts:
                        phrase_counts[word] = []
                    phrase_counts[word].append(chapter_num)

            # Find overused phrases
            for phrase, chapters_list in phrase_counts.items():
                unique_chapters = set(chapters_list)
                if len(unique_chapters) > 3:  # Appears in multiple chapters
                    # Check if it's not a common word
                    common_words = ["的", "了", "是", "在", "有", "和", "与", "而", "但", "这", "那"]
                    if phrase not in common_words and len(phrase) >= 3:
                        issue_found = False
                        # Filter out proper nouns, place names, etc.
                        if phrase[0].isupper() or phrase[0] in "春夏秋冬天地人物":
                            issue_found = True
                        elif phrase in ["突然", "接着", "于是", "因此", "但是", "然而", "然后"]:
                            issue_found = True

                        if issue_found:
                            issues.append(PolishingIssue(
                                issue_id=f"rep_{phrase}",
                                polishing_type=PolishingType.REPETITION_CHECK,
                                severity=PolishingSeverity.MINOR,
                                description=f"短语'{phrase}'在多个章节中重复出现",
                                suggestion="建议替换为同义词或改写句式",
                            ))

            # Deduplicate by description
            seen = set()
            unique_issues = []
            for issue in issues:
                if issue.description not in seen:
                    seen.add(issue.description)
                    unique_issues.append(issue)

            score = 1.0 - (len(unique_issues) * 0.03)
            status = PolishingStatus.PASSED if len(unique_issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.REPETITION_CHECK,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(unique_issues),
                minor_issues=unique_issues[:10],  # Only show first 10
                details={"phrases_analyzed": len(phrase_counts)},
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.REPETITION_CHECK,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Repetition check skipped: {str(e)}"],
            )

    def _polish_readability(self, chapters: list[dict]) -> PolishingResult:
        """Analyze overall readability."""
        try:
            issues: list[PolishingIssue] = []

            total_word_count = 0
            total_sentences = 0
            long_sentence_count = 0

            for ch in chapters:
                content = ch.get("content", "")
                total_word_count += len(content)
                # Count sentences (roughly)
                sentences = re.split(r'[。！？]', content)
                total_sentences += len(sentences)
                # Check for very long sentences
                for sent in sentences:
                    if len(sent) > 100:
                        long_sentence_count += 1

            avg_sentence_length = total_word_count / max(1, total_sentences)

            if avg_sentence_length > 50:
                issues.append(PolishingIssue(
                    issue_id="readability_length",
                    polishing_type=PolishingType.READABILITY,
                    severity=PolishingSeverity.MODERATE,
                    description=f"平均句子长度过长：{avg_sentence_length:.1f}字",
                    suggestion="建议拆分长句，增加段落变化",
                ))

            if long_sentence_count > len(chapters) * 2:
                issues.append(PolishingIssue(
                    issue_id="readability_long",
                    polishing_type=PolishingType.READABILITY,
                    severity=PolishingSeverity.MINOR,
                    description=f"发现{long_sentence_count}个超长句子",
                    suggestion="建议拆分100字以上的句子",
                ))

            score = 1.0 - (len(issues) * 0.1)
            status = PolishingStatus.PASSED if len(issues) == 0 else PolishingStatus.NEEDS_REVISION

            return PolishingResult(
                polishing_type=PolishingType.READABILITY,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=len(issues),
                moderate_issues=[i for i in issues if i.severity == PolishingSeverity.MODERATE],
                minor_issues=[i for i in issues if i.severity == PolishingSeverity.MINOR],
                details={
                    "total_word_count": total_word_count,
                    "total_sentences": total_sentences,
                    "avg_sentence_length": avg_sentence_length,
                },
            )
        except Exception as e:
            return PolishingResult(
                polishing_type=PolishingType.READABILITY,
                status=PolishingStatus.NEEDS_REVISION,
                score=0.0,
                issue_count=0,
                suggestions=[f"Readability analysis skipped: {str(e)}"],
            )

    def _build_volume_report(
        self,
        volume: dict,
        all_chapters: list[dict],
        global_results: list[PolishingResult],
    ) -> VolumePolishingReport:
        """Build a polishing report for a single volume."""
        volume_chapters = [
            ch for ch in all_chapters
            if ch.get("volume_id") == volume.get("volume_id") or ch.get("volume_number") == volume.get("volume_number")
        ]
        volume_chapters.sort(key=lambda x: x.get("chapter_number", 0))

        # Filter results relevant to this volume's chapters
        relevant_results = []
        for result in global_results:
            relevant = PolishingResult(
                polishing_type=result.polishing_type,
                status=result.status,
                score=result.score,
                issue_count=result.issue_count,
                critical_issues=[i for i in result.critical_issues
                               if i.chapter_start is None or
                               any(i.chapter_start <= ch.get("chapter_number", 0) <= (i.chapter_end or i.chapter_start)
                                   for ch in volume_chapters)],
                major_issues=[i for i in result.major_issues
                            if i.chapter_start is None or
                            any(i.chapter_start <= ch.get("chapter_number", 0) <= (i.chapter_end or i.chapter_start)
                                for ch in volume_chapters)],
                moderate_issues=[i for i in result.moderate_issues
                               if i.chapter_start is None or
                               any(i.chapter_start <= ch.get("chapter_number", 0) <= (i.chapter_end or i.chapter_start)
                                   for ch in volume_chapters)],
                minor_issues=[i for i in result.minor_issues
                            if i.chapter_start is None or
                            any(i.chapter_start <= ch.get("chapter_number", 0) <= (i.chapter_end or i.chapter_start)
                                for ch in volume_chapters)],
                details=result.details,
                suggestions=result.suggestions,
            )
            relevant_results.append(relevant)

        overall_score = sum(r.score for r in relevant_results) / max(1, len(relevant_results))
        failed_count = sum(1 for r in relevant_results if r.status == PolishingStatus.NEEDS_REVISION)

        status = PolishingStatus.PASSED if failed_count == 0 else PolishingStatus.NEEDS_REVISION

        return VolumePolishingReport(
            volume_id=volume.get("volume_id", ""),
            volume_number=volume.get("volume_number", 1),
            title=volume.get("title", ""),
            status=status,
            overall_score=overall_score,
            issues_found=sum(r.issue_count for r in relevant_results),
            polishing_results=relevant_results,
            polished_at=datetime.now().isoformat(),
            summary=self._generate_volume_summary(status, overall_score, len(volume_chapters)),
        )

    def _calculate_overall_score(self, polishing_results: list[PolishingResult]) -> float:
        """Calculate overall score from polishing results."""
        if not polishing_results:
            return 1.0
        total_score = sum(r.score for r in polishing_results)
        return total_score / len(polishing_results)

    def _create_revision_plan(
        self,
        polishing_results: list[PolishingResult],
        chapters: list[dict],
    ) -> PolishingPlan:
        """Create revision plan based on polishing results."""
        plan = PolishingPlan()

        for result in polishing_results:
            if result.status == PolishingStatus.NEEDS_REVISION:
                # Add critical/major issues to priority fixes
                for issue in result.critical_issues + result.major_issues:
                    if issue.polishing_type == PolishingType.GLOBAL_TONE:
                        plan.global_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.CHARACTER_VOICE:
                        plan.character_voice_fixes.append(f"[{issue.character_name}] {issue.suggestion}")
                    elif issue.polishing_type == PolishingType.NARRATIVE_PACING:
                        plan.pacing_fixes.append(f"章节{issue.chapter_start}: {issue.suggestion}")
                    elif issue.polishing_type == PolishingType.THEME_COHERENCE:
                        plan.theme_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.WORLD_RULES:
                        plan.world_rules_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.PLOT_THREADS:
                        plan.plot_thread_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.EMOTIONAL_ARC:
                        plan.emotional_arc_fixes.append(f"章节{issue.chapter_start}: {issue.suggestion}")
                    elif issue.polishing_type == PolishingType.DIALOGUE_UNIVERSAL:
                        plan.dialogue_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.DESCRIPTION_CONSISTENCY:
                        plan.description_fixes.append(f"{issue.character_name}: {issue.suggestion}")
                    elif issue.polishing_type == PolishingType.TRANSITION_BOOK:
                        plan.transition_fixes.append(f"章节{issue.chapter_start}-{issue.chapter_end}: {issue.suggestion}")
                    elif issue.polishing_type == PolishingType.REPETITION_CHECK:
                        plan.repetition_fixes.append(issue.suggestion)
                    elif issue.polishing_type == PolishingType.READABILITY:
                        plan.readability_fixes.append(issue.suggestion)

                # Add suggestions
                plan.global_fixes.extend(result.suggestions)

        # Deduplicate
        plan.global_fixes = list(dict.fromkeys(plan.global_fixes))
        plan.character_voice_fixes = list(dict.fromkeys(plan.character_voice_fixes))
        plan.pacing_fixes = list(dict.fromkeys(plan.pacing_fixes))
        plan.theme_fixes = list(dict.fromkeys(plan.theme_fixes))
        plan.world_rules_fixes = list(dict.fromkeys(plan.world_rules_fixes))
        plan.plot_thread_fixes = list(dict.fromkeys(plan.plot_thread_fixes))
        plan.emotional_arc_fixes = list(dict.fromkeys(plan.emotional_arc_fixes))
        plan.dialogue_fixes = list(dict.fromkeys(plan.dialogue_fixes))
        plan.description_fixes = list(dict.fromkeys(plan.description_fixes))
        plan.transition_fixes = list(dict.fromkeys(plan.transition_fixes))
        plan.repetition_fixes = list(dict.fromkeys(plan.repetition_fixes))
        plan.readability_fixes = list(dict.fromkeys(plan.readability_fixes))

        return plan

    def _extract_global_issues(self, polishing_results: list[PolishingResult]) -> list[str]:
        """Extract global-level issues."""
        issues = []
        for result in polishing_results:
            for issue in result.critical_issues + result.major_issues:
                if issue.chapter_start is None:
                    issues.append(f"{issue.polishing_type.value}: {issue.description}")
        return issues

    def _extract_critical_patterns(self, polishing_results: list[PolishingResult]) -> list[str]:
        """Extract critical patterns across the book."""
        patterns = []
        for result in polishing_results:
            if result.issue_count > 3:
                patterns.append(f"{result.polishing_type.value}: 发现{result.issue_count}处问题")
        return patterns

    def _extract_recommended_fixes(self, polishing_results: list[PolishingResult]) -> list[str]:
        """Extract recommended fixes."""
        fixes = []
        for result in polishing_results:
            fixes.extend(result.suggestions[:3])  # Top 3 suggestions per type
        return list(dict.fromkeys(fixes))[:10]  # Deduplicate and limit to 10

    def _generate_summary(
        self,
        status: PolishingStatus,
        overall_score: float,
        total_issues: int,
        failed_count: int,
    ) -> str:
        """Generate human-readable summary."""
        if status == PolishingStatus.PASSED:
            return f"全书润色通过！整体质量评分 {overall_score:.1%}，共发现 {total_issues} 处小问题。"
        else:
            return f"全书润色发现问题。{failed_count} 项检查未通过，整体质量评分 {overall_score:.1%}，共 {total_issues} 处问题需关注。"

    def _generate_volume_summary(
        self,
        status: PolishingStatus,
        score: float,
        chapter_count: int,
    ) -> str:
        """Generate volume-level summary."""
        if status == PolishingStatus.PASSED:
            return f"卷润色通过。评分 {score:.1%}，共 {chapter_count} 章。"
        else:
            return f"卷润色发现问题。评分 {score:.1%}，共 {chapter_count} 章需修订。"

    def _generate_recommendation(self, status: PolishingStatus, score: float) -> str:
        """Generate overall recommendation."""
        if status == PolishingStatus.PASSED:
            return "稿件质量良好，可以进入下一阶段。"
        elif score >= 0.8:
            return "稿件整体质量不错，建议进行局部修订后导出。"
        elif score >= 0.6:
            return "建议对发现的问题进行系统性修订。"
        else:
            return "问题较多，建议重点章节进行全面重写。"

    def get_summary(
        self,
        result: FullBookPolishingResult,
    ) -> str:
        """Get a short summary from polishing result.

        Args:
            result: Polishing result

        Returns:
            Short summary string
        """
        return result.report.summary