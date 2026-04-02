"""Project initialization engine for CHAI novel writing system."""

import uuid
from datetime import datetime
from typing import Optional

from chai.models.project_init import (
    ProjectType,
    ProjectStatus,
    WritingMode,
    ProjectBasicInfo,
    ProjectSettings,
    ProjectTypeConfig,
    ProjectProfile,
    ProjectInitializationRequest,
    ProjectInitializationResult,
    ProjectSummary,
)


class ProjectInitializationEngine:
    """Engine for initializing new novel projects.

    Handles the first step of the workflow: initializing project type
    and basic information. This creates a project profile that can be
    used for subsequent steps like outline generation.
    """

    # Default word count targets by project type
    DEFAULT_WORD_COUNTS = {
        ProjectType.XIANHUA: 80000,
        ProjectType.YUANMAN: 100000,
        ProjectType.DUSHI: 60000,
        ProjectType.YANQING: 50000,
        ProjectType.XUANYI: 70000,
        ProjectType.KEHAN: 80000,
        ProjectType.LISHI: 90000,
        ProjectType.JUNSHI: 100000,
        ProjectType.YOUXI: 80000,
        ProjectType.JINGJI: 70000,
        ProjectType.QINGXIAOSHUO: 40000,
        ProjectType.TONGREN: 50000,
        ProjectType.DANMEI: 50000,
        ProjectType.BAIHE: 50000,
        ProjectType.NVZUN: 60000,
        ProjectType.ZHICHANG: 60000,
        ProjectType.FANTASY: 90000,
        ProjectType.SCI_FI: 85000,
        ProjectType.URBAN_FANTASY: 70000,
        ProjectType.ROMANCE: 50000,
        ProjectType.MYSTERY: 65000,
        ProjectType.THRILLER: 70000,
        ProjectType.HORROR: 60000,
        ProjectType.LITERARY: 70000,
        ProjectType.ACTION: 75000,
        ProjectType.HISTORICAL_FICTION: 85000,
    }

    # Genres that use cultivation systems
    CULTIVATION_GENRES = {
        ProjectType.XIANHUA,
        ProjectType.YUANMAN,
    }

    # Genres that use game mechanics
    GAME_MECHANICS_GENRES = {
        ProjectType.YOUXI,
    }

    # Modern setting genres
    MODERN_SETTING_GENRES = {
        ProjectType.DUSHI,
        ProjectType.YANQING,
        ProjectType.JINGJI,
        ProjectType.ZHICHANG,
        ProjectType.URBAN_FANTASY,
    }

    def __init__(self):
        """Initialize the project initialization engine."""
        pass

    def initialize_project(
        self,
        request: ProjectInitializationRequest,
    ) -> ProjectInitializationResult:
        """Initialize a new project with basic information.

        Args:
            request: Project initialization request containing title,
                    project type, and other basic information.

        Returns:
            ProjectInitializationResult with the initialized project
            or error information.
        """
        try:
            # Validate request
            if not request.title or not request.title.strip():
                return ProjectInitializationResult(
                    success=False,
                    error_message="Project title is required",
                )

            # Generate project ID
            project_id = f"proj_{uuid.uuid4().hex[:12]}"

            # Get current timestamp
            now = datetime.now().isoformat()

            # Create basic info
            basic_info = ProjectBasicInfo(
                title=request.title.strip(),
                author=request.author.strip() if request.author else "",
                description=request.description.strip() if request.description else "",
                theme=request.theme.strip() if request.theme else "",
                created_from="template" if request.create_from_template else "scratch",
                template_id=request.template_id,
            )

            # Create type configuration
            type_config = self._create_type_config(request.project_type)

            # Calculate settings
            settings = self._create_settings(
                request.project_type,
                request.target_word_count,
                request.writing_mode,
            )

            # Create project profile
            project = ProjectProfile(
                basic_info=basic_info,
                project_type=request.project_type,
                type_config=type_config,
                settings=settings,
                status=ProjectStatus.INITIALIZED,
                project_id=project_id,
                created_at=now,
                updated_at=now,
            )

            # Generate next steps
            next_steps = self._generate_next_steps(
                request.project_type,
                request.create_from_template,
                request.import_existing_outline,
            )

            # Calculate estimated completion time
            estimated_time = self._estimate_completion_time(
                settings.target_word_count,
                settings.writing_mode,
            )

            return ProjectInitializationResult(
                success=True,
                project=project,
                recommended_outline_approach=self._get_recommended_outline_approach(
                    request.project_type
                ),
                estimated_completion_time_hours=estimated_time,
                next_steps=next_steps,
            )

        except Exception as e:
            return ProjectInitializationResult(
                success=False,
                error_message=f"Initialization failed: {str(e)}",
            )

    def _create_type_config(self, project_type: ProjectType) -> ProjectTypeConfig:
        """Create type-specific configuration based on project type.

        Args:
            project_type: The type/genre of the project.

        Returns:
            ProjectTypeConfig with appropriate settings for the type.
        """
        return ProjectTypeConfig(
            project_type=project_type,
            uses_magic_system=project_type in {
                ProjectType.XIANHUA,
                ProjectType.YUANMAN,
                ProjectType.FANTASY,
                ProjectType.URBAN_FANTASY,
            },
            uses_cultivation=project_type in self.CULTIVATION_GENRES,
            uses_game_mechanics=project_type in self.GAME_MECHANICS_GENRES,
            is_modern_setting=project_type in self.MODERN_SETTING_GENRES,
            typical_pacing=self._get_typical_pacing(project_type),
            typical_tone=self._get_typical_tone(project_type),
            allows_multiple_pov=project_type in {
                ProjectType.LITERARY,
                ProjectType.DUSHI,
                ProjectType.HISTORICAL_FICTION,
            },
            requires_extended_world=project_type not in self.MODERN_SETTING_GENRES,
            requires_faction_system=project_type in {
                ProjectType.XIANHUA,
                ProjectType.YUANMAN,
                ProjectType.JUNSHI,
            },
        )

    def _create_settings(
        self,
        project_type: ProjectType,
        override_word_count: Optional[int],
        override_writing_mode: Optional[WritingMode],
    ) -> ProjectSettings:
        """Create project settings with sensible defaults.

        Args:
            project_type: The type/genre of the project.
            override_word_count: Optional override for target word count.
            override_writing_mode: Optional override for writing mode.

        Returns:
            ProjectSettings with appropriate defaults.
        """
        target_word_count = (
            override_word_count
            if override_word_count
            else self.DEFAULT_WORD_COUNTS.get(project_type, 80000)
        )

        # Estimate chapters based on word count
        estimated_chapters = max(10, min(100, target_word_count // 3000))

        return ProjectSettings(
            target_word_count=target_word_count,
            writing_mode=override_writing_mode or WritingMode.AUTONOMOUS,
            estimated_total_chapters=estimated_chapters,
            chapters_per_volume=max(10, estimated_chapters // 3),
        )

    def _get_typical_pacing(self, project_type: ProjectType) -> str:
        """Get typical pacing for a project type."""
        slow_paced = {
            ProjectType.LISHI,
            ProjectType.LITERARY,
            ProjectType.HISTORICAL_FICTION,
        }
        fast_paced = {
            ProjectType.XUANYI,
            ProjectType.THRILLER,
            ProjectType.ACTION,
            ProjectType.YOUXI,
            ProjectType.JUNSHI,
        }

        if project_type in slow_paced:
            return "slow"
        elif project_type in fast_paced:
            return "fast"
        return "moderate"

    def _get_typical_tone(self, project_type: ProjectType) -> str:
        """Get typical tone for a project type."""
        light_tone = {
            ProjectType.YANQING,
            ProjectType.QINGXIAOSHUO,
            ProjectType.BAIHE,
            ProjectType.DANMEI,
        }
        serious_tone = {
            ProjectType.XIANHUA,
            ProjectType.YUANMAN,
            ProjectType.XUANYI,
            ProjectType.THRILLER,
            ProjectType.HORROR,
            ProjectType.JUNSHI,
        }

        if project_type in light_tone:
            return "light"
        elif project_type in serious_tone:
            return "serious"
        return "moderate"

    def _get_recommended_outline_approach(
        self, project_type: ProjectType
    ) -> str:
        """Get recommended outline approach for a project type."""
        if project_type in self.CULTIVATION_GENRES:
            return "gradual_revelation"
        elif project_type == ProjectType.XUANYI:
            return "mystery_structure"
        elif project_type == ProjectType.YANQING:
            return "relationship_arc"
        elif project_type == ProjectType.DUSHI:
            return "slice_of_life"
        return "three_act"

    def _generate_next_steps(
        self,
        project_type: ProjectType,
        create_from_template: bool,
        import_existing_outline: bool,
    ) -> list[str]:
        """Generate recommended next steps for the project."""
        steps = []

        if import_existing_outline:
            steps.append("导入已有大纲文件")
            steps.append("验证大纲完整性")
            steps.append("合并项目设置")
        elif create_from_template:
            steps.append("选择世界观模板")
            steps.append("应用模板设置")
            steps.append("生成详细大纲")
        else:
            steps.append("确定故事主题和核心冲突")
            steps.append("设计主要角色")
            steps.append("生成故事大纲")

        steps.append("规划章节结构")
        steps.append("开始第一章写作")

        return steps

    def _estimate_completion_time(
        self,
        target_word_count: int,
        writing_mode: WritingMode,
    ) -> float:
        """Estimate hours to complete the project.

        This is a rough estimate based on writing mode.

        Args:
            target_word_count: Target word count for the project.
            writing_mode: The writing mode being used.

        Returns:
            Estimated hours to completion.
        """
        # Base hours assuming autonomous writing at ~500 words/minute AI
        base_hours = target_word_count / 500 / 60  # Convert to hours

        # Adjust based on writing mode
        mode_multipliers = {
            WritingMode.AUTONOMOUS: 1.0,
            WritingMode.SEMI_AUTONOMOUS: 1.5,
            WritingMode.COLLABORATIVE: 2.5,
            WritingMode.MANUAL: 5.0,
        }

        multiplier = mode_multipliers.get(writing_mode, 1.0)

        # Add time for outlining, revision, etc.
        revision_factor = 1.3

        return base_hours * multiplier * revision_factor

    def get_project_summary(self, project: ProjectProfile) -> ProjectSummary:
        """Get a summary of a project for display.

        Args:
            project: The project profile to summarize.

        Returns:
            ProjectSummary with key information.
        """
        progress_percent = 0.0
        if project.settings.target_word_count > 0:
            progress_percent = (
                project.total_words_written
                / project.settings.target_word_count
                * 100
            )

        return ProjectSummary(
            project_id=project.project_id,
            title=project.basic_info.title,
            project_type=project.project_type,
            status=project.status,
            progress_percent=min(100.0, progress_percent),
            chapters_written=project.chapters_written,
            total_chapters=project.settings.estimated_total_chapters,
            words_written=project.total_words_written,
            target_words=project.settings.target_word_count,
            created_at=project.created_at,
            last_updated=project.updated_at,
        )

    def validate_project_info(
        self,
        title: str,
        project_type: ProjectType,
        target_word_count: Optional[int] = None,
    ) -> tuple[bool, Optional[str]]:
        """Validate project information.

        Args:
            title: The project title.
            project_type: The project type.
            target_word_count: Optional target word count.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not title or not title.strip():
            return False, "项目标题不能为空"

        if len(title.strip()) < 2:
            return False, "项目标题至少需要2个字符"

        if len(title.strip()) > 200:
            return False, "项目标题不能超过200个字符"

        if target_word_count is not None:
            if target_word_count < 10000:
                return False, "目标字数不能少于10000"
            if target_word_count > 5000000:
                return False, "目标字数不能超过500万"

        return True, None

    def get_available_project_types(self) -> list[tuple[ProjectType, str]]:
        """Get list of available project types with descriptions.

        Returns:
            List of (ProjectType, description) tuples.
        """
        return [
            (ProjectType.XIANHUA, "仙侠 - 修仙、剑法、宗门"),
            (ProjectType.YUANMAN, "玄幻 - 异世界、魔法、神话"),
            (ProjectType.DUSHI, "都市 - 现代都市、职场、生活"),
            (ProjectType.YANQING, "言情 - 爱情、浪漫、情感"),
            (ProjectType.XUANYI, "悬疑 - 推理、侦探、惊悚"),
            (ProjectType.KEHAN, "科幻 - 未来、科技、星际"),
            (ProjectType.LISHI, "历史 - 古代、历史传奇"),
            (ProjectType.JUNSHI, "军事 - 战争、军事策略"),
            (ProjectType.YOUXI, "游戏 - 游戏世界、虚拟现实"),
            (ProjectType.JINGJI, "竞技 - 体育、比赛、热血"),
            (ProjectType.QINGXIAOSHUO, "轻小说 - 轻松、幽默、二次元"),
            (ProjectType.TONGREN, "同人 - 已有作品的同人创作"),
            (ProjectType.DANMEI, "耽美 - BL、男男爱情"),
            (ProjectType.BAIHE, "百合 - GL、女女爱情"),
            (ProjectType.NVZUN, "女尊 - 女性主导的世界"),
            (ProjectType.ZHICHANG, "职场 - 职场奋斗、商业"),
        ]

    def estimate_chapter_count(
        self,
        target_word_count: int,
        min_words: int = 2000,
        max_words: int = 4000,
    ) -> tuple[int, int]:
        """Estimate chapter count range based on word count.

        Args:
            target_word_count: Total target word count.
            min_words: Minimum words per chapter.
            max_words: Maximum words per chapter.

        Returns:
            Tuple of (min_chapters, max_chapters).
        """
        min_chapters = max(1, target_word_count // max_words)
        max_chapters = max(1, target_word_count // min_words)
        return min_chapters, max_chapters
