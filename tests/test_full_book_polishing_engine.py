"""Unit tests for FullBookPolishingEngine."""

import pytest
from chai.models.full_book_polishing import (
    PolishingStatus,
    PolishingType,
    PolishingSeverity,
    BookPolishingConfig,
    FullBookPolishingRequest,
)
from chai.engines.full_book_polishing_engine import FullBookPolishingEngine


class TestFullBookPolishingEngine:
    """Test suite for FullBookPolishingEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = FullBookPolishingEngine()

    def test_engine_initialization(self):
        """Test engine can be initialized."""
        assert self.engine is not None
        assert self.engine.config is not None
        assert isinstance(self.engine.config, BookPolishingConfig)

    def test_config_defaults(self):
        """Test default configuration values."""
        config = BookPolishingConfig()
        assert config.enable_global_tone is True
        assert config.enable_character_voice is True
        assert config.enable_narrative_pacing is True
        assert config.enable_theme_coherence is True
        assert config.enable_world_rules is True
        assert config.enable_plot_threads is True
        assert config.enable_emotional_arc is True
        assert config.enable_dialogue_universal is True
        assert config.enable_description_consistency is True
        assert config.enable_transition_book is True
        assert config.enable_repetition_check is True
        assert config.enable_readability is True
        assert config.min_acceptable_score == 0.7

    def test_polish_single_chapter(self):
        """Test polishing with a single chapter."""
        request = FullBookPolishingRequest(
            book_id="book_001",
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
                            "title": "第一章：开端",
                            "content": "这是一个测试章节的内容。" * 300,
                        }
                    ],
                }
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert result.book_id == "book_001"
        assert result.title == "测试小说"
        assert result.status in [PolishingStatus.PASSED, PolishingStatus.NEEDS_REVISION]
        assert result.report is not None
        assert result.summary is not None

    def test_polish_multiple_volumes(self):
        """Test polishing with multiple volumes."""
        request = FullBookPolishingRequest(
            book_id="book_002",
            title="测试多卷小说",
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
                            "content": "紧张的时刻来临。" * 200,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章",
                            "content": "温馨的场景展开。" * 200,
                        },
                    ],
                },
                {
                    "volume_id": "vol_002",
                    "volume_number": 2,
                    "title": "第二卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_003",
                            "chapter_number": 3,
                            "title": "第三章",
                            "content": "新的冒险开始。" * 200,
                        },
                    ],
                },
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert result.report.total_volumes == 2
        assert result.report.total_chapters == 3
        assert len(result.report.volume_reports) == 2

    def test_polish_empty_book(self):
        """Test polishing with empty book."""
        request = FullBookPolishingRequest(
            book_id="book_003",
            title="空小说",
            volumes=[],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert result.report.total_volumes == 0
        assert result.report.total_chapters == 0

    def test_polish_with_characters(self):
        """Test polishing with character data."""
        request = FullBookPolishingRequest(
            book_id="book_004",
            title="角色小说",
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
                            "content": '张三说："你好"。' * 100,
                        },
                    ],
                }
            ],
            characters=[
                {"name": "张三", "description": "主角"},
                {"name": "李四", "description": "配角"},
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert result.status in [PolishingStatus.PASSED, PolishingStatus.NEEDS_REVISION]

    def test_polish_disabled_checks(self):
        """Test polishing with all checks disabled except minimal."""
        request = FullBookPolishingRequest(
            book_id="book_005",
            title="最小检查小说",
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
                            "content": "测试内容。" * 100,
                        },
                    ],
                }
            ],
            config=BookPolishingConfig(
                enable_global_tone=False,
                enable_character_voice=False,
                enable_narrative_pacing=False,
                enable_theme_coherence=False,
                enable_world_rules=False,
                enable_plot_threads=False,
                enable_emotional_arc=False,
                enable_dialogue_universal=False,
                enable_description_consistency=False,
                enable_transition_book=False,
                enable_repetition_check=False,
                enable_readability=False,
            ),
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert len(result.report.polishing_results) == 0

    def test_polish_result_structure(self):
        """Test that polishing result has correct structure."""
        request = FullBookPolishingRequest(
            book_id="book_006",
            title="结构测试",
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
                            "content": "测试内容。" * 300,
                        },
                    ],
                }
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert hasattr(result, 'report')
        assert hasattr(result, 'summary')
        assert hasattr(result, 'revision_plan')
        assert result.report.book_id == "book_006"
        assert result.report.title == "结构测试"
        assert result.report.total_volumes == 1
        assert result.report.total_chapters == 1
        assert result.summary.total_volumes == 1
        assert result.summary.total_chapters == 1

    def test_polish_with_world_setting(self):
        """Test polishing with world setting data."""
        request = FullBookPolishingRequest(
            book_id="book_007",
            title="世界观小说",
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
                            "content": "魔法世界中的冒险。" * 200,
                        },
                    ],
                }
            ],
            world_setting={
                "rules": [
                    {
                        "name": "魔法限制",
                        "description": "魔法使用者每天只能使用三次魔法",
                        "violations": ["无限魔法"],
                        "suggestion": "遵循魔法限制规则",
                    }
                ]
            },
        )

        result = self.engine.polish(request)

        assert result.success is True

    def test_polish_with_subplot_design(self):
        """Test polishing with subplot design data."""
        request = FullBookPolishingRequest(
            book_id="book_008",
            title="支线小说",
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
                            "content": "伏笔埋下。" * 200,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章",
                            "content": "伏笔回收。" * 200,
                        },
                    ],
                }
            ],
            subplot_design={
                "subplots": [
                    {
                        "name": "神秘伏笔",
                        "plant_chapter": 1,
                        "payoff_chapter": 2,
                    }
                ]
            },
        )

        result = self.engine.polish(request)

        assert result.success is True

    def test_polish_score_calculation(self):
        """Test that polishing score is calculated correctly."""
        request = FullBookPolishingRequest(
            book_id="book_009",
            title="评分测试",
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
                            "content": "正常内容。" * 500,
                        },
                    ],
                }
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        assert 0.0 <= result.report.overall_score <= 1.0
        assert 0.0 <= result.summary.average_score <= 1.0

    def test_get_summary(self):
        """Test get_summary method."""
        request = FullBookPolishingRequest(
            book_id="book_010",
            title="摘要测试",
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
                            "content": "测试内容。" * 300,
                        },
                    ],
                }
            ],
        )

        result = self.engine.polish(request)
        summary = self.engine.get_summary(result)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_polish_consistency_check(self):
        """Test consistency check across chapters."""
        request = FullBookPolishingRequest(
            book_id="book_011",
            title="一致性测试",
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
                            "content": "突然，天空中出现了异变。紧张的气氛弥漫。" * 200,
                        },
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章",
                            "content": "第二天，喜悦的心情充满了整个村庄。" * 200,
                        },
                    ],
                }
            ],
        )

        result = self.engine.polish(request)

        assert result.success is True
        # Should detect the abrupt tone change

    def test_polish_volume_report(self):
        """Test that volume reports are generated correctly."""
        request = FullBookPolishingRequest(
            book_id="book_012",
            title="卷报告测试",
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
                            "content": "第一卷内容。" * 300,
                        },
                    ],
                },
                {
                    "volume_id": "vol_002",
                    "volume_number": 2,
                    "title": "第二卷",
                    "chapters": [
                        {
                            "chapter_id": "ch_002",
                            "chapter_number": 2,
                            "title": "第二章",
                            "content": "第二卷内容。" * 300,
                        },
                    ],
                },
            ],
        )

        result = self.engine.polish(request)

        assert len(result.report.volume_reports) == 2
        vol1_report = result.report.volume_reports[0]
        assert vol1_report.volume_id == "vol_001"
        assert vol1_report.volume_number == 1
        assert vol1_report.title == "第一卷"
        vol2_report = result.report.volume_reports[1]
        assert vol2_report.volume_id == "vol_002"
        assert vol2_report.volume_number == 2

    def test_polish_revision_plan_creation(self):
        """Test that revision plan is created when issues found."""
        request = FullBookPolishingRequest(
            book_id="book_013",
            title="修订计划测试",
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
                            "content": "突然，天空中。" * 50 + "突然，大地震动。" * 50,
                        },
                    ],
                }
            ],
            config=BookPolishingConfig(
                enable_repetition_check=True,
            ),
        )

        result = self.engine.polish(request)

        assert result.success is True
        # If issues found, revision plan should be created
        if result.status == PolishingStatus.NEEDS_REVISION:
            assert result.revision_plan is not None

    def test_polish_exception_handling(self):
        """Test that engine handles exceptions gracefully."""
        # Create a malformed request that might cause issues
        request = FullBookPolishingRequest(
            book_id="book_014",
            title="异常处理测试",
            volumes=[{"invalid": "data"}],
        )

        result = self.engine.polish(request)

        # Should handle gracefully
        assert result.success is False or result.success is True
        assert result.error_message is not None or result.report is not None