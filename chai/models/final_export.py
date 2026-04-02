"""Final export models for exporting the completed novel manuscript.

This module provides models for orchestrating the final export process,
including validation, multi-format export, and output packaging.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""
    MARKDOWN = "markdown"
    EPUB = "epub"
    PDF = "pdf"
    ALL = "all"


class ExportStatus(str, Enum):
    """Export operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationStatus(str, Enum):
    """Manuscript validation status."""
    NOT_VALIDATED = "not_validated"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class ExportQuality(str, Enum):
    """Export quality level."""
    DRAFT = "draft"
    REVIEW = "review"
    FINAL = "final"
    PUBLICATION = "publication"


class ExportTemplate(str, Enum):
    """Pre-defined export templates."""
    SIMPLE = "simple"
    STANDARD = "standard"
    DETAILED = "detailed"
    PUBLICATION = "publication"


class ValidationIssue(BaseModel):
    """A validation issue found during export preparation."""
    issue_id: str
    severity: str = "warning"  # critical, major, minor, warning
    category: str  # content, structure, quality, metadata
    description: str
    location: Optional[str] = None  # chapter, volume, etc.
    suggestion: Optional[str] = None


class ManuscriptValidation(BaseModel):
    """Validation result for the manuscript before export."""
    status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    validated_at: Optional[str] = None
    total_issues: int = 0
    critical_issues: list[ValidationIssue] = []
    major_issues: list[ValidationIssue] = []
    minor_issues: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    word_count_check: bool = True
    chapter_completeness_check: bool = True
    structure_check: bool = True
    quality_score: float = 1.0


class ExportFormatConfig(BaseModel):
    """Configuration for a specific export format."""
    format: ExportFormat
    enabled: bool = True
    template: ExportTemplate = ExportTemplate.STANDARD
    output_filename: Optional[str] = None
    output_dir: Optional[str] = None


class ExportProgress(BaseModel):
    """Progress tracking for export operation."""
    stage: str = "initializing"
    current_step: int = 0
    total_steps: int = 0
    message: str = ""
    percent_complete: float = 0.0


class ExportMetadata(BaseModel):
    """Metadata for the exported manuscript."""
    title: str
    author: str = "CHAI"
    genre: str = ""
    total_words: int = 0
    total_chapters: int = 0
    total_volumes: int = 0
    export_date: str = ""
    export_version: str = "1.0"
    quality_level: ExportQuality = ExportQuality.FINAL
    validation_status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    polishing_applied: bool = False
    self_check_passed: bool = False


class ExportResult(BaseModel):
    """Result for a single format export."""
    format: ExportFormat
    status: ExportStatus
    output_path: Optional[str] = None
    file_size: Optional[int] = None  # bytes
    error_message: Optional[str] = None
    export_time: Optional[str] = None
    validation_issues: list[ValidationIssue] = []


class ExportPackage(BaseModel):
    """Complete export package containing all exported formats."""
    package_id: str
    title: str
    export_date: str = ""
    base_output_dir: str = ""

    markdown_export: Optional[ExportResult] = None
    epub_export: Optional[ExportResult] = None
    pdf_export: Optional[ExportResult] = None

    total_formats: int = 0
    successful_formats: int = 0
    failed_formats: int = 0

    metadata: Optional[ExportMetadata] = None
    validation: Optional[ManuscriptValidation] = None


class FinalExportConfig(BaseModel):
    """Configuration for final export operation."""
    # Export formats to generate
    formats: list[ExportFormat] = Field(default_factory=lambda: [ExportFormat.ALL])

    # Output settings
    output_dir: str = "./output"
    filename_pattern: str = "{title}_{format}_{date}"

    # Quality settings
    quality: ExportQuality = ExportQuality.FINAL
    template: ExportTemplate = ExportTemplate.STANDARD

    # Validation settings
    skip_validation: bool = False
    fail_on_critical: bool = True

    # Individual format settings
    markdown_template: ExportTemplate = ExportTemplate.STANDARD
    epub_template: ExportTemplate = ExportTemplate.STANDARD
    pdf_template: ExportTemplate = ExportTemplate.STANDARD

    # Include options
    include_validation_report: bool = True
    include_polishing_report: bool = False
    include_summary: bool = True

    # Split options
    split_volumes: bool = False
    split_chapters: bool = False


class FinalExportRequest(BaseModel):
    """Request for final export operation."""
    book_id: str
    title: str
    author: str = "CHAI"
    genre: str = ""

    # Volume and chapter data
    volumes: list[dict] = Field(default_factory=list)
    characters: list[dict] = Field(default_factory=list)
    world_setting: Optional[dict] = None

    # Optional reports from previous steps
    polishing_report: Optional[dict] = None
    self_check_report: Optional[dict] = None

    # Configuration
    config: FinalExportConfig = Field(default_factory=FinalExportConfig)


class FinalExportResult(BaseModel):
    """Result of the final export operation."""
    success: bool = False
    export_id: str = ""
    title: str = ""

    status: ExportStatus = ExportStatus.PENDING
    package: Optional[ExportPackage] = None

    validation: Optional[ManuscriptValidation] = None
    export_results: list[ExportResult] = []

    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    elapsed_time: float = 0.0

    error_message: Optional[str] = None

    # Summary statistics
    total_formats: int = 0
    successful_formats: int = 0
    failed_formats: int = 0
    total_file_size: int = 0


class FinalExportSummary(BaseModel):
    """Summary of the final export for display."""
    title: str
    total_words: int
    total_chapters: int
    total_volumes: int

    formats_exported: list[str]
    total_file_size: str  # Human readable

    export_paths: dict[str, str]  # format -> path

    quality_score: float
    validation_passed: bool
    issues_found: int

    recommendation: str
    next_steps: list[str]


class ExportChecklist(BaseModel):
    """Checklist for export readiness."""
    manuscript_complete: bool = False
    all_chapters_written: bool = False
    self_check_passed: bool = False
    polishing_complete: bool = False
    validation_passed: bool = False
    metadata_complete: bool = False

    missing_items: list[str] = []
    warnings: list[str] = []
    ready_for_export: bool = False
