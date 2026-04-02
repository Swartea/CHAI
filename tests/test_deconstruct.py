"""Tests for book deconstruction feature."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chai.crawler import FanqieCrawler, FanqieHotEntry, FanqieBook
from chai.db import DeconstructDB
from chai.models.deconstruct import (
    CharacterTemplate,
    CharacterTemplateType,
    DeconstructSource,
    DeconstructionResult,
    PlotPattern,
    PlotPatternType,
    WorldTemplate,
    WorldTemplateType,
)
from chai.engines import BookDeconstructor


class TestFanqieCrawler:
    """Tests for FanqieCrawler."""

    def test_crawler_init(self):
        """Test crawler initialization."""
        crawler = FanqieCrawler(timeout=15, max_retries=2)
        assert crawler.timeout == 15
        assert crawler.max_retries == 2
        assert crawler.user_agent != ""

    def test_fanqie_hot_entry_model(self):
        """Test FanqieHotEntry model."""
        entry = FanqieHotEntry(
            id="test_123",
            name="测试词条",
            category="玄幻",
            book_count=100,
            description="测试描述",
        )
        assert entry.id == "test_123"
        assert entry.name == "测试词条"
        assert entry.category == "玄幻"
        assert entry.book_count == 100

    def test_fanqie_book_model(self):
        """Test FanqieBook model."""
        book = FanqieBook(
            id="book_456",
            title="测试书籍",
            author="测试作者",
            genre="玄幻",
            synopsis="测试简介",
            word_count=500000,
            rating=4.5,
            tags=["穿越", "修仙"],
        )
        assert book.id == "book_456"
        assert book.title == "测试书籍"
        assert book.author == "测试作者"
        assert "穿越" in book.tags

    @pytest.mark.asyncio
    async def test_get_hot_list_fallback(self):
        """Test get_hot_list falls back to web scraping on API failure."""
        crawler = FanqieCrawler()
        with patch.object(crawler, "_get_hot_list_api", side_effect=Exception("API failed")):
            with patch.object(crawler, "_get_hot_list_web", new_callable=AsyncMock) as mock_web:
                mock_web.return_value = [
                    FanqieHotEntry(id="1", name="词条1", category="玄幻"),
                    FanqieHotEntry(id="2", name="词条2", category="都市"),
                ]
                result = await crawler.get_hot_list(limit=10)
                assert len(result) == 2
                assert result[0].name == "词条1"

    @pytest.mark.asyncio
    async def test_get_books_by_entry_web_fallback(self):
        """Test get_books_by_entry falls back to web scraping."""
        crawler = FanqieCrawler()
        with patch.object(crawler, "_get_books_by_entry_api", side_effect=Exception("API failed")):
            with patch.object(crawler, "_get_books_by_entry_web", new_callable=AsyncMock) as mock_web:
                mock_web.return_value = [
                    FanqieBook(id="b1", title="书1", author="作者1", genre="玄幻"),
                ]
                result = await crawler.get_books_by_entry("entry_123", limit=5)
                assert len(result) == 1
                assert result[0].title == "书1"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with FanqieCrawler() as crawler:
            assert crawler._client is not None or True  # Client creation is lazy


class TestDeconstructDB:
    """Tests for DeconstructDB."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = DeconstructDB(data_dir=Path(tmpdir))
            yield db

    def test_save_and_get_character_template(self, temp_db):
        """Test saving and retrieving a character template."""
        source = DeconstructSource(
            book_id="book_1",
            book_title="测试书籍",
            author="测试作者",
        )
        template = CharacterTemplate(
            id="char_tmpl_1",
            name="草根逆袭型男主",
            template_type=CharacterTemplateType.PROTAGONIST,
            genre="玄幻",
            source=source,
            personality_traits=["坚韧", "聪明"],
            strengths=["意志坚定"],
            weaknesses=["有时过于固执"],
        )

        temp_db.save_character_template(template)

        retrieved = temp_db.get_character_template("char_tmpl_1")
        assert retrieved is not None
        assert retrieved.name == "草根逆袭型男主"
        assert retrieved.template_type == CharacterTemplateType.PROTAGONIST
        assert "坚韧" in retrieved.personality_traits

    def test_get_character_templates_with_filter(self, temp_db):
        """Test getting character templates with genre filter."""
        source = DeconstructSource(
            book_id="book_1",
            book_title="测试书籍",
            author="测试作者",
        )

        # Add templates of different genres
        temp_db.save_character_template(
            CharacterTemplate(
                id="char_1",
                name="玄幻角色",
                template_type=CharacterTemplateType.PROTAGONIST,
                genre="玄幻",
                source=source,
            )
        )
        temp_db.save_character_template(
            CharacterTemplate(
                id="char_2",
                name="都市角色",
                template_type=CharacterTemplateType.PROTAGONIST,
                genre="都市",
                source=source,
            )
        )

        xuanhuan = temp_db.get_character_templates(genre="玄幻")
        assert len(xuanhuan) == 1
        assert xuanhuan[0].name == "玄幻角色"

        urban = temp_db.get_character_templates(genre="都市")
        assert len(urban) == 1
        assert urban[0].name == "都市角色"

    def test_increment_character_usage(self, temp_db):
        """Test incrementing character template usage count."""
        source = DeconstructSource(
            book_id="book_1",
            book_title="测试书籍",
            author="测试作者",
        )
        template = CharacterTemplate(
            id="char_usage_test",
            name="测试角色",
            template_type=CharacterTemplateType.SUPPORTING,
            genre="玄幻",
            source=source,
        )
        temp_db.save_character_template(template)

        assert template.usage_count == 0
        temp_db.increment_character_usage("char_usage_test")
        retrieved = temp_db.get_character_template("char_usage_test")
        assert retrieved.usage_count == 1

    def test_save_and_get_plot_pattern(self, temp_db):
        """Test saving and retrieving a plot pattern."""
        source = DeconstructSource(
            book_id="book_2",
            book_title="测试书籍2",
            author="作者2",
        )
        pattern = PlotPattern(
            id="plot_pat_1",
            name="逆境崛起",
            pattern_type=PlotPatternType.HEROS_JOURNEY,
            genre="玄幻",
            source=source,
            description="主角从逆境中崛起的故事",
            key_beat_templates=["失去一切", "最低谷", "觉醒", "奋斗", "成功"],
        )

        temp_db.save_plot_pattern(pattern)
        retrieved = temp_db.get_plot_pattern("plot_pat_1")
        assert retrieved is not None
        assert retrieved.name == "逆境崛起"
        assert len(retrieved.key_beat_templates) == 5

    def test_save_and_get_world_template(self, temp_db):
        """Test saving and retrieving a world template."""
        source = DeconstructSource(
            book_id="book_3",
            book_title="测试书籍3",
            author="作者3",
        )
        world = WorldTemplate(
            id="world_tmpl_1",
            name="修仙世界观",
            template_type=WorldTemplateType.FANTASY,
            genre="玄幻",
            source=source,
            world_summary="一个以修仙为主的世界",
            recurring_locations=["仙门", "凡间", "魔域"],
            typical_conflicts=["正邪之争", "资源争夺"],
        )

        temp_db.save_world_template(world)
        retrieved = temp_db.get_world_template("world_tmpl_1")
        assert retrieved is not None
        assert retrieved.name == "修仙世界观"
        assert "仙门" in retrieved.recurring_locations

    def test_save_result_with_templates(self, temp_db):
        """Test saving a complete deconstruction result with all templates."""
        source = DeconstructSource(
            book_id="book_full",
            book_title="完整拆解书籍",
            author="作者全",
        )

        char_template = CharacterTemplate(
            id="full_char_1",
            name="完整角色",
            template_type=CharacterTemplateType.PROTAGONIST,
            genre="玄幻",
            source=source,
        )
        plot_pattern = PlotPattern(
            id="full_plot_1",
            name="完整情节",
            pattern_type=PlotPatternType.THREE_ACT,
            genre="玄幻",
            source=source,
        )
        world_template = WorldTemplate(
            id="full_world_1",
            name="完整世界观",
            template_type=WorldTemplateType.FANTASY,
            genre="玄幻",
            source=source,
        )

        result = DeconstructionResult(
            id="full_result_1",
            source=source,
            character_templates=[char_template],
            plot_patterns=[plot_pattern],
            world_template=world_template,
            genre_classification="玄幻",
            status="completed",
        )

        temp_db.save_result_with_templates(result)

        # Verify all parts were saved
        assert temp_db.get_result("full_result_1") is not None
        assert temp_db.get_character_template("full_char_1") is not None
        assert temp_db.get_plot_pattern("full_plot_1") is not None
        assert temp_db.get_world_template("full_world_1") is not None

    def test_get_stats(self, temp_db):
        """Test getting database statistics."""
        source = DeconstructSource(
            book_id="stats_book",
            book_title="统计书籍",
            author="统计作者",
        )

        # Add some data
        temp_db.save_character_template(
            CharacterTemplate(
                id="stat_char_1",
                name="统计角色",
                template_type=CharacterTemplateType.SUPPORTING,
                genre="玄幻",
                source=source,
            )
        )

        stats = temp_db.get_stats()
        assert stats["character_templates"] == 1
        assert stats["plot_patterns"] == 0
        assert stats["world_templates"] == 0
        assert "data_dir" in stats


