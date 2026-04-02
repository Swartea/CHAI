"""Final export engine for orchestrating the complete manuscript export process.

This module provides the FinalExportEngine which coordinates all export formats
(Markdown, EPUB, PDF) after the manuscript has been written, checked, and polished.
"""

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from chai.models.final_export import (
    ExportFormat,
    ExportStatus,
    ValidationStatus,
    ExportQuality,
    ExportTemplate,
    ValidationIssue,
    ManuscriptValidation,
    ExportFormatConfig,
    ExportProgress,
    ExportMetadata,
    ExportResult,
    ExportPackage,
    FinalExportConfig,
    FinalExportRequest,
    FinalExportResult,
    FinalExportSummary,
    ExportChecklist,
)
from chai.models import Novel, Volume, Chapter
from chai.engines.markdown_manuscript_engine import MarkdownManuscriptEngine
from chai.engines.epub_manuscript_engine import EPUBManuscriptEngine
from chai.engines.pdf_manuscript_engine import PDFManuscriptEngine


class FinalExportEngine:
    """Engine for orchestrating the final manuscript export.

    This engine coordinates the complete export workflow:
    1. Validates the manuscript for export readiness
    2. Exports to requested formats (Markdown, EPUB, PDF)
    3. Creates a complete export package with metadata
    4. Generates validation and summary reports
    """

    def __init__(self, config: Optional[FinalExportConfig] = None):
        """Initialize the final export engine.

        Args:
            config: Optional configuration for export operation.
        """
        self.config = config or FinalExportConfig()

    def export(self, request: FinalExportRequest) -> FinalExportResult:
        """Perform the final export operation.

        Args:
            request: Export request containing manuscript data and configuration.

        Returns:
            FinalExportResult with complete export results and package info.
        """
        start_time = time.time()
        export_id = f"export_{uuid.uuid4().hex[:8]}"

        # Initialize result
        result = FinalExportResult(
            export_id=export_id,
            title=request.title,
            status=ExportStatus.IN_PROGRESS,
            started_at=datetime.now().isoformat(),
        )

        try:
            # Step 1: Validate manuscript
            validation = self._validate_manuscript(request)
            result.validation = validation

            if validation.status == ValidationStatus.INVALID:
                if self.config.fail_on_critical and validation.critical_issues:
                    result.success = False
                    result.status = ExportStatus.FAILED
                    result.error_message = "Critical validation issues found"
                    result.completed_at = datetime.now().isoformat()
                    result.elapsed_time = time.time() - start_time
                    return result

            # Step 2: Build novel structure from request data
            novel = self._build_novel(request)

            # Step 3: Create output directory
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 4: Export to each format
            export_results: list[ExportResult] = []
            package = ExportPackage(
                package_id=export_id,
                title=request.title,
                export_date=datetime.now().strftime("%Y-%m-%d"),
                base_output_dir=str(output_dir),
            )

            formats_to_export = self._get_formats_to_export()

            for fmt in formats_to_export:
                export_result = self._export_format(
                    fmt, novel, request, output_dir
                )
                export_results.append(export_result)

                if fmt == ExportFormat.MARKDOWN:
                    package.markdown_export = export_result
                elif fmt == ExportFormat.EPUB:
                    package.epub_export = export_result
                elif fmt == ExportFormat.PDF:
                    package.pdf_export = export_result

            # Update package
            successful = [r for r in export_results if r.status == ExportStatus.COMPLETED]
            failed = [r for r in export_results if r.status == ExportStatus.FAILED]

            package.total_formats = len(export_results)
            package.successful_formats = len(successful)
            package.failed_formats = len(failed)

            # Build metadata
            total_words = sum(c.get("word_count", 0) for v in request.volumes for c in v.get("chapters", []))
            total_chapters = sum(len(v.get("chapters", [])) for v in request.volumes)

            package.metadata = ExportMetadata(
                title=request.title,
                author=request.author,
                genre=request.genre,
                total_words=total_words,
                total_chapters=total_chapters,
                total_volumes=len(request.volumes),
                export_date=datetime.now().isoformat(),
                quality_level=self.config.quality,
                validation_status=validation.status,
                polishing_applied=request.polishing_report is not None,
                self_check_passed=request.self_check_report is not None,
            )

            package.validation = validation

            # Finalize result
            result.success = len(failed) == 0
            result.status = ExportStatus.COMPLETED if result.success else ExportStatus.FAILED
            result.package = package
            result.export_results = export_results
            result.total_formats = len(export_results)
            result.successful_formats = len(successful)
            result.failed_formats = len(failed)
            result.total_file_size = sum(
                r.file_size or 0 for r in export_results
            )

        except Exception as e:
            result.success = False
            result.status = ExportStatus.FAILED
            result.error_message = str(e)

        result.completed_at = datetime.now().isoformat()
        result.elapsed_time = time.time() - start_time

        return result

    def _validate_manuscript(self, request: FinalExportRequest) -> ManuscriptValidation:
        """Validate the manuscript for export readiness.

        Args:
            request: The export request.

        Returns:
            ManuscriptValidation with validation results.
        """
        validation = ManuscriptValidation(
            status=ValidationStatus.VALIDATING,
            validated_at=datetime.now().isoformat(),
        )

        issues: list[ValidationIssue] = []

        # Check 1: Word count
        total_words = sum(
            c.get("word_count", 0)
            for v in request.volumes
            for c in v.get("chapters", [])
        )

        if total_words < 1000:
            issues.append(ValidationIssue(
                issue_id="word_count_low",
                severity="major",
                category="content",
                description=f"总字数过低: {total_words} 字",
                suggestion="建议增加更多内容后再导出",
            ))
            validation.word_count_check = False
        elif total_words < 5000:
            issues.append(ValidationIssue(
                issue_id="word_count_short",
                severity="warning",
                category="content",
                description=f"总字数较少: {total_words} 字",
                suggestion="这是一部短篇作品，如需出版可能需要扩充",
            ))
        else:
            validation.word_count_check = True

        # Check 2: Chapter completeness
        chapters_with_content = 0
        total_chapters = 0
        empty_chapters: list[str] = []

        for vol in request.volumes:
            for ch in vol.get("chapters", []):
                total_chapters += 1
                content = ch.get("content", "")
                if content and len(content.strip()) > 100:
                    chapters_with_content += 1
                else:
                    empty_chapters.append(
                        f"第{vol.get('volume_number', 1)}卷 第{ch.get('chapter_number', 1)}章"
                    )

        validation.total_issues = chapters_with_content < total_chapters

        if empty_chapters:
            issues.append(ValidationIssue(
                issue_id="empty_chapters",
                severity="critical",
                category="content",
                description=f"发现 {len(empty_chapters)} 个空章节",
                location=",".join(empty_chapters[:3]),
                suggestion="请完成所有章节内容后再导出",
            ))
            validation.chapter_completeness_check = False
        else:
            validation.chapter_completeness_check = True

        # Check 3: Structure
        if len(request.volumes) == 0:
            issues.append(ValidationIssue(
                issue_id="no_volumes",
                severity="critical",
                category="structure",
                description="没有发现任何卷/册",
                suggestion="请添加卷/册内容后再导出",
            ))
            validation.structure_check = False
        else:
            validation.structure_check = True

        # Check 4: Chapter numbering continuity
        for vol in request.volumes:
            chapters = vol.get("chapters", [])
            chapter_numbers = [c.get("chapter_number", 0) for c in chapters]
            expected = list(range(1, len(chapters) + 1))

            if chapter_numbers != expected:
                missing = set(expected) - set(chapter_numbers)
                if missing:
                    issues.append(ValidationIssue(
                        issue_id="chapter_numbers",
                        severity="major",
                        category="structure",
                        description=f"卷{vol.get('volume_number', 1)}章节编号不连续",
                        location=f"卷{vol.get('volume_number', 1)}",
                        suggestion=f"缺少章节编号: {sorted(missing)}",
                    ))

        # Categorize issues
        validation.critical_issues = [i for i in issues if i.severity == "critical"]
        validation.major_issues = [i for i in issues if i.severity == "major"]
        validation.minor_issues = [i for i in issues if i.severity == "minor"]
        validation.warnings = [i for i in issues if i.severity == "warning"]

        validation.total_issues = len(issues)

        # Calculate quality score
        base_score = 1.0
        base_score -= len(validation.critical_issues) * 0.3
        base_score -= len(validation.major_issues) * 0.15
        base_score -= len(validation.minor_issues) * 0.05
        base_score -= len(validation.warnings) * 0.02
        validation.quality_score = max(0.0, min(1.0, base_score))

        # Set validation status
        if validation.critical_issues:
            validation.status = ValidationStatus.INVALID
        elif validation.major_issues:
            validation.status = ValidationStatus.WARNING
        elif validation.minor_issues or validation.warnings:
            validation.status = ValidationStatus.WARNING
        else:
            validation.status = ValidationStatus.VALID

        return validation

    def _build_novel(self, request: FinalExportRequest) -> Novel:
        """Build Novel object from request data.

        Args:
            request: The export request.

        Returns:
            Novel object constructed from request data.
        """
        # Build volumes
        volumes: list[Volume] = []
        for vol_data in request.volumes:
            chapters: list[Chapter] = []

            for ch_data in vol_data.get("chapters", []):
                # Build scenes if available
                scenes = []
                for scene_data in ch_data.get("scenes", []):
                    from chai.models import Scene, SceneType
                    scene = Scene(
                        scene_id=scene_data.get("scene_id", f"scene_{uuid.uuid4().hex[:8]}"),
                        scene_type=SceneType.NARRATIVE,
                        location=scene_data.get("location"),
                        time_period=scene_data.get("time_period"),
                        mood=scene_data.get("mood"),
                        content=scene_data.get("content", ""),
                        word_count=len(scene_data.get("content", "")),
                    )
                    scenes.append(scene)

                chapter = Chapter(
                    id=ch_data.get("chapter_id", f"ch_{uuid.uuid4().hex[:8]}"),
                    number=ch_data.get("chapter_number", 1),
                    title=ch_data.get("title", "无标题"),
                    content=ch_data.get("content", ""),
                    summary=ch_data.get("summary", ""),
                    word_count=ch_data.get("word_count", len(ch_data.get("content", ""))),
                    scenes=scenes if scenes else [],
                    is_prologue=ch_data.get("is_prologue", False),
                    is_epilogue=ch_data.get("is_epilogue", False),
                )
                chapters.append(chapter)

            volume = Volume(
                id=vol_data.get("volume_id", f"vol_{uuid.uuid4().hex[:8]}"),
                number=vol_data.get("volume_number", 1),
                title=vol_data.get("title", "无标题"),
                description=vol_data.get("description", ""),
                chapters=chapters,
            )
            volumes.append(volume)

        # Build Novel
        novel = Novel(
            id=request.book_id,
            title=request.title,
            genre=request.genre,
            volumes=volumes,
        )

        return novel

    def _get_formats_to_export(self) -> list[ExportFormat]:
        """Get list of formats to export based on config.

        Returns:
            List of ExportFormat values.
        """
        formats = self.config.formats

        if ExportFormat.ALL in formats:
            return [ExportFormat.MARKDOWN, ExportFormat.EPUB, ExportFormat.PDF]

        return [f for f in formats if f != ExportFormat.ALL]

    def _export_format(
        self,
        fmt: ExportFormat,
        novel: Novel,
        request: FinalExportRequest,
        output_dir: Path,
    ) -> ExportResult:
        """Export manuscript to a specific format.

        Args:
            fmt: The export format.
            novel: The novel object.
            request: The export request.
            output_dir: Base output directory.

        Returns:
            ExportResult for this format.
        """
        result = ExportResult(
            format=fmt,
            status=ExportStatus.IN_PROGRESS,
        )

        start_time = time.time()

        try:
            # Generate filename
            date_str = datetime.now().strftime("%Y%m%d")
            title_clean = request.title.replace(" ", "_").replace("/", "-")

            if fmt == ExportFormat.MARKDOWN:
                filename = f"{title_clean}_markdown_{date_str}.md"
                result = self._export_markdown(novel, output_dir / filename, request)

            elif fmt == ExportFormat.EPUB:
                filename = f"{title_clean}_epub_{date_str}.epub"
                result = self._export_epub(novel, output_dir / filename, request)

            elif fmt == ExportFormat.PDF:
                filename = f"{title_clean}_pdf_{date_str}.pdf"
                result = self._export_pdf(novel, output_dir / filename, request)

            result.status = ExportStatus.COMPLETED
            result.export_time = datetime.now().isoformat()

            # Get file size
            if result.output_path:
                path = Path(result.output_path)
                if path.exists():
                    result.file_size = path.stat().st_size

        except Exception as e:
            result.status = ExportStatus.FAILED
            result.error_message = str(e)

        return result

    def _export_markdown(
        self,
        novel: Novel,
        output_path: Path,
        request: FinalExportRequest,
    ) -> ExportResult:
        """Export to Markdown format.

        Args:
            novel: The novel object.
            output_path: Output file path.
            request: The export request.

        Returns:
            ExportResult for Markdown export.
        """
        from chai.models.manuscript_export import ManuscriptTemplate

        template_map = {
            ExportTemplate.SIMPLE: ManuscriptTemplate.SIMPLE,
            ExportTemplate.STANDARD: ManuscriptTemplate.STANDARD,
            ExportTemplate.DETAILED: ManuscriptTemplate.DETAILED,
            ExportTemplate.PUBLICATION: ManuscriptTemplate.DETAILED,
        }

        template = template_map.get(self.config.markdown_template, ManuscriptTemplate.STANDARD)

        from chai.models.manuscript_export import ManuscriptExportConfig

        config = ManuscriptExportConfig(
            template=template,
            include_table_of_contents=True,
            include_front_matter=True,
            include_back_matter=True,
            include_chapter_summaries=True,
            include_word_counts=True,
            include_character_list=len(request.characters) > 0,
            include_world_setting=request.world_setting is not None,
        )

        engine = MarkdownManuscriptEngine(config=config)
        result = engine.export_to_file(novel, output_path)

        return ExportResult(
            format=ExportFormat.MARKDOWN,
            status=ExportStatus.COMPLETED,
            output_path=str(output_path),
        )

    def _export_epub(
        self,
        novel: Novel,
        output_path: Path,
        request: FinalExportRequest,
    ) -> ExportResult:
        """Export to EPUB format.

        Args:
            novel: The novel object.
            output_path: Output file path.
            request: The export request.

        Returns:
            ExportResult for EPUB export.
        """
        from chai.models.epub_export import EPUBTemplate, EPUBExportConfig

        template_map = {
            ExportTemplate.SIMPLE: EPUBTemplate.SIMPLE,
            ExportTemplate.STANDARD: EPUBTemplate.STANDARD,
            ExportTemplate.DETAILED: EPUBTemplate.DETAILED,
            ExportTemplate.PUBLICATION: EPUBTemplate.DETAILED,
        }

        template = template_map.get(self.config.epub_template, EPUBTemplate.STANDARD)

        config = EPUBExportConfig(
            template=template,
            include_table_of_contents=True,
            include_css=True,
        )

        engine = EPUBManuscriptEngine(config=config)

        try:
            result = engine.export_to_file(novel, output_path)
            return ExportResult(
                format=ExportFormat.EPUB,
                status=ExportStatus.COMPLETED,
                output_path=str(output_path),
            )
        except Exception as e:
            return ExportResult(
                format=ExportFormat.EPUB,
                status=ExportStatus.FAILED,
                error_message=str(e),
            )

    def _export_pdf(
        self,
        novel: Novel,
        output_path: Path,
        request: FinalExportRequest,
    ) -> ExportResult:
        """Export to PDF format.

        Args:
            novel: The novel object.
            output_path: Output file path.
            request: The export request.

        Returns:
            ExportResult for PDF export.
        """
        from chai.models.pdf_export import PDFTemplate, PDFExportConfig

        template_map = {
            ExportTemplate.SIMPLE: PDFTemplate.SIMPLE,
            ExportTemplate.STANDARD: PDFTemplate.STANDARD,
            ExportTemplate.DETAILED: PDFTemplate.DETAILED,
            ExportTemplate.PUBLICATION: PDFTemplate.DETAILED,
        }

        template = template_map.get(self.config.pdf_template, PDFTemplate.STANDARD)

        config = PDFExportConfig(
            template=template,
            include_table_of_contents=True,
        )

        engine = PDFManuscriptEngine(config=config)

        try:
            result = engine.export_to_file(novel, output_path)
            return ExportResult(
                format=ExportFormat.PDF,
                status=ExportStatus.COMPLETED,
                output_path=str(output_path),
            )
        except Exception as e:
            return ExportResult(
                format=ExportFormat.PDF,
                status=ExportStatus.FAILED,
                error_message=str(e),
            )

    def validate_readiness(self, request: FinalExportRequest) -> ExportChecklist:
        """Check if the manuscript is ready for final export.

        Args:
            request: The export request.

        Returns:
            ExportChecklist with readiness status.
        """
        checklist = ExportChecklist()

        # Check manuscript completeness
        total_words = sum(
            c.get("word_count", 0)
            for v in request.volumes
            for c in v.get("chapters", [])
        )
        checklist.manuscript_complete = total_words >= 1000

        # Check all chapters written
        empty_chapters = 0
        for vol in request.volumes:
            for ch in vol.get("chapters", []):
                content = ch.get("content", "")
                if not content or len(content.strip()) < 100:
                    empty_chapters += 1

        checklist.all_chapters_written = empty_chapters == 0

        # Check self-check passed
        checklist.self_check_passed = (
            request.self_check_report is not None and
            request.self_check_report.get("passed", False)
        )

        # Check polishing complete
        checklist.polishing_complete = request.polishing_report is not None

        # Check validation passed (manual check)
        checklist.validation_passed = True

        # Check metadata complete
        checklist.metadata_complete = (
            bool(request.title) and
            bool(request.author) and
            len(request.volumes) > 0
        )

        # Collect missing items
        if not checklist.manuscript_complete:
            checklist.missing_items.append("稿件内容不足")

        if not checklist.all_chapters_written:
            checklist.missing_items.append(f"存在 {empty_chapters} 个空章节")

        if not checklist.metadata_complete:
            checklist.missing_items.append("元数据不完整")

        # Generate warnings
        if total_words < 5000:
            checklist.warnings.append("稿件字数较少，可能不适合出版")

        if not checklist.self_check_passed:
            checklist.warnings.append("建议运行自我检查")

        if not checklist.polishing_complete:
            checklist.warnings.append("建议进行全书润色")

        # Ready status
        checklist.ready_for_export = (
            checklist.manuscript_complete and
            checklist.all_chapters_written and
            checklist.metadata_complete
        )

        return checklist

    def get_summary(self, result: FinalExportResult) -> FinalExportSummary:
        """Generate a human-readable summary from export result.

        Args:
            result: The final export result.

        Returns:
            FinalExportSummary for display.
        """
        if not result.package:
            return FinalExportSummary(
                title=result.title,
                total_words=0,
                total_chapters=0,
                total_volumes=0,
                formats_exported=[],
                total_file_size="0 B",
                export_paths={},
                quality_score=0.0,
                validation_passed=False,
                issues_found=0,
                recommendation="导出失败",
                next_steps=["修复问题后重新导出"],
            )

        metadata = result.package.metadata
        validation = result.package.validation

        # Build export paths dict
        export_paths = {}
        if result.package.markdown_export and result.package.markdown_export.output_path:
            export_paths["markdown"] = result.package.markdown_export.output_path
        if result.package.epub_export and result.package.epub_export.output_path:
            export_paths["epub"] = result.package.epub_export.output_path
        if result.package.pdf_export and result.package.pdf_export.output_path:
            export_paths["pdf"] = result.package.pdf_export.output_path

        # Format file size
        total_size = result.total_file_size
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"

        # Generate recommendation
        if result.success:
            if validation and validation.quality_score >= 0.9:
                recommendation = "导出成功！稿件质量优秀，可以发布。"
            elif validation and validation.quality_score >= 0.7:
                recommendation = "导出成功！稿件质量良好，建议检查小问题后发布。"
            else:
                recommendation = "导出成功，但建议进行润色后重新导出以提高质量。"
        else:
            recommendation = "导出失败，请修复问题后重试。"

        # Generate next steps
        next_steps = []
        if result.success:
            next_steps.append("审阅导出的文件")
            next_steps.append("分享或发布作品")
        else:
            if validation and validation.critical_issues:
                next_steps.append("修复关键问题")
            next_steps.append("重新运行导出")

        return FinalExportSummary(
            title=result.title,
            total_words=metadata.total_words if metadata else 0,
            total_chapters=metadata.total_chapters if metadata else 0,
            total_volumes=metadata.total_volumes if metadata else 0,
            formats_exported=list(export_paths.keys()),
            total_file_size=size_str,
            export_paths=export_paths,
            quality_score=validation.quality_score if validation else 0.0,
            validation_passed=(
                validation.status == ValidationStatus.VALID if validation else False
            ),
            issues_found=validation.total_issues if validation else 0,
            recommendation=recommendation,
            next_steps=next_steps,
        )
