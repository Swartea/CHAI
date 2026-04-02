"""Chapter self-check engine for quality assurance after chapter completion.

This engine orchestrates multiple check engines to perform comprehensive self-checks
on a chapter after it is written, ensuring quality before proceeding to the next chapter.
"""

import uuid
import time
from datetime import datetime
from typing import Optional

from chai.models.chapter_self_check import (
    SelfCheckStatus,
    SelfCheckType,
    SelfCheckSeverity,
    SelfCheckResult,
    ChapterSelfCheckProfile,
    ChapterSelfCheckConfig,
    SelfCheckPlan,
    ChapterSelfCheckReport,
    NovelSelfCheckSummary,
    ChapterSelfCheckRequest,
    ChapterSelfCheckResult,
)
from chai.engines.grammar_check_engine import GrammarCheckEngine
from chai.engines.sentence_quality_engine import SentenceQualityEngine
from chai.engines.dialogue_tag_check_engine import DialogueTagCheckEngine
from chai.engines.punctuation_check_engine import PunctuationCheckEngine
from chai.engines.chapter_word_count_engine import ChapterWordCountEngine
from chai.engines.foreshadowing_check_engine import ForeshadowingCheckEngine
from chai.engines.chapter_transition_engine import ChapterTransitionEngine
from chai.engines.style_engine import StyleEngine
from chai.engines.tone_unification_engine import ToneUnificationEngine
from chai.engines.description_density_engine import DescriptionDensityEngine
from chai.engines.dialogue_naturalness_engine import DialogueNaturalnessEngine
from chai.engines.scene_vividness_engine import SceneVividnessEngine
from chai.engines.plot_logic_engine import PlotLogicEngine
from chai.engines.payoff_completeness_engine import PayoffCompletenessEngine
from chai.models import Novel, Chapter
from chai.services import AIService


