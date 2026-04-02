"""Project initialization models for CHAI novel writing system."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Project type classification based on novel genre."""
    # Chinese web novel genres
    XIANHUA = "xianhua"           # 仙侠 - Fantasy/Xianxia
    YUANMAN = "yuanman"           # 玄幻 - Urban Fantasy/High Fantasy
    DUSHI = "dushi"               # 都市 - Urban Modern
    YANQING = "yanqing"           # 言情 - Romance
    XUANYI = "xuanyi"             # 悬疑 - Mystery/Thriller
    KEHAN = "kehuan"              # 科幻 - Science Fiction
    LISHI = "lishi"               # 历史 - Historical
    JUNSHI = "junshi"             # 军事 - Military
    YOUXI = "youxi"               # 游戏 - Game-related
    JINGJI = "jingji"             # 竞技 - Sports/Competition
    QINGXIAOSHUO = "qingxiaoshuo"  # 轻小说 - Light Novel
    TONGREN = "tongren"           # 同人 - Fan Fiction
    DANMEI = "danmei"             # 耽美 - Boys' Love
    BAIHE = "baihe"              # 百合 - Girls' Love
    NVZUN = "nvzun"               # 女尊 - Female Lead in Authority
    ZHICHANG = "zhichang"         # 职场 - Workplace

    # Western genres (aliases)
    FANTASY = "fantasy"            # Fantasy
    SCI_FI = "sci_fi"             # Science Fiction
    URBAN_FANTASY = "urban_fantasy" # Urban Fantasy
    ROMANCE = "romance"           # Romance
    MYSTERY = "mystery"           # Mystery
    THRILLER = "thriller"         # Thriller
    HORROR = "horror"             # Horror
    LITERARY = "literary"         # Literary Fiction
    ACTION = "action"             # Action/Adventure
    HISTORICAL_FICTION = "historical_fiction"  # Historical Fiction


class ProjectStatus(str, Enum):
    """Project initialization status."""
    INITIALIZED = "initialized"     # Project initialized, ready for outline
    OUTLINE_GENERATED = "outline_generated"  # Outline has been generated
    WRITING_IN_PROGRESS = "writing_in_progress"  # Writing in progress
    REVISION_IN_PROGRESS = "revision_in_progress"  # Revision in progress
    COMPLETED = "completed"        # Project completed
    PAUSED = "paused"             # Project paused
    ABANDONED = "abandoned"       # Project abandoned


class WritingMode(str, Enum):
    """Writing mode for the project."""
    AUTONOMOUS = "autonomous"      # Fully AI autonomous writing
    SEMI_AUTONOMOUS = "semi_autonomous"  # AI with human guidance
    COLLABORATIVE = "collaborative"  # Human-AI collaborative writing
    MANUAL = "manual"             # Manual writing with AI assistance only


class ProjectBasicInfo(BaseModel):
    """Basic project information."""
    title: str = Field(description="Novel title")
    author: str = Field(default="", description="Author name")
    description: str = Field(default="", description="Brief description of the novel")
    theme: str = Field(default="", description="Central theme or topic")
    target_audience: str = Field(
        default="new_adult",
        description="Target audience: young_adult, new_adult, adult, all_ages"
    )

    # Optional fields
    series_name: Optional[str] = Field(
        default=None,
        description="Series name if part of a series"
    )
    series_number: Optional[int] = Field(
        default=None,
        description="Book number in the series"
    )
    language: str = Field(
        default="zh-CN",
        description="Primary language of the novel"
    )

    # Project metadata
    created_from: str = Field(
        default="scratch",
        description="How the project was created: scratch, template, import"
    )
    template_id: Optional[str] = Field(
        default=None,
        description="Template ID if created from a template"
    )


class ProjectSettings(BaseModel):
    """Project writing settings."""
    # Word count targets
    target_word_count: int = Field(
        default=80000,
        ge=10000,
        le=5000000,
        description="Target total word count for entire novel"
    )
    min_chapter_word_count: int = Field(
        default=2000,
        ge=500,
        description="Minimum word count per chapter"
    )
    max_chapter_word_count: int = Field(
        default=4000,
        ge=1000,
        description="Maximum word count per chapter"
    )

    # Chapter structure
    estimated_total_chapters: int = Field(
        default=30,
        ge=1,
        description="Estimated total number of chapters"
    )
    has_prologue: bool = Field(
        default=True,
        description="Whether the novel has a prologue"
    )
    has_epilogue: bool = Field(
        default=True,
        description="Whether the novel has an epilogue"
    )
    prologue_word_count: int = Field(
        default=3000,
        ge=500,
        description="Target prologue word count"
    )
    epilogue_word_count: int = Field(
        default=3000,
        ge=500,
        description="Target epilogue word count"
    )

    # Volume structure
    volumes_planned: int = Field(
        default=1,
        ge=1,
        description="Number of volumes planned"
    )
    chapters_per_volume: int = Field(
        default=30,
        ge=1,
        description="Target chapters per volume"
    )

    # Writing mode
    writing_mode: WritingMode = Field(
        default=WritingMode.AUTONOMOUS,
        description="Writing mode for this project"
    )

    # Quality settings
    auto_proofread: bool = Field(
        default=True,
        description="Whether to auto-proofread each chapter"
    )
    auto_export: bool = Field(
        default=False,
        description="Whether to auto-export after completion"
    )

    # Checkpoint settings
    auto_checkpoint: bool = Field(
        default=True,
        description="Whether to create automatic checkpoints"
    )
    checkpoint_interval_minutes: int = Field(
        default=30,
        ge=5,
        description="Auto-checkpoint interval in minutes"
    )


