"""Complete outline models for generating or importing full novel outlines.

This module provides models for the complete outline workflow - the second step
in the CHAI novel writing workflow after project initialization.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CompleteOutlineMode(str, Enum):
    """Mode for creating complete outline."""
    GENERATE = "generate"  # Generate new outline from project info
    IMPORT = "import"  # Import existing outline
    HYBRID = "hybrid"  # Import base and generate missing parts


class CompleteOutlineStatus(str, Enum):
    """Status of complete outline creation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    GENERATING_COMPONENTS = "generating_components"
    VALIDATING = "validating"
    COMPLETE = "complete"
    FAILED = "failed"


class OutlineComponentStatus(str, Enum):
    """Status of individual outline components."""
    PENDING = "pending"
    GENERATED = "generated"
    IMPORTED = "imported"
    MERGED = "merged"
    VALIDATED = "validated"
    FAILED = "failed"


class VolumeOutlinePlan(BaseModel):
    """Plan for a single volume in the complete outline."""
    volume_index: int = Field(description="Volume index (1-based)")
    volume_title: str = Field(description="Title of the volume")
    chapter_count: int = Field(description="Number of chapters in this volume")
    chapter_start: int = Field(description="Starting chapter number")
    chapter_end: int = Field(description="Ending chapter number")
    volume_summary: str = Field(default="", description="Summary of volume arc")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class ChapterOutlinePlan(BaseModel):
    """Plan for a single chapter in the complete outline."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(description="Title of the chapter")
    volume_index: int = Field(description="Volume this chapter belongs to")
    synopsis: str = Field(default="", description="Chapter synopsis")
    word_count_target: int = Field(default=3000, description="Target word count")
    scenes: list[str] = Field(default_factory=list, description="Scene descriptions")
    plot_threads: list[str] = Field(default_factory=list, description="Plot threads in this chapter")
    foreshadowing: list[str] = Field(default_factory=list, description="Foreshadowing elements")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class SubplotOutlinePlan(BaseModel):
    """Plan for subplot outline."""
    subplot_id: str = Field(description="Unique subplot ID")
    subplot_type: str = Field(description="Type of subplot")
    description: str = Field(description="Subplot description")
    chapters_involved: list[int] = Field(description="Chapter numbers involved")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class ForeshadowingOutlinePlan(BaseModel):
    """Plan for foreshadowing outline."""
    foreshadowing_id: str = Field(description="Unique foreshadowing ID")
    element: str = Field(description="Foreshadowing element description")
    chapter_planted: int = Field(description="Chapter where planted")
    chapter_payoff: Optional[int] = Field(description="Chapter where payoff occurs")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class ClimaxOutlinePlan(BaseModel):
    """Plan for climax outline."""
    climax_id: str = Field(description="Unique climax ID")
    climax_type: str = Field(description="Type of climax")
    chapter_location: int = Field(description="Chapter where climax occurs")
    description: str = Field(description="Climax description")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class EndingOutlinePlan(BaseModel):
    """Plan for ending outline."""
    ending_id: str = Field(description="Unique ending ID")
    ending_type: str = Field(description="Type of ending")
    chapter_location: int = Field(description="Chapter where ending occurs")
    description: str = Field(description="Ending description")
    status: OutlineComponentStatus = Field(default=OutlineComponentStatus.PENDING)


class CompleteOutlineComponents(BaseModel):
    """All components of a complete outline."""
    volumes: list[VolumeOutlinePlan] = Field(default_factory=list, description="Volume plans")
    chapters: list[ChapterOutlinePlan] = Field(default_factory=list, description="Chapter plans")
    subplots: list[SubplotOutlinePlan] = Field(default_factory=list, description="Subplot plans")
    foreshadowing: list[ForeshadowingOutlinePlan] = Field(default_factory=list, description="Foreshadowing plans")
    climax: list[ClimaxOutlinePlan] = Field(default_factory=list, description="Climax plans")
    ending: Optional[EndingOutlinePlan] = Field(default=None, description="Ending plan")


class CompleteOutlineGenerationConfig(BaseModel):
    """Configuration for complete outline generation."""
    mode: CompleteOutlineMode = Field(default=CompleteOutlineMode.GENERATE, description="Generation mode")
    target_volumes: int = Field(default=1, description="Target number of volumes")
    target_chapters: int = Field(default=24, description="Target number of chapters")
    target_word_count: int = Field(default=80000, description="Target total word count")
    include_subplots: bool = Field(default=True, description="Include subplot planning")
    include_foreshadowing: bool = Field(default=True, description="Include foreshadowing planning")
    include_climax: bool = Field(default=True, description="Include climax planning")
    include_ending: bool = Field(default=True, description="Include ending planning")
    outline_structure: str = Field(default="three_act", description="Outline structure type")
    import_format: Optional[str] = Field(default=None, description="Import format if mode is IMPORT")


class CompleteOutlineRequest(BaseModel):
    """Request for creating a complete outline."""
    project_id: str = Field(description="Project ID from initialization")
    project_title: str = Field(description="Title of the novel")
    project_type: str = Field(description="Type/genre of the novel")
    theme: str = Field(description="Central theme of the novel")
    main_characters: list[dict] = Field(default_factory=list, description="Main character dicts")
    supporting_characters: list[dict] = Field(default_factory=list, description="Supporting character dicts")
    antagonists: list[dict] = Field(default_factory=list, description="Antagonist dicts")
    world_setting: Optional[dict] = Field(default=None, description="World setting dict")
    config: CompleteOutlineGenerationConfig = Field(default_factory=CompleteOutlineGenerationConfig)
    import_content: Optional[str] = Field(default=None, description="Content to import if mode is IMPORT")
    import_format: Optional[str] = Field(default=None, description="Format of import content")


class CompleteOutlineResult(BaseModel):
    """Result of complete outline creation."""
    outline_id: str = Field(description="Unique outline ID")
    project_id: str = Field(description="Associated project ID")
    status: CompleteOutlineStatus = Field(description="Overall status")
    components: CompleteOutlineComponents = Field(description="Generated outline components")
    story_outline_id: Optional[str] = Field(default=None, description="ID of generated story outline")
    main_structure_id: Optional[str] = Field(default=None, description="ID of main structure")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    generation_stats: dict = Field(default_factory=dict, description="Generation statistics")


class CompleteOutlineSummary(BaseModel):
    """Summary of a complete outline for display."""
    outline_id: str = Field(description="Outline ID")
    project_title: str = Field(description="Project title")
    status: CompleteOutlineStatus = Field(description="Status")
    volume_count: int = Field(description="Number of volumes")
    chapter_count: int = Field(description="Number of chapters")
    subplot_count: int = Field(description="Number of subplots")
    foreshadowing_count: int = Field(description="Number of foreshadowing elements")
    climax_count: int = Field(description="Number of climax points")
    has_ending: bool = Field(description="Whether ending is planned")
    word_count_target: int = Field(description="Target word count")
    created_at: str = Field(description="Creation timestamp")


class OutlineValidationIssue(BaseModel):
    """Issue found during outline validation."""
    issue_type: str = Field(description="Type of issue")
    severity: str = Field(description="Severity: warning, error")
    location: str = Field(description="Where the issue is located")
    description: str = Field(description="Description of the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class OutlineValidationResult(BaseModel):
    """Result of outline validation."""
    is_valid: bool = Field(description="Whether outline is valid")
    issues: list[OutlineValidationIssue] = Field(default_factory=list, description="Issues found")
    warnings: int = Field(default=0, description="Number of warnings")
    errors: int = Field(default=0, description="Number of errors")


class NextChapterToWrite(BaseModel):
    """Information about the next chapter to write."""
    chapter_number: int = Field(description="Chapter number")
    chapter_title: str = Field(description="Chapter title")
    synopsis: str = Field(default="", description="Chapter synopsis")
    word_count_target: int = Field(description="Target word count")
    previous_chapter_summary: str = Field(default="", description="Summary of previous chapter")
    plot_continuity: list[str] = Field(default_factory=list, description="Plot points to continue")
    foreshadowing_active: list[str] = Field(default_factory=list, description="Foreshadowing to pay attention to")