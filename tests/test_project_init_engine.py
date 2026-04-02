"""Tests for project initialization engine."""

import pytest

from chai.engines.project_init_engine import ProjectInitializationEngine
from chai.models.project_init import (
    ProjectType,
    ProjectStatus,
    WritingMode,
    ProjectInitializationRequest,
)


class TestProjectInitializationEngine:
    """Test cases for ProjectInitializationEngine."""

    @pytest.fixture
    def engine(self):
        """Create a ProjectInitializationEngine instance."""
        return ProjectInitializationEngine()

    def test_initialize_project_basic(self, engine):
        """Test basic project initialization."""
        request = ProjectInitializationRequest(
            title="测试小说",
            author="测试作者",
            project_type=ProjectType.XIANHUA,
            theme="修仙成神",
            description="一个关于修仙者成长的小说",
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project is not None
        assert result.project.basic_info.title == "测试小说"
        assert result.project.basic_info.author == "测试作者"
        assert result.project.project_type == ProjectType.XIANHUA
        assert result.project.basic_info.theme == "修仙成神"
        assert result.project.status == ProjectStatus.INITIALIZED
        assert result.next_steps is not None
        assert len(result.next_steps) > 0

    def test_initialize_project_xianhua_type_config(self, engine):
        """Test that xianhua project type gets correct config."""
        request = ProjectInitializationRequest(
            title="仙侠小说",
            project_type=ProjectType.XIANHUA,
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project.type_config.uses_cultivation is True
        assert result.project.type_config.uses_magic_system is True
        assert result.project.type_config.requires_faction_system is True

    def test_initialize_project_dushi_type_config(self, engine):
        """Test that dushi project type gets correct config."""
        request = ProjectInitializationRequest(
            title="都市小说",
            project_type=ProjectType.DUSHI,
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project.type_config.is_modern_setting is True
        assert result.project.type_config.uses_cultivation is False
        assert result.project.type_config.uses_magic_system is False

    def test_initialize_project_with_word_count_override(self, engine):
        """Test project initialization with word count override."""
        request = ProjectInitializationRequest(
            title="自定义字数小说",
            project_type=ProjectType.XUANYI,
            target_word_count=150000,
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project.settings.target_word_count == 150000

    def test_initialize_project_with_writing_mode_override(self, engine):
        """Test project initialization with writing mode override."""
        request = ProjectInitializationRequest(
            title="协作写作小说",
            project_type=ProjectType.YANQING,
            writing_mode=WritingMode.COLLABORATIVE,
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project.settings.writing_mode == WritingMode.COLLABORATIVE

    def test_initialize_project_empty_title_fails(self, engine):
        """Test that empty title fails validation."""
        request = ProjectInitializationRequest(
            title="",
            project_type=ProjectType.XIANHUA,
        )

        result = engine.initialize_project(request)

        assert result.success is False
        assert "title" in result.error_message.lower() or "required" in result.error_message.lower()

    def test_initialize_project_whitespace_title_fails(self, engine):
        """Test that whitespace-only title fails validation."""
        request = ProjectInitializationRequest(
            title="   ",
            project_type=ProjectType.XIANHUA,
        )

        result = engine.initialize_project(request)

        assert result.success is False

    def test_initialize_project_generates_unique_id(self, engine):
        """Test that each project gets a unique ID."""
        request = ProjectInitializationRequest(
            title="测试小说",
            project_type=ProjectType.XIANHUA,
        )

        result1 = engine.initialize_project(request)
        result2 = engine.initialize_project(request)

        assert result1.success is True
        assert result2.success is True
        assert result1.project.project_id != result2.project.project_id

    def test_initialize_project_sets_timestamps(self, engine):
        """Test that initialization sets creation timestamp."""
        request = ProjectInitializationRequest(
            title="测试小说",
            project_type=ProjectType.YUANMAN,
        )

        result = engine.initialize_project(request)

        assert result.success is True
        assert result.project.created_at is not None
        assert result.project.updated_at is not None
        assert result.project.created_at == result.project.updated_at

    def test_get_available_project_types(self, engine):
        """Test getting list of available project types."""
        types = engine.get_available_project_types()

        assert len(types) > 0
        assert all(isinstance(t[0], ProjectType) for t in types)
        assert all(isinstance(t[1], str) for t in types)

    def test_estimate_chapter_count(self, engine):
        """Test chapter count estimation."""
        min_ch, max_ch = engine.estimate_chapter_count(80000)

        assert min_ch >= 1
        assert max_ch >= min_ch
        assert max_ch <= 80  # 80000 / 1000 = 80

    def test_validate_project_info_valid(self, engine):
        """Test validation of valid project info."""
        is_valid, error = engine.validate_project_info(
            title="测试小说",
            project_type=ProjectType.XIANHUA,
            target_word_count=80000,
        )

        assert is_valid is True
        assert error is None

    def test_validate_project_info_empty_title(self, engine):
        """Test validation fails for empty title."""
        is_valid, error = engine.validate_project_info(
            title="",
            project_type=ProjectType.XIANHUA,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_project_info_short_title(self, engine):
        """Test validation fails for too short title."""
        is_valid, error = engine.validate_project_info(
            title="A",
            project_type=ProjectType.XIANHUA,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_project_info_long_title(self, engine):
        """Test validation fails for too long title."""
        is_valid, error = engine.validate_project_info(
            title="A" * 201,
            project_type=ProjectType.XIANHUA,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_project_info_low_word_count(self, engine):
        """Test validation fails for low word count."""
        is_valid, error = engine.validate_project_info(
            title="测试小说",
            project_type=ProjectType.XIANHUA,
            target_word_count=5000,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_project_info_high_word_count(self, engine):
        """Test validation fails for high word count."""
        is_valid, error = engine.validate_project_info(
            title="测试小说",
            project_type=ProjectType.XIANHUA,
            target_word_count=10000000,
        )

        assert is_valid is False
        assert error is not None

    def test_get_project_summary(self, engine):
        """Test getting project summary."""
        request = ProjectInitializationRequest(
            title="测试小说",
            project_type=ProjectType.XUANYI,
            theme="探案",
        )

        result = engine.initialize_project(request)
        summary = engine.get_project_summary(result.project)

        assert summary.project_id == result.project.project_id
        assert summary.title == "测试小说"
        assert summary.project_type == ProjectType.XUANYI
        assert summary.status == ProjectStatus.INITIALIZED
        assert summary.progress_percent == 0.0
        assert summary.chapters_written == 0

    def test_type_config_pacing_xianxia(self, engine):
        """Test pacing is set correctly for xianxia."""
        request = ProjectInitializationRequest(
            title="仙侠小说",
            project_type=ProjectType.XIANHUA,
        )
        result = engine.initialize_project(request)

        # Xianxia should have moderate pacing
        assert result.project.type_config.typical_pacing in ["slow", "moderate", "fast"]

    def test_type_config_pacing_thriller(self, engine):
        """Test pacing is set correctly for thriller."""
        request = ProjectInitializationRequest(
            title="悬疑小说",
            project_type=ProjectType.XUANYI,
        )
        result = engine.initialize_project(request)

        # Xuanyi/thriller should have fast pacing
        assert result.project.type_config.typical_pacing == "fast"

    def test_recommended_outline_approach_xianxia(self, engine):
        """Test recommended outline approach for xianxia."""
        request = ProjectInitializationRequest(
            title="仙侠小说",
            project_type=ProjectType.XIANHUA,
        )
        result = engine.initialize_project(request)

        assert result.recommended_outline_approach == "gradual_revelation"

    def test_recommended_outline_approach_mystery(self, engine):
        """Test recommended outline approach for mystery."""
        request = ProjectInitializationRequest(
            title="悬疑小说",
            project_type=ProjectType.XUANYI,
        )
        result = engine.initialize_project(request)

        assert result.recommended_outline_approach == "mystery_structure"

    def test_next_steps_from_scratch(self, engine):
        """Test next steps for project created from scratch."""
        request = ProjectInitializationRequest(
            title="新小说",
            project_type=ProjectType.XIANHUA,
            create_from_template=False,
            import_existing_outline=False,
        )
        result = engine.initialize_project(request)

        assert "确定故事主题" in result.next_steps[0]
        assert "开始第一章写作" in result.next_steps[-1]

    def test_next_steps_from_template(self, engine):
        """Test next steps for project created from template."""
        request = ProjectInitializationRequest(
            title="模板小说",
            project_type=ProjectType.XIANHUA,
            create_from_template=True,
            template_id="template_001",
        )
        result = engine.initialize_project(request)

        assert "选择世界观模板" in result.next_steps[0]

    def test_next_steps_with_import(self, engine):
        """Test next steps for project with existing outline import."""
        request = ProjectInitializationRequest(
            title="导入小说",
            project_type=ProjectType.XIANHUA,
            create_from_template=False,
            import_existing_outline=True,
        )
        result = engine.initialize_project(request)

        assert "导入已有大纲" in result.next_steps[0]

    def test_estimated_completion_time_autonomous(self, engine):
        """Test estimated completion time for autonomous mode."""
        request = ProjectInitializationRequest(
            title="自动写作小说",
            project_type=ProjectType.XIANHUA,
            writing_mode=WritingMode.AUTONOMOUS,
            target_word_count=80000,
        )
        result = engine.initialize_project(request)

        assert result.estimated_completion_time_hours is not None
        assert result.estimated_completion_time_hours > 0

    def test_estimated_completion_time_collaborative(self, engine):
        """Test estimated completion time is longer for collaborative mode."""
        request_autonomous = ProjectInitializationRequest(
            title="自动写作小说",
            project_type=ProjectType.XIANHUA,
            writing_mode=WritingMode.AUTONOMOUS,
            target_word_count=80000,
        )
        request_collab = ProjectInitializationRequest(
            title="协作写作小说",
            project_type=ProjectType.XIANHUA,
            writing_mode=WritingMode.COLLABORATIVE,
            target_word_count=80000,
        )

        result_autonomous = engine.initialize_project(request_autonomous)
        result_collab = engine.initialize_project(request_collab)

        assert (result_collab.estimated_completion_time_hours >
                result_autonomous.estimated_completion_time_hours)

    def test_project_has_default_settings(self, engine):
        """Test that project has sensible default settings."""
        request = ProjectInitializationRequest(
            title="测试小说",
            project_type=ProjectType.XIANHUA,
        )
        result = engine.initialize_project(request)

        assert result.project.settings.target_word_count > 0
        assert result.project.settings.min_chapter_word_count >= 500
        assert result.project.settings.max_chapter_word_count >= 1000
        assert result.project.settings.estimated_total_chapters >= 1
        assert result.project.settings.has_prologue is True
        assert result.project.settings.has_epilogue is True

    def test_all_genre_types_initializable(self, engine):
        """Test that all project types can be initialized."""
        for project_type in ProjectType:
            request = ProjectInitializationRequest(
                title=f"{project_type.value}类型小说",
                project_type=project_type,
            )
            result = engine.initialize_project(request)

            assert result.success is True, f"Failed for {project_type}"
            assert result.project.project_type == project_type