class ChapterSelfCheckEngine:
    """Engine for comprehensive self-check after chapter completion.

    This engine orchestrates multiple check engines to validate chapter quality:
    - Grammar and typo check (GrammarCheckEngine)
    - Sentence quality check (SentenceQualityEngine)
    - Dialogue tag check (DialogueTagCheckEngine)
    - Punctuation check (PunctuationCheckEngine)
    - Word count check (ChapterWordCountEngine)
    - Foreshadowing check (ForeshadowingCheckEngine)
    - Transition check (ChapterTransitionEngine)
    - Style consistency check (StyleEngine)
    - Tone consistency check (ToneUnificationEngine)
    - Description density check (DescriptionDensityEngine)
    - Dialogue naturalness check (DialogueNaturalnessEngine)
    - Scene vividness check (SceneVividnessEngine)
    - Plot logic check (PlotLogicEngine)
    - Payoff completeness check (PayoffCompletenessEngine)
    """

    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        config: Optional[ChapterSelfCheckConfig] = None,
    ):
        """Initialize chapter self-check engine.

        Args:
            ai_service: Optional AI service for enhanced checks
            config: Optional configuration for self-check
        """
        self.ai_service = ai_service
        self.config = config or ChapterSelfCheckConfig()

        # Initialize check engines (only those that don't require AI service)
        self.word_count_engine = ChapterWordCountEngine(
            min_target=self.config.min_word_count,
            max_target=self.config.max_word_count,
        )

        # AI-dependent engines - only initialize if AI service is available
        if ai_service:
            self.grammar_engine = GrammarCheckEngine(ai_service)
            self.sentence_quality_engine = SentenceQualityEngine(ai_service)
            self.dialogue_tag_engine = DialogueTagCheckEngine(ai_service)
            self.punctuation_engine = PunctuationCheckEngine(ai_service)
            self.foreshadowing_engine = ForeshadowingCheckEngine(ai_service)
            self.transition_engine = ChapterTransitionEngine(ai_service)
            self.style_engine = StyleEngine(ai_service)
            self.tone_engine = ToneUnificationEngine(ai_service)
            self.description_density_engine = DescriptionDensityEngine(ai_service)
            self.dialogue_naturalness_engine = DialogueNaturalnessEngine(ai_service)
            self.scene_vividness_engine = SceneVividnessEngine(ai_service)
            self.plot_logic_engine = PlotLogicEngine(ai_service)
            self.payoff_engine = PayoffCompletenessEngine(ai_service)
        else:
            # When no AI service is available, use basic rule-based checks
            self.grammar_engine = None
            self.sentence_quality_engine = None
            self.dialogue_tag_engine = None
            self.punctuation_engine = None
            self.foreshadowing_engine = None
            self.transition_engine = None
            self.style_engine = None
            self.tone_engine = None
            self.description_density_engine = None
            self.dialogue_naturalness_engine = None
            self.scene_vividness_engine = SceneVividnessEngine()
            self.plot_logic_engine = None
            self.payoff_engine = None

    def check_chapter(
        self,
        request: ChapterSelfCheckRequest,
    ) -> ChapterSelfCheckResult:
        """Perform comprehensive self-check on a chapter.

        Args:
            request: Self-check request with chapter content and config

        Returns:
            ChapterSelfCheckResult with all check results
        """
        start_time = time.time()
        check_id = f"check_{uuid.uuid4().hex[:8]}"

        try:
            # Initialize check results
            check_results: list[SelfCheckResult] = []
            checks_passed = 0
            checks_failed = 0
            checks_warning = 0

            # Perform each enabled check
            config = request.config

            # 1. Grammar check
            if config.enable_grammar and self.grammar_engine:
                result = self._check_grammar(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 2. Sentence quality check
            if config.enable_sentence_quality and self.sentence_quality_engine:
                result = self._check_sentence_quality(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 3. Dialogue tag check
            if config.enable_dialogue_tag and self.dialogue_tag_engine:
                result = self._check_dialogue_tag(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 4. Punctuation check
            if config.enable_punctuation and self.punctuation_engine:
                result = self._check_punctuation(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 5. Word count check
            if config.enable_word_count:
                result = self._check_word_count(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 6. Foreshadowing check
            if config.enable_foreshadowing and self.foreshadowing_engine:
                result = self._check_foreshadowing(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 7. Transition check
            if config.enable_transition and self.transition_engine:
                result = self._check_transition(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 8. Style check
            if config.enable_style and self.style_engine:
                result = self._check_style(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 9. Tone check
            if config.enable_tone and self.tone_engine:
                result = self._check_tone(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 10. Description density check
            if config.enable_description_density and self.description_density_engine:
                result = self._check_description_density(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 11. Dialogue naturalness check
            if config.enable_dialogue_naturalness and self.dialogue_naturalness_engine:
                result = self._check_dialogue_naturalness(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 12. Scene vividness check
            if config.enable_scene_vividness and self.scene_vividness_engine:
                result = self._check_scene_vividness(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 13. Plot logic check
            if config.enable_plot_logic and self.plot_logic_engine:
                result = self._check_plot_logic(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # 14. Payoff completeness check
            if config.enable_payoff_completeness and self.payoff_engine:
                result = self._check_payoff_completeness(request)
                check_results.append(result)
                self._update_counts(result.status, checks_passed, checks_failed, checks_warning)

            # Calculate overall score and status
            overall_score = self._calculate_overall_score(check_results)
            total_issues = sum(r.issue_count for r in check_results)

            # Determine overall status
            if checks_failed > 0:
                status = SelfCheckStatus.FAILED
            elif checks_warning > 0:
                status = SelfCheckStatus.WARNING
            else:
                status = SelfCheckStatus.PASSED

            # Create profile
            profile = ChapterSelfCheckProfile(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                status=status,
                overall_score=overall_score,
                checks_passed=checks_passed,
                checks_failed=checks_failed,
                checks_warning=checks_warning,
                total_issues=total_issues,
                check_results=check_results,
                checked_at=datetime.now().isoformat(),
            )

            # Create revision plan if needed
            revision_plan = None
            if status in (SelfCheckStatus.FAILED, SelfCheckStatus.WARNING):
                revision_plan = self._create_revision_plan(check_results, request)

            # Create report
            report = ChapterSelfCheckReport(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                status=status,
                overall_score=overall_score,
                check_results=check_results,
                revision_plan=revision_plan,
                checked_at=datetime.now().isoformat(),
                summary=self._generate_summary(status, overall_score, total_issues, checks_failed, checks_warning),
            )

            elapsed_time = time.time() - start_time

            return ChapterSelfCheckResult(
                success=True,
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                status=status,
                profile=profile,
                report=report,
                revision_plan=revision_plan,
            )

        except Exception as e:
            return ChapterSelfCheckResult(
                success=False,
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                status=SelfCheckStatus.FAILED,
                profile=ChapterSelfCheckProfile(
                    chapter_id=request.chapter_id,
                    chapter_number=request.chapter_number,
                    title=request.title,
                    status=SelfCheckStatus.FAILED,
                ),
                report=ChapterSelfCheckReport(
                    chapter_id=request.chapter_id,
                    chapter_number=request.chapter_number,
                    title=request.title,
                    status=SelfCheckStatus.FAILED,
                    overall_score=0.0,
                    check_results=[],
                    checked_at=datetime.now().isoformat(),
                ),
                error_message=str(e),
            )

    def _check_grammar(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check grammar and typos."""
        try:
            # Create minimal Novel and Chapter for grammar check
            chapter = Chapter(
                id=request.chapter_id,
                number=request.chapter_number,
                title=request.title,
                content=request.content,
            )
            novel = Novel(
                id=f"novel_{request.chapter_id}",
                title="temp",
                chapters=[chapter],
            )

            analysis = self.grammar_engine.check_novel_grammar(novel)

            # Convert to SelfCheckResult
            critical_issues = [e.description for e in analysis.errors
                             if e.severity.value == "critical"]
            major_issues = [e.description for e in analysis.errors
                           if e.severity.value == "major"]
            moderate_issues = [e.description for e in analysis.errors
                             if e.severity.value == "minor"]
            minor_issues = [e.description for e in analysis.errors
                          if e.severity.value == "typographical"]

            issue_count = len(analysis.errors)
            score = 1.0 - (issue_count / max(100, len(request.content)))

            status = SelfCheckStatus.PASSED
            if critical_issues:
                status = SelfCheckStatus.FAILED
            elif major_issues:
                status = SelfCheckStatus.FAILED
            elif moderate_issues or minor_issues:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.GRAMMAR,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=critical_issues[:5],
                major_issues=major_issues[:10],
                moderate_issues=moderate_issues[:10],
                minor_issues=minor_issues[:10],
                details={"total_errors": len(analysis.errors)},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.GRAMMAR,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Grammar check skipped: {str(e)}"],
            )

    def _check_sentence_quality(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check sentence quality (disease sentences, redundancy)."""
        try:
            analysis = self.sentence_quality_engine.check_chapter_quality(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            critical_issues = [i.description for i in analysis.issues
                             if i.severity.value == "critical"]
            major_issues = [i.description for i in analysis.issues
                           if i.severity.value == "major"]
            moderate_issues = [i.description for i in analysis.issues
                             if i.severity.value == "moderate"]
            minor_issues = [i.description for i in analysis.issues
                          if i.severity.value == "minor"]

            issue_count = len(analysis.issues)
            score = 1.0 - (issue_count / max(100, len(request.content)))

            status = SelfCheckStatus.PASSED
            if critical_issues or major_issues:
                status = SelfCheckStatus.FAILED
            elif moderate_issues or minor_issues:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.SENTENCE_QUALITY,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=critical_issues[:5],
                major_issues=major_issues[:10],
                moderate_issues=moderate_issues[:10],
                minor_issues=minor_issues[:10],
                details={"disease_count": analysis.disease_count, "redundancy_count": analysis.redundancy_count},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.SENTENCE_QUALITY,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Sentence quality check skipped: {str(e)}"],
            )

    def _check_dialogue_tag(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check dialogue tag standardization."""
        try:
            result = self.dialogue_tag_engine.check_chapter_dialogue_tags(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            critical_issues = [i.description for i in result.issues
                             if i.severity.value == "critical"]
            major_issues = [i.description for i in result.issues
                           if i.severity.value == "major"]
            moderate_issues = [i.description for i in result.issues
                             if i.severity.value == "moderate"]
            minor_issues = [i.description for i in result.issues
                          if i.severity.value == "minor"]

            issue_count = len(result.issues)
            score = 1.0 - (issue_count / max(10, result.total_dialogues))

            status = SelfCheckStatus.PASSED
            if critical_issues or major_issues:
                status = SelfCheckStatus.FAILED
            elif moderate_issues or minor_issues:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.DIALOGUE_TAG,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=critical_issues[:5],
                major_issues=major_issues[:10],
                moderate_issues=moderate_issues[:10],
                minor_issues=minor_issues[:10],
                details={"total_dialogues": result.total_dialogues, "consistent_dialogues": result.consistent_dialogues},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.DIALOGUE_TAG,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Dialogue tag check skipped: {str(e)}"],
            )

    def _check_punctuation(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check punctuation standardization."""
        try:
            result = self.punctuation_engine.check_chapter_punctuation(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            critical_issues = [i.description for i in result.issues
                             if i.severity.value == "critical"]
            major_issues = [i.description for i in result.issues
                           if i.severity.value == "major"]
            moderate_issues = [i.description for i in result.issues
                             if i.severity.value == "moderate"]
            minor_issues = [i.description for i in result.issues
                          if i.severity.value == "minor"]

            issue_count = len(result.issues)
            score = 1.0 - (issue_count / max(100, len(request.content)))

            status = SelfCheckStatus.PASSED
            if critical_issues or major_issues:
                status = SelfCheckStatus.FAILED
            elif moderate_issues or minor_issues:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.PUNCTUATION,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=critical_issues[:5],
                major_issues=major_issues[:10],
                moderate_issues=moderate_issues[:10],
                minor_issues=minor_issues[:10],
                details={"total_punctuation": result.total_punctuation, "correct_punctuation": result.correct_punctuation},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.PUNCTUATION,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Punctuation check skipped: {str(e)}"],
            )

    def _check_word_count(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check word count validation."""
        try:
            profile = self.word_count_engine.analyze_chapter(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
                min_target=request.config.min_word_count,
                max_target=request.config.max_word_count,
            )

            issue_count = 1 if not profile.is_within_target else 0
            score = 1.0 if profile.is_within_target else 0.5

            status = SelfCheckStatus.PASSED
            if not profile.is_within_target:
                if profile.severity.value == "severe":
                    status = SelfCheckStatus.FAILED
                else:
                    status = SelfCheckStatus.WARNING

            recommendations = []
            if not profile.is_within_target:
                issue = self.word_count_engine.identify_issue(profile)
                if issue:
                    recommendations.append(issue.recommendation)

            return SelfCheckResult(
                check_type=SelfCheckType.WORD_COUNT,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=[],
                major_issues=[f"字数{profile.actual_word_count}不在{profile.min_target}-{profile.max_target}范围内"] if issue_count > 0 else [],
                moderate_issues=[],
                minor_issues=[],
                recommendations=recommendations,
                details={
                    "actual_count": profile.actual_word_count,
                    "min_target": profile.min_target,
                    "max_target": profile.max_target,
                    "is_within_target": profile.is_within_target,
                },
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.WORD_COUNT,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Word count check skipped: {str(e)}"],
            )

    def _check_foreshadowing(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check foreshadowing consistency."""
        try:
            result = self.foreshadowing_engine.check_chapter_foreshadowing(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
                previous_chapter_content=request.previous_chapter_content,
                next_chapter_content=request.next_chapter_content,
            )

            issue_count = len(result.issues)
            score = 1.0 - (issue_count / 10.0)

            status = SelfCheckStatus.PASSED
            if issue_count > 3:
                status = SelfCheckStatus.FAILED
            elif issue_count > 0:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.FORESHADOWING,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=[],
                major_issues=[i.description for i in result.issues if i.severity.value == "major"][:5],
                moderate_issues=[i.description for i in result.issues if i.severity.value == "moderate"][:5],
                minor_issues=[i.description for i in result.issues if i.severity.value == "minor"][:5],
                details={"plants_found": result.plants_found, "callbacks_found": result.callbacks_found},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.FORESHADOWING,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Foreshadowing check skipped: {str(e)}"],
            )

    def _check_transition(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check chapter transition quality."""
        try:
            # Analyze transition from previous chapter
            if request.previous_chapter_content:
                prev_analysis = self.transition_engine.analyze_chapter_ending(
                    chapter_id=f"{request.chapter_id}_prev",
                    chapter_number=request.chapter_number - 1,
                    title="Previous Chapter",
                    content=request.previous_chapter_content,
                )
            else:
                prev_analysis = None

            # Analyze transition to next chapter
            if request.next_chapter_content:
                next_analysis = self.transition_engine.analyze_chapter_opening(
                    chapter_id=f"{request.chapter_id}_next",
                    chapter_number=request.chapter_number + 1,
                    title="Next Chapter",
                    content=request.next_chapter_content,
                )
            else:
                next_analysis = None

            # Analyze this chapter's opening and ending
            opening_analysis = self.transition_engine.analyze_chapter_opening(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )
            ending_analysis = self.transition_engine.analyze_chapter_ending(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            # Calculate transition quality
            issues = []
            if opening_analysis.quality.value == "poor":
                issues.append("章节开头过渡质量较差")
            if ending_analysis.quality.value == "poor":
                issues.append("章节结尾过渡质量较差")
            if prev_analysis and prev_analysis.quality.value == "poor":
                issues.append("与前章过渡质量较差")
            if next_analysis and next_analysis.quality.value == "poor":
                issues.append("与后章过渡质量较差")

            issue_count = len(issues)
            score = 1.0 - (issue_count * 0.2)

            status = SelfCheckStatus.PASSED
            if issue_count >= 3:
                status = SelfCheckStatus.FAILED
            elif issue_count > 0:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.TRANSITION,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                critical_issues=[],
                major_issues=issues,
                moderate_issues=[],
                minor_issues=[],
                details={
                    "opening_quality": opening_analysis.quality.value,
                    "ending_quality": ending_analysis.quality.value,
                },
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.TRANSITION,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Transition check skipped: {str(e)}"],
            )

    def _check_style(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check style consistency."""
        try:
            analysis = self.style_engine.analyze_consistency(
                content=request.content,
                genre=request.config.enable_style,  # Using enable_style as genre hint
            )

            issue_count = len(analysis.issues)
            score = max(0.0, min(1.0, analysis.overall_score))

            status = SelfCheckStatus.PASSED
            if score < 0.6:
                status = SelfCheckStatus.FAILED
            elif score < 0.8:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.STYLE,
                status=status,
                score=score,
                issue_count=issue_count,
                critical_issues=[],
                major_issues=[i.description for i in analysis.issues if i.severity.value == "major"][:5],
                moderate_issues=[i.description for i in analysis.issues if i.severity.value == "moderate"][:5],
                minor_issues=[i.description for i in analysis.issues if i.severity.value == "minor"][:5],
                details={"tone_consistency": analysis.tone_consistency},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.STYLE,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Style check skipped: {str(e)}"],
            )

    def _check_tone(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check tone consistency within chapter."""
        try:
            profile = self.tone_engine.analyze_chapter_tone(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            shifts = len(profile.tone_shifts) if hasattr(profile, 'tone_shifts') else 0
            issue_count = shifts
            score = 1.0 - (shifts * 0.1)

            status = SelfCheckStatus.PASSED
            if shifts > 3:
                status = SelfCheckStatus.FAILED
            elif shifts > 0:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.TONE,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                moderate_issues=[f"发现{shifts}处语调变化"] if shifts > 0 else [],
                details={"primary_tone": profile.primary_tone.value if hasattr(profile, 'primary_tone') else "unknown"},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.TONE,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Tone check skipped: {str(e)}"],
            )

    def _check_description_density(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check description density balance."""
        try:
            profile = self.description_density_engine.analyze_chapter_density(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            shifts = len(profile.density_shifts) if hasattr(profile, 'density_shifts') else 0
            issue_count = shifts
            score = max(0.0, min(1.0, 1.0 - shifts * 0.1))

            status = SelfCheckStatus.PASSED
            if shifts > 5:
                status = SelfCheckStatus.FAILED
            elif shifts > 0:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.DESCRIPTION_DENSITY,
                status=status,
                score=max(0.0, min(1.0, score)),
                issue_count=issue_count,
                moderate_issues=[f"发现{shifts}处描写密度变化"] if shifts > 0 else [],
                details={"average_density": profile.average_density.value if hasattr(profile, 'average_density') else "unknown"},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.DESCRIPTION_DENSITY,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Description density check skipped: {str(e)}"],
            )

    def _check_dialogue_naturalness(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check dialogue naturalness."""
        try:
            analysis = self.dialogue_naturalness_engine.analyze_chapter_dialogue(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
                characters=request.characters,
            )

            issue_count = len(analysis.issues) if hasattr(analysis, 'issues') else 0
            score = max(0.0, min(1.0, analysis.overall_score if hasattr(analysis, 'overall_score') else 1.0))

            status = SelfCheckStatus.PASSED
            if score < 0.6:
                status = SelfCheckStatus.FAILED
            elif score < 0.8:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.DIALOGUE_NATURALNESS,
                status=status,
                score=score,
                issue_count=issue_count,
                major_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "major"][:5] if hasattr(analysis, 'issues') else [],
                moderate_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "moderate"][:5] if hasattr(analysis, 'issues') else [],
                details={},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.DIALOGUE_NATURALNESS,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Dialogue naturalness check skipped: {str(e)}"],
            )

    def _check_scene_vividness(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check scene vividness."""
        try:
            analysis = self.scene_vividness_engine.analyze_chapter_vividness(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            issue_count = len(analysis.issues) if hasattr(analysis, 'issues') else 0
            score = max(0.0, min(1.0, analysis.overall_score if hasattr(analysis, 'overall_score') else 1.0))

            status = SelfCheckStatus.PASSED
            if score < 0.6:
                status = SelfCheckStatus.FAILED
            elif score < 0.8:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.SCENE_VIVIDNESS,
                status=status,
                score=score,
                issue_count=issue_count,
                major_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "major"][:5] if hasattr(analysis, 'issues') else [],
                moderate_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "moderate"][:5] if hasattr(analysis, 'issues') else [],
                details={},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.SCENE_VIVIDNESS,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Scene vividness check skipped: {str(e)}"],
            )

    def _check_plot_logic(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check plot logic consistency."""
        try:
            analysis = self.plot_logic_engine.analyze_chapter_plot_logic(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            issue_count = len(analysis.issues) if hasattr(analysis, 'issues') else 0
            score = max(0.0, min(1.0, analysis.overall_score if hasattr(analysis, 'overall_score') else 1.0))

            status = SelfCheckStatus.PASSED
            if score < 0.6:
                status = SelfCheckStatus.FAILED
            elif score < 0.8:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.PLOT_LOGIC,
                status=status,
                score=score,
                issue_count=issue_count,
                major_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "major"][:5] if hasattr(analysis, 'issues') else [],
                moderate_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "moderate"][:5] if hasattr(analysis, 'issues') else [],
                details={},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.PLOT_LOGIC,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Plot logic check skipped: {str(e)}"],
            )

    def _check_payoff_completeness(self, request: ChapterSelfCheckRequest) -> SelfCheckResult:
        """Check payoff completeness for foreshadowed elements."""
        try:
            analysis = self.payoff_engine.analyze_chapter_payoff_completeness(
                chapter_id=request.chapter_id,
                chapter_number=request.chapter_number,
                title=request.title,
                content=request.content,
            )

            issue_count = len(analysis.issues) if hasattr(analysis, 'issues') else 0
            score = max(0.0, min(1.0, analysis.overall_score if hasattr(analysis, 'overall_score') else 1.0))

            status = SelfCheckStatus.PASSED
            if score < 0.6:
                status = SelfCheckStatus.FAILED
            elif score < 0.8:
                status = SelfCheckStatus.WARNING

            return SelfCheckResult(
                check_type=SelfCheckType.PAYOFF_COMPLETENESS,
                status=status,
                score=score,
                issue_count=issue_count,
                major_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "major"][:5] if hasattr(analysis, 'issues') else [],
                moderate_issues=[i.description for i in analysis.issues if hasattr(i, 'severity') and i.severity.value == "moderate"][:5] if hasattr(analysis, 'issues') else [],
                details={},
            )
        except Exception as e:
            return SelfCheckResult(
                check_type=SelfCheckType.PAYOFF_COMPLETENESS,
                status=SelfCheckStatus.WARNING,
                score=1.0,
                issue_count=0,
                warnings=[f"Payoff completeness check skipped: {str(e)}"],
            )

    def _update_counts(
        self,
        status: SelfCheckStatus,
        checks_passed: int,
        checks_failed: int,
        checks_warning: int,
    ) -> None:
        """Update check counts based on status."""
        if status == SelfCheckStatus.PASSED:
            checks_passed += 1
        elif status == SelfCheckStatus.FAILED:
            checks_failed += 1
        elif status == SelfCheckStatus.WARNING:
            checks_warning += 1

    def _calculate_overall_score(self, check_results: list[SelfCheckResult]) -> float:
        """Calculate overall score from check results."""
        if not check_results:
            return 1.0

        total_score = sum(r.score for r in check_results)
        return total_score / len(check_results)

    def _create_revision_plan(
        self,
        check_results: list[SelfCheckResult],
        request: ChapterSelfCheckRequest,
    ) -> SelfCheckPlan:
        """Create revision plan based on check results."""
        plan = SelfCheckPlan(
            chapter_id=request.chapter_id,
            chapter_number=request.chapter_number,
        )

        for result in check_results:
            if result.status == SelfCheckStatus.FAILED:
                # Add critical/major issues to priority fixes
                plan.priority_fixes.extend(result.critical_issues)
                plan.priority_fixes.extend(result.major_issues)

            # Categorize fixes by type
            if result.check_type == SelfCheckType.GRAMMAR:
                plan.grammar_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.SENTENCE_QUALITY:
                plan.sentence_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.DIALOGUE_TAG:
                plan.dialogue_tag_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.PUNCTUATION:
                plan.punctuation_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.WORD_COUNT:
                plan.word_count_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.TRANSITION:
                plan.transition_fixes.extend(result.major_issues + result.moderate_issues)
            elif result.check_type == SelfCheckType.STYLE:
                plan.style_fixes.extend(result.major_issues + result.moderate_issues)
            else:
                plan.other_fixes.extend(result.major_issues + result.moderate_issues)

            # Add recommendations
            plan.priority_fixes.extend(result.recommendations)

        # Deduplicate
        plan.priority_fixes = list(dict.fromkeys(plan.priority_fixes))
        plan.grammar_fixes = list(dict.fromkeys(plan.grammar_fixes))
        plan.sentence_fixes = list(dict.fromkeys(plan.sentence_fixes))
        plan.dialogue_tag_fixes = list(dict.fromkeys(plan.dialogue_tag_fixes))
        plan.punctuation_fixes = list(dict.fromkeys(plan.punctuation_fixes))
        plan.word_count_fixes = list(dict.fromkeys(plan.word_count_fixes))
        plan.transition_fixes = list(dict.fromkeys(plan.transition_fixes))
        plan.style_fixes = list(dict.fromkeys(plan.style_fixes))
        plan.other_fixes = list(dict.fromkeys(plan.other_fixes))

        return plan

    def _generate_summary(
        self,
        status: SelfCheckStatus,
        overall_score: float,
        total_issues: int,
        checks_failed: int,
        checks_warning: int,
    ) -> str:
        """Generate human-readable summary."""
        if status == SelfCheckStatus.PASSED:
            return f"章节自检通过。整体质量评分 {overall_score:.1%}，共发现 {total_issues} 处小问题。"
        elif status == SelfCheckStatus.WARNING:
            return f"章节自检发现 {checks_warning} 处警告。整体质量评分 {overall_score:.1%}，共 {total_issues} 处问题需关注。"
        else:
            return f"章节自检未通过。{checks_failed} 项检查失败，整体质量评分 {overall_score:.1%}，共 {total_issues} 处问题需要修复。"

    def get_summary(
        self,
        result: ChapterSelfCheckResult,
    ) -> str:
        """Get a short summary from check result.

        Args:
            result: Self-check result

        Returns:
            Short summary string
        """
        return result.report.summary
