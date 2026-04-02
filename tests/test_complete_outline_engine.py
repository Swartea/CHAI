"""Unit tests for CompleteOutlineEngine."""

import asyncio
import pytest
from chai.engines.complete_outline_engine import CompleteOutlineEngine
from chai.models.complete_outline import (
    CompleteOutlineMode,
    CompleteOutlineStatus,
    CompleteOutlineGenerationConfig,
    CompleteOutlineRequest,
    CompleteOutlineComponents,
    VolumeOutlinePlan,
    ChapterOutlinePlan,
    SubplotOutlinePlan,
    ForeshadowingOutlinePlan,
    ClimaxOutlinePlan,
    EndingOutlinePlan,
)


class TestCompleteOutlineEngine:
    """Test cases for CompleteOutlineEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CompleteOutlineEngine()

    def test_initialization(self):
        """Test engine initialization."""
        assert self.engine is not None
        assert self.engine.outline_import_engine is not None
        # Without AI service, these should be None
        assert self.engine.story_outline_engine is None
        assert self.engine.main_structure_engine is None
        assert self.engine.chapter_synopsis_engine is None
        assert self.engine.subplot_engine is None
        assert self.engine.climax_engine is None

    def test_create_request_with_defaults(self):
        """Test creating a complete outline request with defaults."""
        request = CompleteOutlineRequest(
            project_id="test_project_1",
            project_title="测试小说",
            project_type="xianhua",
            theme="修仙成神",
        )

        assert request.project_id == "test_project_1"
        assert request.project_title == "测试小说"
        assert request.config.mode == CompleteOutlineMode.GENERATE

    def test_create_request_with_custom_config(self):
        """Test creating a request with custom configuration."""
        config = CompleteOutlineGenerationConfig(
            mode=CompleteOutlineMode.GENERATE,
            target_volumes=2,
            target_chapters=30,
            target_word_count=100000,
            include_subplots=True,
            include_foreshadowing=True,
            include_climax=True,
            include_ending=True,
            outline_structure="three_act",
        )

        request = CompleteOutlineRequest(
            project_id="test_project_2",
            project_title="另一部小说",
            project_type="yuanman",
            theme="玄幻冒险",
            config=config,
        )

        assert request.config.target_volumes == 2
        assert request.config.target_chapters == 30
        assert request.config.include_subplots is True

    def test_create_request_with_import_mode(self):
        """Test creating an import mode request."""
        import_content = '{"title": "导入小说", "chapters": [{"number": 1, "title": "第一章"}]}'

        request = CompleteOutlineRequest(
            project_id="test_import",
            project_title="导入小说",
            project_type="dushi",
            theme="都市生活",
            config=CompleteOutlineGenerationConfig(mode=CompleteOutlineMode.IMPORT),
            import_content=import_content,
            import_format="json",
        )

        assert request.config.mode == CompleteOutlineMode.IMPORT
        assert request.import_content is not None
        assert request.import_format == "json"

    def test_validate_outline_with_empty_components(self):
        """Test validation with empty components."""
        components = CompleteOutlineComponents()
        result = self.engine.validate_outline(components)

        assert result.is_valid is False
        assert result.errors >= 1  # Missing chapters is an error
        assert len(result.issues) >= 1

    def test_validate_outline_with_valid_components(self):
        """Test validation with valid components."""
        components = CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=10,
                    chapter_start=1,
                    chapter_end=10,
                    status="generated",
                )
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    synopsis=f"第{i}章概要",
                    word_count_target=3000,
                    status="generated",
                )
                for i in range(1, 11)
            ],
            subplots=[
                SubplotOutlinePlan(
                    subplot_id="sub_1",
                    subplot_type="romantic",
                    description="感情线",
                    chapters_involved=list(range(1, 11)),
                    status="generated",
                )
            ],
            foreshadowing=[
                ForeshadowingOutlinePlan(
                    foreshadowing_id="fore_1",
                    element="神秘元素",
                    chapter_planted=3,
                    chapter_payoff=9,
                    status="generated",
                )
            ],
            climax=[
                ClimaxOutlinePlan(
                    climax_id="climax_1",
                    climax_type="final_climax",
                    chapter_location=9,
                    description="高潮场景",
                    status="generated",
                )
            ],
            ending=EndingOutlinePlan(
                ending_id="ending_1",
                ending_type="clean_resolution",
                chapter_location=10,
                description="圆满结局",
                status="generated",
            ),
        )

        result = self.engine.validate_outline(components)

        assert result.is_valid is True
        assert result.errors == 0

    def test_validate_outline_with_missing_chapters(self):
        """Test validation catches missing chapter numbers."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=1,
                    chapter_title="第一章",
                    volume_index=1,
                    status="generated",
                ),
                ChapterOutlinePlan(
                    chapter_number=3,  # Missing chapter 2
                    chapter_title="第三章",
                    volume_index=1,
                    status="generated",
                ),
            ],
        )

        result = self.engine.validate_outline(components)

        assert result.is_valid is False
        assert any("missing_chapters" in i.issue_type for i in result.issues)

    def test_validate_outline_with_duplicate_chapters(self):
        """Test validation catches duplicate chapter numbers."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=1,
                    chapter_title="第一章",
                    volume_index=1,
                    status="generated",
                ),
                ChapterOutlinePlan(
                    chapter_number=1,  # Duplicate
                    chapter_title="另一版本的第一章",
                    volume_index=1,
                    status="generated",
                ),
            ],
        )

        result = self.engine.validate_outline(components)

        assert result.is_valid is False
        assert any("duplicate" in i.issue_type.lower() for i in result.issues)

    def test_validate_outline_with_early_climax(self):
        """Test validation warns about early climax."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    status="generated",
                )
                for i in range(1, 21)
            ],
            climax=[
                ClimaxOutlinePlan(
                    climax_id="climax_early",
                    climax_type="main_climax",
                    chapter_location=5,  # Too early for 20 chapters
                    description="过早的高潮",
                    status="generated",
                )
            ],
        )

        result = self.engine.validate_outline(components)

        assert result.warnings >= 1
        assert any("climax" in i.issue_type.lower() for i in result.issues)

    def test_get_next_chapter_with_empty_components(self):
        """Test getting next chapter from empty outline."""
        components = CompleteOutlineComponents()
        result = self.engine.get_next_chapter(components)

        assert result is None

    def test_get_next_chapter_with_all_written(self):
        """Test getting next chapter when all are written."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    status="generated",
                )
                for i in range(1, 5)
            ],
        )

        result = self.engine.get_next_chapter(components, written_chapters=[1, 2, 3, 4])

        assert result is None

    def test_get_next_chapter_with_partial_written(self):
        """Test getting next chapter with some written."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    synopsis=f"第{i}章内容",
                    word_count_target=3000,
                    status="generated",
                )
                for i in range(1, 5)
            ],
            foreshadowing=[
                ForeshadowingOutlinePlan(
                    foreshadowing_id="fore_1",
                    element="伏笔元素",
                    chapter_planted=1,
                    chapter_payoff=3,
                    status="generated",
                )
            ],
        )

        result = self.engine.get_next_chapter(components, written_chapters=[1, 2])

        assert result is not None
        assert result.chapter_number == 3
        assert result.chapter_title == "第3章"
        assert len(result.foreshadowing_active) == 1

    def test_get_next_chapter_with_no_written(self):
        """Test getting next chapter when none are written."""
        components = CompleteOutlineComponents(
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    synopsis=f"第{i}章概要",
                    word_count_target=3000,
                    status="generated",
                )
                for i in range(1, 4)
            ],
        )

        result = self.engine.get_next_chapter(components)

        assert result is not None
        assert result.chapter_number == 1
        assert result.previous_chapter_summary == ""

    def test_get_summary(self):
        """Test getting outline summary."""
        components = CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=10,
                    chapter_start=1,
                    chapter_end=10,
                    status="generated",
                )
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    word_count_target=3000,
                    status="generated",
                )
                for i in range(1, 11)
            ],
            subplots=[
                SubplotOutlinePlan(
                    subplot_id="sub_1",
                    subplot_type="romantic",
                    description="感情线",
                    chapters_involved=list(range(1, 11)),
                    status="generated",
                )
            ],
            foreshadowing=[
                ForeshadowingOutlinePlan(
                    foreshadowing_id="fore_1",
                    element="伏笔",
                    chapter_planted=2,
                    chapter_payoff=9,
                    status="generated",
                )
            ],
            climax=[
                ClimaxOutlinePlan(
                    climax_id="climax_1",
                    climax_type="final_climax",
                    chapter_location=9,
                    description="高潮",
                    status="generated",
                )
            ],
            ending=EndingOutlinePlan(
                ending_id="ending_1",
                ending_type="clean_resolution",
                chapter_location=10,
                description="结局",
                status="generated",
            ),
        )

        summary = self.engine.get_summary(components, "测试小说")

        assert summary.project_title == "测试小说"
        assert summary.volume_count == 1
        assert summary.chapter_count == 10
        assert summary.subplot_count == 1
        assert summary.foreshadowing_count == 1
        assert summary.climax_count == 1
        assert summary.has_ending is True
        assert summary.word_count_target == 30000

    def test_export_outline_package(self):
        """Test exporting outline as package."""
        components = CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=2,
                    chapter_start=1,
                    chapter_end=2,
                    volume_summary="卷概要",
                    status="generated",
                )
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=1,
                    chapter_title="第一章",
                    volume_index=1,
                    synopsis="章概要",
                    word_count_target=3000,
                    scenes=["场景1", "场景2"],
                    plot_threads=["主线"],
                    foreshadowing=["fore_1"],
                    status="generated",
                ),
                ChapterOutlinePlan(
                    chapter_number=2,
                    chapter_title="第二章",
                    volume_index=1,
                    synopsis="章概要2",
                    word_count_target=3000,
                    status="generated",
                ),
            ],
            subplots=[
                SubplotOutlinePlan(
                    subplot_id="sub_1",
                    subplot_type="romantic",
                    description="感情线",
                    chapters_involved=[1, 2],
                    status="generated",
                )
            ],
            foreshadowing=[
                ForeshadowingOutlinePlan(
                    foreshadowing_id="fore_1",
                    element="伏笔元素",
                    chapter_planted=1,
                    chapter_payoff=2,
                    status="generated",
                )
            ],
            climax=[
                ClimaxOutlinePlan(
                    climax_id="climax_1",
                    climax_type="final_climax",
                    chapter_location=2,
                    description="高潮",
                    status="generated",
                )
            ],
            ending=EndingOutlinePlan(
                ending_id="ending_1",
                ending_type="clean_resolution",
                chapter_location=2,
                description="结局",
                status="generated",
            ),
        )

        package = self.engine.export_outline_package(components, "test_project")

        assert package["project_id"] == "test_project"
        assert "created_at" in package
        assert len(package["volumes"]) == 1
        assert len(package["chapters"]) == 2
        assert len(package["subplots"]) == 1
        assert len(package["foreshadowing"]) == 1
        assert len(package["climax"]) == 1
        assert package["ending"] is not None

    def test_create_complete_outline_import_mode_no_content(self):
        """Test that import mode fails without content."""
        request = CompleteOutlineRequest(
            project_id="test_import_no_content",
            project_title="导入测试",
            project_type="xianhua",
            theme="测试",
            config=CompleteOutlineGenerationConfig(mode=CompleteOutlineMode.IMPORT),
        )

        result = asyncio.run(self.engine.create_complete_outline(request))

        assert result.status == CompleteOutlineStatus.FAILED
        assert "required" in result.error_message.lower()

    def test_create_complete_outline_generate_mode_minimal(self):
        """Test generating outline in minimal mode without AI."""
        request = CompleteOutlineRequest(
            project_id="test_generate_minimal",
            project_title="生成测试",
            project_type="xianhua",
            theme="修仙",
            config=CompleteOutlineGenerationConfig(
                mode=CompleteOutlineMode.GENERATE,
                target_volumes=1,
                target_chapters=12,
                target_word_count=40000,
                include_subplots=False,
                include_foreshadowing=False,
                include_climax=False,
                include_ending=False,
            ),
        )

        result = asyncio.run(self.engine.create_complete_outline(request))

        assert result.status == CompleteOutlineStatus.COMPLETE
        assert len(result.components.volumes) >= 1
        assert len(result.components.chapters) == 12
        assert result.generation_stats["chapters_generated"] == 12

    def test_complete_outline_components_creation(self):
        """Test creating complete outline components."""
        components = CompleteOutlineComponents(
            volumes=[
                VolumeOutlinePlan(
                    volume_index=1,
                    volume_title="第一卷",
                    chapter_count=24,
                    chapter_start=1,
                    chapter_end=24,
                    volume_summary="测试卷",
                    status="generated",
                )
            ],
            chapters=[
                ChapterOutlinePlan(
                    chapter_number=i,
                    chapter_title=f"第{i}章",
                    volume_index=1,
                    synopsis=f"第{i}章测试概要",
                    word_count_target=3000,
                    status="generated",
                )
                for i in range(1, 25)
            ],
        )

        assert len(components.volumes) == 1
        assert len(components.chapters) == 24
        assert components.subplots == []
        assert components.foreshadowing == []
        assert components.climax == []
        assert components.ending is None

    def test_complete_outline_request_with_characters(self):
        """Test creating request with character data."""
        request = CompleteOutlineRequest(
            project_id="test_with_chars",
            project_title="角色小说",
            project_type="yanqing",
            theme="爱情",
            main_characters=[
                {"id": "char_1", "name": "主角A", "role": "protagonist"},
                {"id": "char_2", "name": "主角B", "role": "protagonist"},
            ],
            supporting_characters=[
                {"id": "char_3", "name": "朋友", "role": "supporting"},
            ],
            antagonists=[
                {"id": "char_4", "name": "反派", "role": "antagonist"},
            ],
        )

        assert len(request.main_characters) == 2
        assert len(request.supporting_characters) == 1
        assert len(request.antagonists) == 1

    def test_complete_outline_hybrid_mode(self):
        """Test hybrid outline creation mode."""
        import_content = '{"title": "混合小说", "chapters": [{"number": 1, "title": "第一章"}, {"number": 2, "title": "第二章"}]}'

        request = CompleteOutlineRequest(
            project_id="test_hybrid",
            project_title="混合模式",
            project_type="kehuan",
            theme="科幻",
            config=CompleteOutlineGenerationConfig(
                mode=CompleteOutlineMode.HYBRID,
                target_chapters=10,
                include_subplots=True,
                include_foreshadowing=True,
                include_climax=True,
                include_ending=True,
            ),
            import_content=import_content,
            import_format="json",
        )

        result = asyncio.run(self.engine.create_complete_outline(request))

        # Hybrid mode should import base then fill in missing parts
        assert result.status in [CompleteOutlineStatus.COMPLETE, CompleteOutlineStatus.IN_PROGRESS]
        assert len(result.components.chapters) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
