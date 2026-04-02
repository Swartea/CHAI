"""Unit tests for FinalExportEngine."""

import pytest
from chai.models.final_export import (
    ExportFormat,
    ExportStatus,
    ValidationStatus,
    ExportQuality,
    ExportTemplate,
    FinalExportConfig,
    FinalExportRequest,
    FinalExportResult,
)
from chai.engines.final_export_engine import FinalExportEngine


class TestFinalExportEngine:
    """Test suite for FinalExportEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = FinalExportEngine()

    def test_engine_initialization(self):
        """Test engine can be initialized."""
        assert self.engine is not None
        assert self.engine.config is not None
        assert isinstance(self.engine.config, FinalExportConfig)

    def test_config_defaults(self):
        """Test default configuration values."""
        config = FinalExportConfig()
        assert ExportFormat.ALL in config.formats
        assert config.output_dir == "./output"
        assert config.quality == ExportQuality.FINAL
        assert config.template == ExportTemplate.STANDARD
        assert config.skip_validation is False
        assert config.fail_on_critical is True

    def test_validate_readiness_complete_manuscript(self):
        """Test readiness validation with complete manuscript."""
        request = FinalExportRequest(
            book_id="book_001",
            title="测试小说",
            author="测试作者",
            genre="玄幻",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章：开端",
                            "content": "这是一个测试章节的内容。" * 300,
                            "word_count": 4500,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章：发展",
                            "content": "这是第二个测试章节的内容。" * 300,
                            "word_count": 4500,
                        },
                    ],
                }
            ],
        )

        checklist = self.engine.validate_readiness(request)

        assert checklist.manuscript_complete is True
        assert checklist.all_chapters_written is True
        assert checklist.metadata_complete is True
        assert checklist.ready_for_export is True

    def test_validate_readiness_empty_chapters(self):
        """Test readiness validation with empty chapters."""
        request = FinalExportRequest(
            book_id="book_002",
            title="测试小说",
            author="测试作者",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章：开端",
                            "content": "这是一个测试章节的内容。" * 300,
                            "word_count": 4500,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章：空章节",
                            "content": "",
                            "word_count": 0,
                        },
                    ],
                }
            ],
        )

        checklist = self.engine.validate_readiness(request)

        assert checklist.manuscript_complete is True
        assert checklist.all_chapters_written is False
        assert "存在 1 个空章节" in checklist.missing_items

    def test_validate_readiness_insufficient_words(self):
        """Test readiness validation with insufficient word count."""
        request = FinalExportRequest(
            book_id="book_003",
            title="短篇",
            author="测试作者",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "很少的内容",
                            "word_count": 50,
                        },
                    ],
                }
            ],
        )

        checklist = self.engine.validate_readiness(request)

        assert checklist.manuscript_complete is False
        assert "稿件内容不足" in checklist.missing_items

    def test_validate_readiness_missing_metadata(self):
        """Test readiness validation with missing metadata."""
        request = FinalExportRequest(
            book_id="book_004",
            title="",
            author="",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 300,
                            "word_count": 4500,
                        },
                    ],
                }
            ],
        )

        checklist = self.engine.validate_readiness(request)

        assert checklist.metadata_complete is False

    def test_validate_manuscript_all_checks_pass(self):
        """Test manuscript validation with all checks passing."""
        request = FinalExportRequest(
            book_id="book_005",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 500,
                            "word_count": 7000,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章",
                            "content": "更多测试内容" * 500,
                            "word_count": 7000,
                        },
                    ],
                }
            ],
        )

        validation = self.engine._validate_manuscript(request)

        assert validation.status == ValidationStatus.VALID
        assert validation.word_count_check is True
        assert validation.chapter_completeness_check is True
        assert validation.structure_check is True
        assert validation.quality_score >= 0.8

    def test_validate_manuscript_critical_issues(self):
        """Test manuscript validation with critical issues."""
        request = FinalExportRequest(
            book_id="book_006",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "",
                            "word_count": 0,
                        },
                    ],
                }
            ],
        )

        validation = self.engine._validate_manuscript(request)

        assert validation.status == ValidationStatus.INVALID
        assert len(validation.critical_issues) > 0
        assert validation.chapter_completeness_check is False

    def test_validate_manuscript_low_word_count(self):
        """Test manuscript validation with low word count."""
        request = FinalExportRequest(
            book_id="book_007",
            title="测试",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "很少",
                            "word_count": 10,
                        },
                    ],
                }
            ],
        )

        validation = self.engine._validate_manuscript(request)

        assert validation.word_count_check is False
        assert len(validation.major_issues) > 0

    def test_validate_manuscript_no_volumes(self):
        """Test manuscript validation with no volumes."""
        request = FinalExportRequest(
            book_id="book_008",
            title="测试小说",
            volumes=[],
        )

        validation = self.engine._validate_manuscript(request)

        assert validation.structure_check is False
        assert len(validation.critical_issues) > 0

    def test_get_formats_to_export_all(self):
        """Test format list when ALL is specified."""
        config = FinalExportConfig(formats=[ExportFormat.ALL])
        engine = FinalExportEngine(config=config)

        formats = engine._get_formats_to_export()

        assert ExportFormat.MARKDOWN in formats
        assert ExportFormat.EPUB in formats
        assert ExportFormat.PDF in formats
        assert len(formats) == 3

    def test_get_formats_to_export_specific(self):
        """Test format list when specific formats are specified."""
        config = FinalExportConfig(formats=[ExportFormat.MARKDOWN])
        engine = FinalExportEngine(config=config)

        formats = engine._get_formats_to_export()

        assert formats == [ExportFormat.MARKDOWN]

    def test_build_novel_from_request(self):
        """Test building Novel object from request data."""
        request = FinalExportRequest(
            book_id="book_009",
            title="测试小说",
            author="测试作者",
            genre="玄幻",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "description": "测试卷描述",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章：开端",
                            "content": "第一章的内容" * 200,
                            "word_count": 2800,
                            "is_prologue": True,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章：发展",
                            "content": "第二章的内容" * 300,
                            "word_count": 4200,
                            "summary": "本章讲述...",
                        },
                    ],
                }
            ],
        )

        novel = self.engine._build_novel(request)

        assert novel.id == "book_009"
        assert novel.title == "测试小说"
        assert novel.genre == "玄幻"
        assert len(novel.volumes) == 1
        assert len(novel.volumes[0].chapters) == 2
        assert novel.volumes[0].chapters[0].is_prologue is True
        assert novel.volumes[0].chapters[1].summary == "本章讲述..."

    def test_export_markdown_only(self):
        """Test exporting to markdown only."""
        request = FinalExportRequest(
            book_id="book_010",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 500,
                            "word_count": 7000,
                        },
                    ],
                }
            ],
        )

        config = FinalExportConfig(
            formats=[ExportFormat.MARKDOWN],
            output_dir="/tmp/test_export",
        )
        engine = FinalExportEngine(config=config)

        result = engine.export(request)

        assert result.success is True
        assert result.total_formats >= 1
        assert result.successful_formats >= 1

    def test_export_validation_fails_on_critical(self):
        """Test that export fails when fail_on_critical is True and critical issues exist."""
        request = FinalExportRequest(
            book_id="book_011",
            title="测试",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "",
                            "word_count": 0,
                        },
                    ],
                }
            ],
        )

        config = FinalExportConfig(fail_on_critical=True)
        engine = FinalExportEngine(config=config)

        result = engine.export(request)

        assert result.success is False
        assert result.error_message == "Critical validation issues found"

    def test_get_summary(self):
        """Test generating summary from export result."""
        from chai.models.final_export import ExportPackage, ExportMetadata

        result = FinalExportResult(
            success=True,
            export_id="export_001",
            title="测试小说",
            status=ExportStatus.COMPLETED,
            total_formats=3,
            successful_formats=3,
            failed_formats=0,
            total_file_size=1024 * 1024,
            package=ExportPackage(
                package_id="export_001",
                title="测试小说",
                metadata=ExportMetadata(
                    title="测试小说",
                    total_words=100000,
                    total_chapters=50,
                    total_volumes=2,
                    quality_score=0.95,
                ),
                validation=self.engine._validate_manuscript(FinalExportRequest(
                    book_id="test",
                    title="测试小说",
                    volumes=[{
                        "volume_id": "v1",
                        "volume_number": 1,
                        "title": "第一卷",
                        "chapters": [{
                            "chapter_id": "c1",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "x" * 500,
                            "word_count": 500,
                        }],
                    }],
                )),
            ),
        )

        summary = self.engine.get_summary(result)

        assert summary.title == "测试小说"
        assert summary.total_words == 100000
        assert summary.total_chapters == 50
        assert summary.total_volumes == 2
        assert len(summary.formats_exported) >= 0

    def test_export_with_polishing_report(self):
        """Test export with polishing report included."""
        request = FinalExportRequest(
            book_id="book_012",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 500,
                            "word_count": 7000,
                        },
                    ],
                }
            ],
            polishing_report={"passed": True, "score": 0.9},
        )

        config = FinalExportConfig(
            formats=[ExportFormat.MARKDOWN],
            output_dir="/tmp/test_export",
        )
        engine = FinalExportEngine(config=config)

        result = engine.export(request)

        assert result.success is True
        if result.package and result.package.metadata:
            assert result.package.metadata.polishing_applied is True

    def test_export_with_self_check_report(self):
        """Test export with self-check report included."""
        request = FinalExportRequest(
            book_id="book_013",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 500,
                            "word_count": 7000,
                        },
                    ],
                }
            ],
            self_check_report={"passed": True, "issues": []},
        )

        config = FinalExportConfig(
            formats=[ExportFormat.MARKDOWN],
            output_dir="/tmp/test_export",
        )
        engine = FinalExportEngine(config=config)

        result = engine.export(request)

        assert result.success is True
        if result.package and result.package.metadata:
            assert result.package.metadata.self_check_passed is True

    def test_export_with_characters(self):
        """Test export with character list."""
        request = FinalExportRequest(
            book_id="book_014",
            title="测试小说",
            volumes=[
                {
                    "volume_id": "vol_001",
                    "volume_number": 1,
                    "title": "第一卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_001",
                            "chapter_number": 1,
                            "title": "第一章",
                            "content": "测试内容" * 500,
                            "word_count": 7000,
                        },
                    ],
                }
            ],
            characters=[
                {"name": "张三", "role": "主角"},
                {"name": "李四", "role": "配角"},
            ],
        )

        config = FinalExportConfig(
            formats=[ExportFormat.MARKDOWN],
            output_dir="/tmp/test_export",
        )
        engine = FinalExportEngine(config=config)

        result = engine.export(request)

        assert result.success is True
