"""Tests for outline import engine."""

import pytest
import json

from chai.engines.outline_import_engine import OutlineImportEngine
from chai.models.outline_import import (
    ImportFormat,
    ImportSource,
    OutlineValidationStatus,
    ChapterWritingStatus,
)


class TestOutlineImportEngine:
    """Test cases for OutlineImportEngine."""

    @pytest.fixture
    def engine(self):
        """Create an OutlineImportEngine instance."""
        return OutlineImportEngine()

    @pytest.fixture
    def sample_json_outline(self):
        """Create a sample JSON outline."""
        return json.dumps({
            "title": "测试小说",
            "genre": "玄幻",
            "theme": "成长与冒险",
            "outline_type": "three_act",
            "target_word_count": 80000,
            "target_chapter_count": 24,
            "chapters": [
                {
                    "number": 1,
                    "title": "第一章：开始",
                    "summary": "主角出场",
                    "status": "complete",
                    "content": "这是第一章的完整内容。",
                    "word_count": 3000,
                },
                {
                    "number": 2,
                    "title": "第二章：转折",
                    "summary": "遇到导师",
                    "status": "pending",
                },
                {
                    "number": 3,
                    "title": "第三章：试炼",
                    "summary": "第一次考验",
                    "status": "partial",
                    "content": "这是部分内容。",
                    "word_count": 1500,
                },
                {
                    "number": 4,
                    "title": "第四章：成长",
                    "summary": "能力提升",
                    "status": "pending",
                },
            ],
            "plot_threads": [
                {
                    "name": "主线剧情",
                    "thread_type": "main",
                    "description": "主角的成长之路",
                    "chapters_active": [1, 2, 3, 4],
                },
                {
                    "name": "感情线",
                    "thread_type": "romantic",
                    "description": "与女主角的感情发展",
                    "chapters_active": [2, 3, 4],
                },
            ],
            "foreshadowing": [
                {
                    "element": "神秘符号",
                    "foreshadowing_type": "symbolic",
                    "chapter_planted": 1,
                    "chapter_payoff": 4,
                    "status": "planted",
                },
            ],
        })

    @pytest.fixture
    def sample_markdown_outline(self):
        """Create a sample Markdown outline."""
        return """# 测试小说

## 第一卷：起源

### 第1章：开始

- 主角在山村中出生
- 从小表现出异常天赋

### 第2章：转折

- 遇到云游老者
- 被带入修仙门派

## 第二卷：修炼

### 第3章：入门

- 正式成为外门弟子
- 结识同门师兄弟

### 第4章：试炼

- 第一次门派试炼
- 获得神秘传承
"""

    @pytest.fixture
    def sample_plain_text_outline(self):
        """Create a sample plain text outline."""
        return """第1章：开始
主角李凡在青云村出生，从小便展现出惊人的修炼天赋。某日，一位云游老者路过村庄，发现了他的特殊体质。

第2章：转折
老者将李凡带入玄天宗，他正式成为外门弟子。在宗门中，他结识了大师兄林风和师姐王雪。

第3章：试炼
李凡迎来了第一次门派试炼，在试炼中意外发现了一处上古遗迹，获得了神秘传承。

第4章：成长
通过神秘传承，李凡的修为突飞猛进，但他也因此引来了内门弟子的嫉妒。
"""

    @pytest.mark.asyncio
    async def test_import_json_outline(self, engine, sample_json_outline):
        """Test importing JSON format outline."""
        result = await engine.import_outline(
            content=sample_json_outline,
            import_format=ImportFormat.JSON,
            source=ImportSource.USER_FILE,
            original_file_name="outline.json",
        )

        assert result.success is True
        assert result.validation_status == OutlineValidationStatus.VALID
        assert result.total_chapters == 4
        assert result.completed_chapters == 1
        assert result.partial_chapters == 1
        assert result.pending_chapters == 2
        assert result.next_chapter_to_write == 2

    @pytest.mark.asyncio
    async def test_import_markdown_outline(self, engine, sample_markdown_outline):
        """Test importing Markdown format outline."""
        result = await engine.import_outline(
            content=sample_markdown_outline,
            import_format=ImportFormat.MARKDOWN,
            source=ImportSource.USER_FILE,
        )

        assert result.success is True
        assert result.total_chapters == 4
        assert result.next_chapter_to_write == 1

    @pytest.mark.asyncio
    async def test_import_plain_text_outline(self, engine, sample_plain_text_outline):
        """Test importing plain text format outline."""
        result = await engine.import_outline(
            content=sample_plain_text_outline,
            import_format=ImportFormat.PLAIN_TEXT,
            source=ImportSource.USER_FILE,
        )

        assert result.success is True
        assert result.total_chapters == 4

    @pytest.mark.asyncio
    async def test_import_invalid_json(self, engine):
        """Test importing invalid JSON."""
        result = await engine.import_outline(
            content="not valid json",
            import_format=ImportFormat.JSON,
        )

        assert result.success is False
        assert result.validation_status == OutlineValidationStatus.INVALID
        assert len(result.validation_errors) > 0

    @pytest.mark.asyncio
    async def test_chinese_number_conversion(self, engine):
        """Test Chinese number to integer conversion."""
        assert engine._chinese_to_number("一") == 1
        assert engine._chinese_to_number("十") == 10
        assert engine._chinese_to_number("一二") == 12
        assert engine._chinese_to_number("二十") == 20
        assert engine._chinese_to_number("一百") == 100

    def test_validate_raw_outline_complete(self, engine, sample_json_outline):
        """Test validation of complete outline."""
        import json
        from chai.models.outline_import import RawOutlineData

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            title=data["title"],
            genre=data["genre"],
            theme=data["theme"],
            chapters_data=data["chapters"],
            plot_threads_data=data.get("plot_threads", []),
            foreshadowing_data=data.get("foreshadowing", []),
        )

        result = engine._validate_raw_outline(raw)

        assert result["status"] == OutlineValidationStatus.VALID

    def test_validate_raw_outline_missing_title(self, engine):
        """Test validation with missing title."""
        from chai.models.outline_import import RawOutlineData

        raw = RawOutlineData(
            chapters_data=[
                {"number": 1, "title": "第一章"},
            ],
        )

        result = engine._validate_raw_outline(raw)

        assert result["status"] == OutlineValidationStatus.PARTIAL
        assert any("Title" in w for w in result.get("warnings", []))

    def test_validate_raw_outline_duplicate_chapters(self, engine):
        """Test validation with duplicate chapter numbers."""
        from chai.models.outline_import import RawOutlineData

        raw = RawOutlineData(
            chapters_data=[
                {"number": 1, "title": "第一章"},
                {"number": 1, "title": "也是第一章"},  # Duplicate
                {"number": 2, "title": "第二章"},
            ],
        )

        result = engine._validate_raw_outline(raw)

        assert len(result.get("warnings", [])) > 0

    def test_analyze_outline(self, engine, sample_json_outline):
        """Test outline analysis."""
        import json
        from chai.models.outline_import import RawOutlineData

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            chapters_data=data["chapters"],
        )

        analysis = engine._analyze_outline(raw)

        assert analysis["total_chapters"] == 4
        # Note: status comparison uses string values from JSON
        # Chapter 1: status="complete" but content length < 100 chars
        # Chapter 3: status="partial" and content length < 100 chars
        assert analysis["chapters_with_content"] == 0  # No chapter has content > 100 chars
        assert analysis["chapters_empty"] == 4
        assert analysis["writing_progress_percentage"] == 0.0

    def test_build_continuation_context(self, engine, sample_json_outline):
        """Test building continuation context."""
        import json
        from chai.models.outline_import import RawOutlineData

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            title=data["title"],
            genre=data["genre"],
            chapters_data=data["chapters"],
            plot_threads_data=data.get("plot_threads", []),
            foreshadowing_data=data.get("foreshadowing", []),
        )

        context = engine._build_continuation_context(raw)

        assert context["story_title"] == "测试小说"
        assert context["genre"] == "玄幻"
        # Chapter 1 is complete, so last_written is 1
        # Chapter 2 is pending with no content, so next_chapter is 2
        assert context["next_chapter"] == 2
        assert context["last_written_chapter"] == 1
        # All chapters are pending because content < 100 chars
        assert len(context["pending_chapters"]) == 4

    def test_convert_to_story_outline(self, engine, sample_json_outline):
        """Test converting import result to StoryOutline."""
        import json
        from chai.models.outline_import import RawOutlineData

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            title=data["title"],
            genre=data["genre"],
            theme=data["theme"],
            outline_type=data["outline_type"],
            chapters_data=data["chapters"],
            plot_threads_data=data.get("plot_threads", []),
            foreshadowing_data=data.get("foreshadowing", []),
        )

        from chai.models.outline_import import OutlineImportResult

        import_result = OutlineImportResult(
            success=True,
            outline_id="test_outline",
            import_format=ImportFormat.JSON,
            source=ImportSource.USER_FILE,
            validation_status=OutlineValidationStatus.VALID,
            total_chapters=4,
            raw_data=raw,
        )

        outline = engine.convert_to_story_outline(import_result)

        assert outline.title == "测试小说"
        assert outline.genre == "玄幻"
        assert outline.theme == "成长与冒险"
        assert len(outline.chapters) == 4
        assert len(outline.plot_threads) == 2
        assert len(outline.foreshadowing_elements) == 1

    def test_get_next_chapter_to_write(self, engine, sample_json_outline):
        """Test getting next chapter to write."""
        import json
        from chai.models.outline_import import RawOutlineData, OutlineImportResult

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(chapters_data=data["chapters"])

        import_result = OutlineImportResult(
            success=True,
            import_format=ImportFormat.JSON,
            source=ImportSource.USER_FILE,
            validation_status=OutlineValidationStatus.VALID,
            total_chapters=4,
            raw_data=raw,
        )

        next_chapter = engine.get_next_chapter_to_write(import_result)

        assert next_chapter is not None
        assert next_chapter.number == 2

    def test_get_continuation_context(self, engine, sample_json_outline):
        """Test getting continuation context."""
        import json
        from chai.models.outline_import import RawOutlineData, OutlineImportResult

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            title=data["title"],
            genre=data["genre"],
            chapters_data=data["chapters"],
            plot_threads_data=data.get("plot_threads", []),
            foreshadowing_data=data.get("foreshadowing", []),
        )

        import_result = OutlineImportResult(
            success=True,
            import_format=ImportFormat.JSON,
            source=ImportSource.USER_FILE,
            validation_status=OutlineValidationStatus.VALID,
            total_chapters=4,
            raw_data=raw,
        )

        context = engine.get_continuation_context(import_result)

        assert context.story_title == "测试小说"
        assert context.genre == "玄幻"
        # Chapter 1 is complete, so last_written is 1
        assert context.last_written_chapter == 1
        # All chapters have content < 100 chars, so all are pending
        assert len(context.pending_chapters) == 4

    def test_export_outline_summary(self, engine, sample_json_outline):
        """Test exporting outline summary."""
        import json
        from chai.models.outline_import import RawOutlineData, OutlineImportResult

        data = json.loads(sample_json_outline)
        raw = RawOutlineData(
            title=data["title"],
            genre=data["genre"],
            theme=data["theme"],
            chapters_data=data["chapters"],
        )

        import_result = OutlineImportResult(
            success=True,
            import_format=ImportFormat.JSON,
            source=ImportSource.USER_FILE,
            validation_status=OutlineValidationStatus.VALID,
            total_chapters=4,
            completed_chapters=1,
            partial_chapters=1,
            pending_chapters=2,
            writing_status_summary={"writing_progress_percentage": 50.0},
            next_chapter_to_write=2,
            continuation_context={"pending_chapters": [{"number": 2, "title": "第二章"}]},
            raw_data=raw,
        )

        summary = engine.export_outline_summary(import_result)

        assert "测试小说" in summary
        assert "章节概览" in summary
        assert "总章节数：4" in summary
        assert "写作进度：50.0%" in summary

    def test_parse_yaml_format(self, engine):
        """Test YAML format parsing."""
        yaml_content = """title: YAML测试小说
genre: 科幻
chapters:
  - number: 1
    title: 第一章
    summary: 星际启程
  - number: 2
    title: 第二章
    summary: 遭遇海盗
"""
        result = engine._parse_yaml(yaml_content)

        assert result["title"] == "YAML测试小说"
        assert result["genre"] == "科幻"
        assert len(result["chapters"]) == 2

    def test_chapter_patterns(self, engine):
        """Test various chapter patterns."""
        test_cases = [
            ("第1章：开始", True),
            ("第一章：开始", True),
            ("第123章：冒险", True),
            ("Chapter 1: Beginning", True),
            ("第1话：开始", True),
            ("第1卷：起源", False),  # This is a volume
            # Note: # 第一章 is handled by markdown parser, not CHAPTER_PATTERN
        ]

        for text, should_match in test_cases:
            matches = bool(engine.CHAPTER_PATTERN.match(text))
            assert matches == should_match, f"Pattern matching failed for: {text}"

    def test_volume_patterns(self, engine):
        """Test volume patterns."""
        test_cases = [
            ("第1卷：起源", True),
            ("第一卷：起源", True),
            ("Volume 1", True),
            ("第1部", True),
            ("第1章：开始", False),  # This is a chapter
        ]

        for text, should_match in test_cases:
            matches = bool(engine.VOLUME_PATTERN.match(text))
            assert matches == should_match, f"Volume pattern matching failed for: {text}"