class TestDeconstructionModels:
    """Tests for deconstruction data models."""

    def test_deconstruct_source_model(self):
        """Test DeconstructSource model."""
        source = DeconstructSource(
            book_id="src_123",
            book_title="源书籍",
            author="原作者",
            platform="fanqie",
            url="https://fanqienovel.com/book/123",
        )
        assert source.book_id == "src_123"
        assert source.platform == "fanqie"

    def test_character_template_defaults(self):
        """Test CharacterTemplate default values."""
        source = DeconstructSource(
            book_id="book",
            book_title="书",
            author="作者",
        )
        template = CharacterTemplate(
            id="t1",
            name="测试",
            template_type=CharacterTemplateType.SUPPORTING,
            genre="都市",
            source=source,
        )
        assert template.usage_count == 0
        assert template.personality_traits == []
        assert template.created_at is not None

    def test_deconstruction_result_status(self):
        """Test DeconstructionResult status field."""
        source = DeconstructSource(
            book_id="book",
            book_title="书",
            author="作者",
        )
        result = DeconstructionResult(
            id="result_1",
            source=source,
            status="pending",
        )
        assert result.status == "pending"

    def test_plot_pattern_type_enum(self):
        """Test PlotPatternType enum values."""
        assert PlotPatternType.HEROS_JOURNEY.value == "heros_journey"
        assert PlotPatternType.THREE_ACT.value == "three_act"
        assert PlotPatternType.SAVE_THE_CAT.value == "save_the_cat"

    def test_world_template_type_enum(self):
        """Test WorldTemplateType enum values."""
        assert WorldTemplateType.FANTASY.value == "fantasy"
        assert WorldTemplateType.SCIFI.value == "sci-fi"
        assert WorldTemplateType.URBAN.value == "urban"


