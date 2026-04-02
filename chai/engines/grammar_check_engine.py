"""Grammar and typo check engine for quality assurance."""

import re
import uuid
from typing import Optional
from collections import Counter

from chai.models import Novel, Chapter
from chai.models.grammar_check import (
    GrammarErrorType,
    GrammarErrorSeverity,
    GrammarError,
    GrammarCheckResult,
    ChapterGrammarProfile,
    GrammarCheckAnalysis,
    GrammarCheckRevision,
    GrammarCheckPlan,
    GrammarCheckReport,
    TypoPattern,
    GrammarPattern,
)
from chai.services import AIService


# Common Chinese typos (wrong -> correct)
COMMON_TYPOS: list[TypoPattern] = [
    # 的地得混淆
    TypoPattern(pattern="的", correction="地", error_type=GrammarErrorType.DE_CONFUSION, examples=["慢慢地走", "高兴的跳"]),
    TypoPattern(pattern="地", correction="的", error_type=GrammarErrorType.DE_CONFUSION, examples=["美丽的地", "高大的地"]),
    TypoPattern(pattern="得", correction="的", error_type=GrammarErrorType.DE_CONFUSION, examples=["我的得", "你的得"]),
    # 常见错别字
    TypoPattern(pattern="在哪", correction="在哪儿", error_type=GrammarErrorType.TYPO),
    TypoPattern(pattern="好象", correction="好像", error_type=GrammarErrorType.TYPO),
    TypoPattern(pattern="象", correction="像", error_type=GrammarErrorType.HOMOPHONE_ERROR, examples=["图像", "画像"]),
    TypoPattern(pattern="竟", correction="竞", error_type=GrammarErrorType.HOMOPHONE_ERROR),
    TypoPattern(pattern="己", correction="已", error_type=GrammarErrorType.HOMOPHONE_ERROR),
    TypoPattern(pattern="戌", correction="戍", error_type=GrammarErrorType.CHARACTER_CONFUSION),
    TypoPattern(pattern="赢", correction="羸", error_type=GrammarErrorType.CHARACTER_CONFUSION),
    # 其他常见错误
    TypoPattern(pattern="练", correction="炼", error_type=GrammarErrorType.TYPO),
    TypoPattern(pattern="胁", correction="协", error_type=GrammarErrorType.CHARACTER_CONFUSION),
    TypoPattern(pattern="籍", correction="藉", error_type=GrammarErrorType.CHARACTER_CONFUSION),
]

# Grammar patterns for detection
GRAMMAR_PATTERNS: list[GrammarPattern] = [
    # 句子不完整
    GrammarPattern(
        pattern=r"[，、][a-zA-Z\u4e00-\u9fa5]+$",
        error_type=GrammarErrorType.INCOMPLETE_SENTENCE,
        description="句子以逗号或顿号结尾，不完整",
        severity=GrammarErrorSeverity.MAJOR,
    ),
    # 了重复
    GrammarPattern(
        pattern=r"了了",
        error_type=GrammarErrorType.REPEATED_LE,
        description="'了'字重复使用",
        severity=GrammarErrorSeverity.MAJOR,
    ),
    GrammarPattern(
        pattern=r"已经了",
        error_type=GrammarErrorType.EXTRA_LE,
        description="'已经'后不应再加'了'",
        severity=GrammarErrorSeverity.MINOR,
    ),
    GrammarPattern(
        pattern=r"曾经了",
        error_type=GrammarErrorType.EXTRA_LE,
        description="'曾经'后不应再加'了'",
        severity=GrammarErrorSeverity.MINOR,
    ),
    # 的地得错误
    GrammarPattern(
        pattern=r"\w+的地飞",
        error_type=GrammarErrorType.DE_CONFUSION,
        description="'地'用错，应为'得'",
        severity=GrammarErrorSeverity.MINOR,
    ),
    GrammarPattern(
        pattern=r"的很",
        error_type=GrammarErrorType.DE_CONFUSION,
        description="'的'后接形容词时应用'地'",
        severity=GrammarErrorSeverity.MINOR,
    ),
    GrammarPattern(
        pattern=r"\w+得跑",
        error_type=GrammarErrorType.DE_CONFUSION,
        description="'得'用错，应为'地'",
        severity=GrammarErrorSeverity.MINOR,
    ),
    # 标点错误
    GrammarPattern(
        pattern=r"，，",
        error_type=GrammarErrorType.PUNCTUATION_CONFUSION,
        description="逗号重复",
        severity=GrammarErrorSeverity.TYPOGRAPHICAL,
    ),
    GrammarPattern(
        pattern=r"。。",
        error_type=GrammarErrorType.PUNCTUATION_CONFUSION,
        description="句号重复",
        severity=GrammarErrorSeverity.TYPOGRAPHICAL,
    ),
    GrammarPattern(
        pattern=r"。。。[。]",
        error_type=GrammarErrorType.PUNCTUATION_CONFUSION,
        description="省略号后不应接句号",
        severity=GrammarErrorSeverity.MINOR,
    ),
    # 主谓不一致
    GrammarPattern(
        pattern=r"(他的|她的|它的|我的|你的).*(是|在|有).*(了|的|吗)",
        error_type=GrammarErrorType.SUBJECT_VERB_DISAGREEMENT,
        description="主谓可能不一致",
        severity=GrammarErrorSeverity.MINOR,
    ),
]