class ProjectTypeConfig(BaseModel):
    """Project type/genre specific configuration."""
    project_type: ProjectType = Field(description="Project type")

    # Type-specific settings
    uses_magic_system: bool = Field(
        default=False,
        description="Whether the genre uses a magic/ability system"
    )
    uses_cultivation: bool = Field(
        default=False,
        description="Whether the genre uses cultivation/leveling system"
    )
    uses_game_mechanics: bool = Field(
        default=False,
        description="Whether the genre uses game mechanics"
    )
    is_modern_setting: bool = Field(
        default=False,
        description="Whether the setting is modern/realistic"
    )

    # Narrative style preferences
    typical_pacing: str = Field(
        default="moderate",
        description="Typical pacing: slow, moderate, fast"
    )
    typical_tone: str = Field(
        default="serious",
        description="Typical tone: light, moderate, serious"
    )
    allows_multiple_pov: bool = Field(
        default=False,
        description="Allow multiple POV characters"
    )

    # World building requirements
    requires_extended_world: bool = Field(
        default=True,
        description="Whether the genre requires extended world building"
    )
    requires_faction_system: bool = Field(
        default=False,
        description="Whether factions/powers are important"
    )


class ProjectProfile(BaseModel):
    """Complete project profile combining all project information."""
    # Basic info
    basic_info: ProjectBasicInfo = Field(
        description="Basic project information"
    )

    # Type configuration
    project_type: ProjectType = Field(
        description="Project type/genre"
    )
    type_config: ProjectTypeConfig = Field(
        description="Type-specific configuration"
    )

    # Settings
    settings: ProjectSettings = Field(
        description="Project writing settings"
    )

    # Status tracking
    status: ProjectStatus = Field(
        default=ProjectStatus.INITIALIZED,
        description="Current project status"
    )

    # Progress tracking
    outline_completed: bool = Field(
        default=False,
        description="Whether outline has been completed"
    )
    chapters_written: int = Field(
        default=0,
        description="Number of chapters written"
    )
    total_words_written: int = Field(
        default=0,
        description="Total words written"
    )

    # Metadata
    project_id: str = Field(
        description="Unique project identifier"
    )
    created_at: str = Field(
        description="Creation timestamp"
    )
    updated_at: str = Field(
        description="Last update timestamp"
    )


class ProjectInitializationRequest(BaseModel):
    """Request to initialize a new project."""
    title: str = Field(description="Novel title")
    author: str = Field(default="", description="Author name")
    project_type: ProjectType = Field(description="Project type/genre")
    theme: str = Field(default="", description="Central theme")
    description: str = Field(default="", description="Brief description")

    # Optional settings overrides
    target_word_count: Optional[int] = Field(
        default=None,
        description="Override default target word count"
    )
    writing_mode: Optional[WritingMode] = Field(
        default=None,
        description="Override default writing mode"
    )

    # Project creation options
    create_from_template: bool = Field(
        default=False,
        description="Whether to create from a template"
    )
    template_id: Optional[str] = Field(
        default=None,
        description="Template ID if creating from template"
    )
    import_existing_outline: bool = Field(
        default=False,
        description="Whether to import an existing outline"
    )


class ProjectInitializationResult(BaseModel):
    """Result of project initialization."""
    success: bool = Field(description="Whether initialization succeeded")
    project: Optional[ProjectProfile] = Field(
        default=None,
        description="Initialized project profile"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if initialization failed"
    )

    # Recommendations
    recommended_outline_approach: Optional[str] = Field(
        default=None,
        description="Recommended approach for creating outline"
    )
    estimated_completion_time_hours: Optional[float] = Field(
        default=None,
        description="Estimated hours to complete the project"
    )

    # Next steps
    next_steps: list[str] = Field(
        default_factory=list,
        description="Recommended next steps"
    )


class ProjectSummary(BaseModel):
    """Summary of a project for display purposes."""
    project_id: str = Field(description="Project ID")
    title: str = Field(description="Project title")
    project_type: ProjectType = Field(description="Project type")
    status: ProjectStatus = Field(description="Project status")

    # Progress
    progress_percent: float = Field(
        description="Overall progress percentage"
    )
    chapters_written: int = Field(
        description="Number of chapters written"
    )
    total_chapters: int = Field(
        description="Total chapters planned"
    )
    words_written: int = Field(
        description="Words written so far"
    )
    target_words: int = Field(
        description="Target word count"
    )

    # Time tracking
    created_at: str = Field(description="Creation date")
    last_updated: str = Field(description="Last update date")