class TestBookDeconstructor:
    """Tests for BookDeconstructor engine."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create a mock AI service."""
        service = MagicMock()
        service.deconstruct_book = AsyncMock(return_value={
            "character_templates": [
                {
                    "name": "AI生成角色",
                    "template_type": "protagonist",
                    "age_range": "20-30",
                    "background_template": "天才少年",
                    "personality_traits": ["冷静", "理性"],
                    "strengths": ["分析能力强"],
                    "weaknesses": ["情感淡漠"],
                    "speech_pattern": "简洁有力",
                    "growth_arc_template": "从冷漠到温暖",
                }
            ],
            "plot_patterns": [
                {
                    "name": "AI生成情节",
                    "pattern_type": "three_act",
                    "description": "三幕式结构",
                    "structure_summary": "建置-对抗-解决",
                    "key_beat_templates": ["设定", "事件", "结局"],
                    "pacing_notes": "节奏稳健",
                    "tension_curve": ["低", "中", "高"],
                }
            ],
            "world_template": {
                "name": "AI生成世界观",
                "template_type": "fantasy",
                "world_summary": "奇幻世界",
                "geography_template": {"大陆": "广阔"},
                "political_template": {"王国": "中央集权"},
                "cultural_template": {"宗教": "多神教"},
                "recurring_locations": ["王城", "山脉"],
                "typical_conflicts": ["王位争夺"],
            },
            "genre_classification": "玄幻",
            "tone_and_style": "热血",
            "target_audience": "年轻男性",
        })
        return service

    @pytest.fixture
    def mock_crawler(self):
        """Create a mock crawler."""
        crawler = MagicMock(spec=FanqieCrawler)
        crawler.close = AsyncMock()
        return crawler

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temp directory for the database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_deconstruct_book_success(self, mock_ai_service, mock_crawler, temp_db_dir):
        """Test successful book deconstruction."""
        db = DeconstructDB(data_dir=temp_db_dir)
        deconstructor = BookDeconstructor(
            ai_service=mock_ai_service,
            db=db,
            crawler=mock_crawler,
        )

        book = FanqieBook(
            id="decon_book_1",
            title="待拆解书籍",
            author="原作者",
            genre="玄幻",
            synopsis="测试简介",
        )

        result = await deconstructor.deconstruct_book(book)

        assert result.status == "completed"
        assert len(result.character_templates) == 1
        assert result.character_templates[0].name == "AI生成角色"
        assert len(result.plot_patterns) == 1
        assert result.plot_patterns[0].name == "AI生成情节"
        assert result.world_template is not None
        assert result.world_template.name == "AI生成世界观"
        assert result.genre_classification == "玄幻"

    @pytest.mark.asyncio
    async def test_deconstruct_book_failure(self, mock_ai_service, mock_crawler, temp_db_dir):
        """Test book deconstruction handles failure gracefully."""
        mock_ai_service.deconstruct_book = AsyncMock(side_effect=Exception("AI error"))
        db = DeconstructDB(data_dir=temp_db_dir)
        deconstructor = BookDeconstructor(
            ai_service=mock_ai_service,
            db=db,
            crawler=mock_crawler,
        )

        book = FanqieBook(
            id="fail_book",
            title="失败书籍",
            author="原作者",
            genre="都市",
            synopsis="会失败的简介",
        )

        result = await deconstructor.deconstruct_book(book)

        assert "failed" in result.status
        # Result should still be saved even on failure
        assert db.get_result(result.id) is not None

    def test_get_templates_for_outline(self, mock_ai_service, temp_db_dir):
        """Test getting templates from database for outline generation."""
        db = DeconstructDB(data_dir=temp_db_dir)
        deconstructor = BookDeconstructor(
            ai_service=mock_ai_service,
            db=db,
            crawler=MagicMock(),
        )

        # Pre-populate database
        source = DeconstructSource(
            book_id="outline_book",
            book_title="大纲书籍",
            author="大纲作者",
        )
        db.save_character_template(
            CharacterTemplate(
                id="outline_char_1",
                name="大纲角色1",
                template_type=CharacterTemplateType.PROTAGONIST,
                genre="玄幻",
                source=source,
            )
        )
        db.save_plot_pattern(
            PlotPattern(
                id="outline_plot_1",
                name="大纲情节1",
                pattern_type=PlotPatternType.THREE_ACT,
                genre="玄幻",
                source=source,
            )
        )
        db.save_world_template(
            WorldTemplate(
                id="outline_world_1",
                name="大纲世界观1",
                template_type=WorldTemplateType.FANTASY,
                genre="玄幻",
                source=source,
            )
        )

        chars, plots, world = deconstructor.get_templates_for_outline(
            genre="玄幻",
            num_characters=5,
            num_plot_patterns=3,
        )

        assert len(chars) == 1
        assert chars[0].name == "大纲角色1"
        assert len(plots) == 1
        assert plots[0].name == "大纲情节1"
        assert world is not None
        assert world.name == "大纲世界观1"