# Dialogue-specific patterns
DIALOGUE_PATTERNS: list[GrammarPattern] = [
    GrammarPattern(
        pattern=r'"[^"]*',
        error_type=GrammarErrorType.MISSING_PUNCTUATION,
        description="引号未闭合",
        severity=GrammarErrorSeverity.MAJOR,
    ),
    GrammarPattern(
        pattern=r"「[^」]*",
        error_type=GrammarErrorType.MISSING_PUNCTUATION,
        description="中文引号未闭合",
        severity=GrammarErrorSeverity.MAJOR,
    ),
]

# Redundant words patterns
REDUNDANT_PATTERNS: list[tuple[str, str]] = [
    (r"非常极其", "极其"),
    (r"大约左右", "大约"),
    (r"多年的以来", "多年以来"),
    (r"十分非常", "十分"),
    (r"各种各样", "各种"),
    (r"多年来一直", "多年来"),
    (r"不断地不断", "不断地"),
    (r"一次又一次", "一次又一次"),
]


class GrammarCheckEngine:
    """Engine for checking grammar and typos in manuscript."""

    def __init__(self, ai_service: AIService):
        """Initialize grammar check engine with AI service."""
        self.ai_service = ai_service

    def check_novel_grammar(self, novel: Novel) -> GrammarCheckAnalysis:
        """Check all chapters for grammar and typos.

        Args:
            novel: Novel to check

        Returns:
            Comprehensive grammar analysis
        """
        chapters = list(novel.chapters.values()) if isinstance(novel.chapters, dict) else novel.chapters
        total_chapters = len(chapters)

        if total_chapters == 0:
            return GrammarCheckAnalysis()

        # Analyze each chapter
        chapter_profiles = []
        all_errors = []

        for chapter in chapters:
            profile, errors = self.check_chapter_grammar(chapter)
            chapter_profiles.append(profile)
            all_errors.extend(errors)

        # Aggregate statistics
        total_sentences = sum(p.total_sentences for p in chapter_profiles)
        total_errors = len(all_errors)

        # Count by type
        errors_by_type: dict[str, int] = {}
        for error in all_errors:
            error_type = error.error_type.value
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        # Count by severity
        critical_count = sum(1 for e in all_errors if e.severity == GrammarErrorSeverity.CRITICAL)
        major_count = sum(1 for e in all_errors if e.severity == GrammarErrorSeverity.MAJOR)
        minor_count = sum(1 for e in all_errors if e.severity == GrammarErrorSeverity.MINOR)
        typographical_count = sum(1 for e in all_errors if e.severity == GrammarErrorSeverity.TYPOGRAPHICAL)

        # Calculate overall scores
        overall_grammar = self._calculate_grammar_score(all_errors, total_sentences)
        overall_typo = self._calculate_typo_score(all_errors, total_sentences)
        overall_punctuation = self._calculate_punctuation_score(all_errors, total_sentences)

        # Find common typos
        typo_words = [e.original_text for e in all_errors if e.error_type == GrammarErrorType.TYPO]
        common_typos = Counter(typo_words).most_common(10)

        # Find common grammar errors
        grammar_error_types = [e.error_type.value for e in all_errors
                             if e.error_type not in (GrammarErrorType.TYPO, GrammarErrorType.PUNCTUATION_CONFUSION)]
        common_grammar = Counter(grammar_error_types).most_common(10)

        # Chapters needing revision
        chapters_needing_revision = [p.chapter_number for p in chapter_profiles if p.needs_revision]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            all_errors, errors_by_type, chapters_needing_revision
        )

        analysis = GrammarCheckAnalysis(
            overall_grammar_score=overall_grammar,
            overall_typo_score=overall_typo,
            overall_punctuation_score=overall_punctuation,
            total_chapters=total_chapters,
            total_sentences=total_sentences,
            total_errors=total_errors,
            errors_by_type=errors_by_type,
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            typographical_count=typographical_count,
            chapter_profiles=chapter_profiles,
            all_errors=all_errors,
            common_typos=common_typos,
            common_grammar_errors=common_grammar,
            chapters_needing_revision=chapters_needing_revision,
            has_critical_issues=critical_count > 0,
            recommendations=recommendations,
        )

        return analysis

    def check_chapter_grammar(self, chapter: Chapter) -> tuple[ChapterGrammarProfile, list[GrammarError]]:
        """Check a single chapter for grammar and typos.

        Args:
            chapter: Chapter to check

        Returns:
            Tuple of (chapter profile, list of errors)
        """
        content = chapter.content or ""
        errors = []

        if not content:
            return ChapterGrammarProfile(
                chapter_number=chapter.number,
                chapter_title=chapter.title or "",
            ), []

        # Split into sentences
        sentences = self._split_sentences(content)

        # Analyze sentences
        total_sentences = len(sentences)
        total_characters = len(content)
        dialogue_sentences = sum(1 for s in sentences if self._is_dialogue(s))
        narration_sentences = total_sentences - dialogue_sentences

        # Detect errors in each sentence
        for idx, sentence in enumerate(sentences):
            sentence_errors = self._check_sentence(sentence, chapter.number, idx)
            errors.extend(sentence_errors)

        # Check for structural issues
        structural_errors = self._check_structural_issues(content, chapter.number)
        errors.extend(structural_errors)

        # Check for typos
        typo_errors = self._check_typos(content, chapter.number)
        errors.extend(typo_errors)

        # Count errors by type
        error_counts: dict[str, int] = {}
        for error in errors:
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Severity distribution
        critical_errors = sum(1 for e in errors if e.severity == GrammarErrorSeverity.CRITICAL)
        major_errors = sum(1 for e in errors if e.severity == GrammarErrorSeverity.MAJOR)
        minor_errors = sum(1 for e in errors if e.severity == GrammarErrorSeverity.MINOR)
        typographical_errors = sum(1 for e in errors if e.severity == GrammarErrorSeverity.TYPOGRAPHICAL)

        # Calculate scores
        grammar_score = max(0.0, 1.0 - (len(errors) / max(1, total_sentences)) * 0.5)
        typo_score = max(0.0, 1.0 - (sum(1 for e in errors if e.error_type == GrammarErrorType.TYPO) / max(1, total_sentences)))
        punctuation_score = max(0.0, 1.0 - (sum(1 for e in errors if "punctuation" in e.error_type.value) / max(1, total_sentences)))

        # Dialogue vs narration errors
        dialogue_errors = sum(1 for e in errors if self._is_dialogue(e.sentence))
        narration_errors = len(errors) - dialogue_errors

        # Quality indicators
        needs_revision = major_errors > 0 or critical_errors > 0 or (minor_errors > total_sentences * 0.1)
        is_well_written = not needs_revision and grammar_score > 0.9

        profile = ChapterGrammarProfile(
            chapter_number=chapter.number,
            chapter_title=chapter.title or "",
            total_sentences=total_sentences,
            total_characters=total_characters,
            dialogue_sentences=dialogue_sentences,
            narration_sentences=narration_sentences,
            error_counts=error_counts,
            total_errors=len(errors),
            critical_errors=critical_errors,
            major_errors=major_errors,
            minor_errors=minor_errors,
            typographical_errors=typographical_errors,
            grammar_score=grammar_score,
            typo_score=typo_score,
            punctuation_score=punctuation_score,
            dialogue_errors=dialogue_errors,
            narration_errors=narration_errors,
            is_well_written=is_well_written,
            needs_revision=needs_revision,
        )

        return profile, errors

    def create_revision_plan(self, analysis: GrammarCheckAnalysis) -> GrammarCheckPlan:
        """Create a revision plan based on analysis.

        Args:
            analysis: Grammar check analysis

        Returns:
            Revision plan
        """
        critical_ids = [e.error_id for e in analysis.all_errors
                       if e.severity == GrammarErrorSeverity.CRITICAL]
        major_ids = [e.error_id for e in analysis.all_errors
                    if e.severity == GrammarErrorSeverity.MAJOR]
        minor_ids = [e.error_id for e in analysis.all_errors
                    if e.severity == GrammarErrorSeverity.MINOR]

        # Create priority order
        priority_order: list[tuple[str, int]] = []
        for eid in critical_ids:
            priority_order.append((eid, 100))
        for eid in major_ids:
            priority_order.append((eid, 70))
        for eid in minor_ids:
            priority_order.append((eid, 30))

        priority_order.sort(key=lambda x: x[1], reverse=True)

        # Determine focus areas
        typo_count = sum(1 for e in analysis.all_errors if e.error_type == GrammarErrorType.TYPO)
        grammar_count = sum(1 for e in analysis.all_errors
                          if e.error_type not in (GrammarErrorType.TYPO, GrammarErrorType.PUNCTUATION_CONFUSION))
        punctuation_count = sum(1 for e in analysis.all_errors if "punctuation" in e.error_type.value)

        plan = GrammarCheckPlan(
            critical_to_fix=critical_ids,
            major_to_fix=major_ids,
            minor_to_fix=minor_ids,
            chapters_to_revise=analysis.chapters_needing_revision,
            priority_order=priority_order,
            estimated_fixes=len(analysis.all_errors),
            ai_assistance_needed=grammar_count > 10,
            focus_on_typos=typo_count > 0,
            focus_on_grammar=grammar_count > 0,
            focus_on_punctuation=punctuation_count > 0,
        )

        return plan

    def generate_check_report(
        self,
        analysis: GrammarCheckAnalysis,
        plan: Optional[GrammarCheckPlan] = None,
    ) -> GrammarCheckReport:
        """Generate a complete check report.

        Args:
            analysis: Grammar check analysis
            plan: Optional revision plan

        Returns:
            Complete check report
        """
        if plan is None:
            plan = self.create_revision_plan(analysis)

        summary = self._generate_summary(analysis)

        report = GrammarCheckReport(
            analysis=analysis,
            revision_plan=plan,
            summary=summary,
            revisions_completed=[],
        )

        return report

    def get_grammar_summary(self, analysis: GrammarCheckAnalysis) -> str:
        """Get a human-readable summary of grammar check.

        Args:
            analysis: Grammar check analysis

        Returns:
            Summary string
        """
        lines = [
            "=== 语法与错别字检查报告 ===",
            "",
            f"检查章节数: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"总错误数: {analysis.total_errors}",
            "",
            "--- 错误分布 ---",
            f"严重错误: {analysis.critical_count}",
            f"较大错误: {analysis.major_count}",
            f"一般错误: {analysis.minor_count}",
            f"排版问题: {analysis.typographical_count}",
            "",
            "--- 评分 ---",
            f"语法评分: {analysis.overall_grammar_score:.0%}",
            f"错字评分: {analysis.overall_typo_score:.0%}",
            f"标点评分: {analysis.overall_punctuation_score:.0%}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision))}")

        if analysis.common_typos:
            lines.append("")
            lines.append("--- 常见错字 ---")
            for word, count in analysis.common_typos[:5]:
                lines.append(f"  {word}: {count}次")

        return "\n".join(lines)

    # Helper methods

    def _split_sentences(self, content: str) -> list[str]:
        """Split content into sentences."""
        # Split by Chinese sentence endings
        sentences = re.split(r'[。！？!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _is_dialogue(self, sentence: str) -> bool:
        """Check if a sentence is dialogue."""
        # Check for dialogue markers
        dialogue_markers = ['"', '"', '"', '"', '「', '」', '『', '』', '说：', '说道：', '答道：', '问道：']
        return any(marker in sentence for marker in dialogue_markers)

    def _check_sentence(self, sentence: str, chapter: int, sentence_idx: int) -> list[GrammarError]:
        """Check a single sentence for errors."""
        errors = []

        # Check grammar patterns
        for pattern in GRAMMAR_PATTERNS:
            matches = re.finditer(pattern.pattern, sentence)
            for match in matches:
                error = GrammarError(
                    error_id=f"grammar_{chapter}_{sentence_idx}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=sentence,
                    position=match.start(),
                    error_type=pattern.error_type,
                    severity=pattern.severity,
                    original_text=match.group(),
                    suggested_fix="",
                    description=pattern.description,
                    confidence=0.8,
                )
                errors.append(error)

        # Check redundant words
        for wrong, correct in REDUNDANT_PATTERNS:
            if wrong in sentence:
                idx = sentence.find(wrong)
                error = GrammarError(
                    error_id=f"redundant_{chapter}_{sentence_idx}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=sentence,
                    position=idx,
                    error_type=GrammarErrorType.REDUNDANT_WORD,
                    severity=GrammarErrorSeverity.MINOR,
                    original_text=wrong,
                    suggested_fix=correct,
                    description=f"冗余词语，建议改为'{correct}'",
                    confidence=0.9,
                )
                errors.append(error)

        # Check for incomplete sentences (ends with comma/pause)
        if sentence.endswith(('，', '、')):
            error = GrammarError(
                error_id=f"incomplete_{chapter}_{sentence_idx}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence=sentence,
                position=len(sentence) - 1,
                error_type=GrammarErrorType.INCOMPLETE_SENTENCE,
                severity=GrammarErrorSeverity.MAJOR,
                original_text=sentence[-1],
                suggested_fix="",
                description="句子以逗号/顿号结尾，不完整",
                confidence=0.95,
            )
            errors.append(error)

        return errors

    def _check_structural_issues(self, content: str, chapter: int) -> list[GrammarError]:
        """Check for structural issues in content."""
        errors = []

        # Check for repeated punctuation
        repeated_patterns = [
            (r'，，+', '，'),
            (r'。。+', '。'),
            (r'？？+', '？'),
            (r'！！+', '！'),
        ]

        for pattern, replacement in repeated_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                error = GrammarError(
                    error_id=f"struct_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=match.group(),
                    position=match.start(),
                    error_type=GrammarErrorType.PUNCTUATION_CONFUSION,
                    severity=GrammarErrorSeverity.TYPOGRAPHICAL,
                    original_text=match.group(),
                    suggested_fix=replacement,
                    description="标点符号重复",
                    confidence=0.95,
                )
                errors.append(error)

        # Check for dialogue quote balance
        double_quote_count = content.count('"')
        if double_quote_count % 2 != 0:
            # Find the position of the last quote
            last_pos = content.rfind('"')
            error = GrammarError(
                error_id=f"quote_{chapter}_{uuid.uuid4().hex[:6]}",
                chapter=chapter,
                sentence=content[max(0, last_pos-20):last_pos+20],
                position=last_pos,
                error_type=GrammarErrorType.MISSING_PUNCTUATION,
                severity=GrammarErrorSeverity.MAJOR,
                original_text='"',
                suggested_fix='"' if last_pos == len(content) - 1 else '',
                description="引号未配对",
                confidence=0.9,
            )
            errors.append(error)

        # Check for 了 errors
        le_patterns = [
            (r'了了', GrammarErrorType.REPEATED_LE, "'了'字重复"),
            (r'已经了', GrammarErrorType.EXTRA_LE, "'已经'后不应再加'了'"),
            (r'曾经了', GrammarErrorType.EXTRA_LE, "'曾经'后不应再加'了'"),
            (r'终于了', GrammarErrorType.EXTRA_LE, "'终于'后不应再加'了'"),
            (r'马上了', GrammarErrorType.EXTRA_LE, "'马上'后不应再加'了'"),
            (r'立刻了', GrammarErrorType.EXTRA_LE, "'立刻'后不应再加'了'"),
        ]

        for pattern, error_type, description in le_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                error = GrammarError(
                    error_id=f"le_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=self._get_context_sentence(content, match.start()),
                    position=match.start(),
                    error_type=error_type,
                    severity=GrammarErrorSeverity.MAJOR,
                    original_text=match.group(),
                    suggested_fix=match.group().replace('了了', '了').replace('已经了', '已经').replace('曾经了', '曾经').replace('终于了', '终于').replace('马上了', '马上').replace('立刻了', '立刻'),
                    description=description,
                    confidence=0.9,
                )
                errors.append(error)

        return errors

    def _check_typos(self, content: str, chapter: int) -> list[GrammarError]:
        """Check for typos in content."""
        errors = []

        # Check common typos
        for typo in COMMON_TYPOS:
            pattern = typo.pattern
            # Use word boundary for single characters
            if len(pattern) == 1:
                regex_pattern = f'{pattern}'
            else:
                regex_pattern = pattern

            matches = re.finditer(regex_pattern, content)
            for match in matches:
                # Get surrounding context to avoid false positives
                context = self._get_context_sentence(content, match.start())

                # Check if this is actually an error
                if self._is_false_positive(match.group(), typo):
                    continue

                error = GrammarError(
                    error_id=f"typo_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=context,
                    position=match.start(),
                    error_type=typo.error_type,
                    severity=GrammarErrorSeverity.MINOR,
                    original_text=match.group(),
                    suggested_fix=typo.correction,
                    description=f"疑似错字，可能应为'{typo.correction}'",
                    confidence=0.7,
                )
                errors.append(error)

        # Check for character confusion (homophones)
        homophone_checks = [
            # 这/那 confusion
            (r'这{1,3}个', None),  # "这这个" - repetition
            # 的地得 confusion (more specific patterns)
            (r'\w+的高', GrammarErrorType.DE_CONFUSION),  # "XX的高" - should be "XX地"
            (r'\w+地很', None),  # "XX得很" - correct
        ]

        # Check specific patterns
        specific_patterns = [
            # 的误用
            (r'(很|非常|特别|十分|相当)的高', GrammarErrorType.DE_CONFUSION, "副词后应用'地'"),
            # 地误用
            (r'(美丽|漂亮|高大|强壮|善良)的地', GrammarErrorType.DE_CONFUSION, "形容词后应用'的'"),
            # 得误用
            (r'(跳|跑|走|飞|说)的', GrammarErrorType.DE_CONFUSION, "动词后应用'得'"),
        ]

        for pattern, error_type, desc in specific_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if error_type is None:
                    continue

                error = GrammarError(
                    error_id=f"confusion_{chapter}_{uuid.uuid4().hex[:6]}",
                    chapter=chapter,
                    sentence=self._get_context_sentence(content, match.start()),
                    position=match.start(),
                    error_type=error_type,
                    severity=GrammarErrorSeverity.MINOR,
                    original_text=match.group(),
                    suggested_fix="",
                    description=desc,
                    confidence=0.75,
                )
                errors.append(error)

        return errors

    def _is_false_positive(self, matched_text: str, typo: TypoPattern) -> bool:
        """Check if a typo match is a false positive."""
        # Skip single character matches in some cases
        if len(matched_text) == 1 and matched_text in ['的', '地', '得']:
            return False  # These are commonly errors
        return False

    def _get_context_sentence(self, content: str, position: int, context_size: int = 30) -> str:
        """Get the sentence containing the position."""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)

        # Find sentence boundaries
        before = content[start:position]
        after = content[position:end]

        # Try to find sentence boundaries
        for i in range(len(before) - 1, -1, -1):
            if before[i] in '。！？?!\n':
                start = start + i + 1
                break

        for i, c in enumerate(after):
            if c in '。！？?!\n':
                end = position + i + 1
                break

        return content[start:end].strip()

    def _calculate_grammar_score(self, errors: list[GrammarError], total_sentences: int) -> float:
        """Calculate overall grammar score."""
        if total_sentences == 0:
            return 1.0

        grammar_errors = [e for e in errors if e.error_type not in (
            GrammarErrorType.TYPO,
            GrammarErrorType.PUNCTUATION_CONFUSION,
            GrammarErrorType.MISSING_PUNCTUATION,
            GrammarErrorType.EXTRA_PUNCTUATION,
        )]

        error_rate = len(grammar_errors) / total_sentences
        return max(0.0, 1.0 - error_rate)

    def _calculate_typo_score(self, errors: list[GrammarError], total_sentences: int) -> float:
        """Calculate typo score."""
        if total_sentences == 0:
            return 1.0

        typo_errors = [e for e in errors if e.error_type == GrammarErrorType.TYPO]
        error_rate = len(typo_errors) / total_sentences
        return max(0.0, 1.0 - error_rate * 2)  # Typos weighted less

    def _calculate_punctuation_score(self, errors: list[GrammarError], total_sentences: int) -> float:
        """Calculate punctuation score."""
        if total_sentences == 0:
            return 1.0

        punctuation_errors = [e for e in errors if 'punctuation' in e.error_type.value]
        error_rate = len(punctuation_errors) / total_sentences
        return max(0.0, 1.0 - error_rate)

    def _generate_recommendations(
        self,
        errors: list[GrammarError],
        errors_by_type: dict[str, int],
        chapters_needing_revision: list[int],
    ) -> list[str]:
        """Generate recommendations based on errors."""
        recs = []

        # Critical issues
        critical = [e for e in errors if e.severity == GrammarErrorSeverity.CRITICAL]
        if critical:
            recs.append(f"存在 {len(critical)} 个严重错误，必须立即修正")

        # Major issues
        major = [e for e in errors if e.severity == GrammarErrorSeverity.MAJOR]
        if major:
            recs.append(f"存在 {len(major)} 个较大错误，建议优先修正")

        # Common typo recommendation
        typo_count = errors_by_type.get(GrammarErrorType.TYPO.value, 0)
        if typo_count > 5:
            recs.append("错别字较多，建议使用专业校对工具或AI辅助修正")

        # Grammar errors
        grammar_count = sum(1 for k, v in errors_by_type.items()
                           if k not in (GrammarErrorType.TYPO.value, GrammarErrorType.PUNCTUATION_CONFUSION.value))
        if grammar_count > 10:
            recs.append("语法错误较多，建议通读修改或使用AI辅助")

        # Punctuation
        punct_count = errors_by_type.get(GrammarErrorType.PUNCTUATION_CONFUSION.value, 0)
        if punct_count > 3:
            recs.append("标点符号问题较多，请检查并统一标点使用")

        # Chapter-specific
        if len(chapters_needing_revision) > 5:
            recs.append(f"有 {len(chapters_needing_revision)} 个章节需要重点修改")

        if not recs:
            recs.append("整体语法质量良好，仅需小幅修改")

        return recs

    def _generate_summary(self, analysis: GrammarCheckAnalysis) -> str:
        """Generate human-readable summary."""
        lines = [
            "《语法与错别字检查报告》",
            "",
            f"检查章节: {analysis.total_chapters}",
            f"总句子数: {analysis.total_sentences}",
            f"总错误数: {analysis.total_errors}",
            "",
            "错误分布:",
            f"  严重错误: {analysis.critical_count}",
            f"  较大错误: {analysis.major_count}",
            f"  一般错误: {analysis.minor_count}",
            f"  排版问题: {analysis.typographical_count}",
            "",
            "评分:",
            f"  语法评分: {analysis.overall_grammar_score:.0%}",
            f"  错字评分: {analysis.overall_typo_score:.0%}",
            f"  标点评分: {analysis.overall_punctuation_score:.0%}",
            "",
        ]

        if analysis.chapters_needing_revision:
            lines.append(f"需要修改的章节: {', '.join(map(str, analysis.chapters_needing_revision[:10]))}")
            if len(analysis.chapters_needing_revision) > 10:
                lines.append(f"  (还有 {len(analysis.chapters_needing_revision) - 10} 个)")

        if analysis.common_typos:
            lines.append("")
            lines.append("常见错字:")
            for word, count in analysis.common_typos[:5]:
                lines.append(f"  {word}: {count}次")

        return "\n".join(lines)