"""Volume split configuration models for multi-volume/book export."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class VolumeSplitStrategy(str, Enum):
    """Strategy for splitting volumes into separate books."""

    ONE_VOLUME_PER_BOOK = "one_volume_per_book"  # Each volume becomes a separate book
    MULTIPLE_VOLUMES_PER_BOOK = "multiple_volumes_per_book"  # Group volumes into books
    ALL_IN_ONE = "all_in_one"  # Keep all volumes in single book (no splitting)


class BookBinding(str, Enum):
    """Book binding style for export."""

    DIGITAL = "digital"  # Digital edition - optimized for screen reading
    PRINT = "print"  # Print edition - optimized for physical printing


class VolumeSplitConfig(BaseModel):
    """Configuration for volume split / multi-book export."""

    strategy: VolumeSplitStrategy = Field(
        default=VolumeSplitStrategy.ONE_VOLUME_PER_BOOK,
        description="How to split volumes into books"
    )
    volumes_per_book: int = Field(
        default=1,
        description="Number of volumes per book (for MULTIPLE_VOLUMES_PER_BOOK strategy)"
    )
    include_book_cover: bool = Field(
        default=True,
        description="Include cover page for each book"
    )
    include_book_toc: bool = Field(
        default=True,
        description="Include table of contents for each book"
    )
    include_series_toc: bool = Field(
        default=False,
        description="Include master table of contents showing all books"
    )
    book_naming_pattern: str = Field(
        default="{series_title} 第{book_number}册 {book_title}",
        description="Pattern for naming book files: {series_title}, {book_number}, {book_title}"
    )
    create_series_info: bool = Field(
        default=True,
        description="Create series information file"
    )
    binding: BookBinding = Field(
        default=BookBinding.DIGITAL,
        description="Binding style for the exported books"
    )


class VolumeBookInfo(BaseModel):
    """Information about a single book created from volume(s)."""

    book_number: int = Field(description="Book number in series (1-indexed)")
    book_title: str = Field(description="Title of this book")
    volume_ids: list[str] = Field(
        default_factory=list,
        description="Volume IDs included in this book"
    )
    chapter_count: int = Field(default=0, description="Number of chapters in this book")
    word_count: int = Field(default=0, description="Total word count")
    file_path: Optional[str] = Field(default=None, description="Path to exported file")


class VolumeSplitResult(BaseModel):
    """Result of volume split operation."""

    series_title: str = Field(description="Original series title")
    total_volumes: int = Field(description="Total number of volumes")
    total_books: int = Field(description="Total number of books created")
    books: list[VolumeBookInfo] = Field(
        default_factory=list,
        description="Information about each book created"
    )
    series_info_path: Optional[str] = Field(
        default=None,
        description="Path to series information file"
    )
    master_toc_path: Optional[str] = Field(
        default=None,
        description="Path to master table of contents"
    )
