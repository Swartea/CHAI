"""Pydantic models for CHAI API."""

from pydantic import BaseModel
from typing import Optional


class NovelCreateRequest(BaseModel):
    genre: str = "玄幻"
    theme: str


class WorldBuildRequest(BaseModel):
    genre: str = "玄幻"
    theme: str


class ChapterWriteRequest(BaseModel):
    novel_id: str
    chapter_index: int


class DeconstructRequest(BaseModel):
    entry_id: Optional[str] = None
    entry_name: Optional[str] = None
    genre: Optional[str] = None
    max_books: int = 5


class NovelResponse(BaseModel):
    id: str
    title: str
    genre: str
    status: str


class WorldResponse(BaseModel):
    name: str
    genre: str
    summary: dict


class ChapterResponse(BaseModel):
    index: int
    title: str
    word_count: int
    status: str


class DeconstructResponse(BaseModel):
    books_analyzed: int
    templates: dict
