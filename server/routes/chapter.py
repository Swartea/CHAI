"""Chapter writing endpoints."""

import sys
import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chai.services import AIService
from chai.engines import ChapterWriter
from chai.utils import load_novel, save_novel


router = APIRouter()


class WriteChapterRequest(BaseModel):
    novel_id: str
    chapter_index: int


@router.post("/write")
async def write_chapter(req: WriteChapterRequest):
    """Write a chapter."""
    try:
        novel_dir = Path(__file__).parent.parent.parent / "novels" / req.novel_id
        novel_file = novel_dir / "novel.json"

        if not novel_file.exists():
            raise HTTPException(status_code=404, detail="Novel not found")

        novel = load_novel(str(novel_dir))

        ai_service = AIService()
        writer = ChapterWriter(ai_service)

        # Get chapter outline
        chapters = novel.plot_outline.chapters if novel.plot_outline else []
        if req.chapter_index >= len(chapters):
            raise HTTPException(status_code=400, detail="Chapter index out of range")

        chapter_outline = chapters[req.chapter_index]

        # Write chapter
        chapter_content = await writer.write_chapter(
            novel=novel,
            chapter_outline=chapter_outline,
            previous_chapter=None,
        )

        # Update novel
        if not novel.chapters:
            novel.chapters = []

        while len(novel.chapters) <= req.chapter_index:
            novel.chapters.append(None)

        novel.chapters[req.chapter_index] = chapter_content
        save_novel(novel, str(novel_dir))

        return {
            "chapter_index": req.chapter_index,
            "title": chapter_content.title if chapter_content else f"Chapter {req.chapter_index + 1}",
            "word_count": chapter_content.word_count if chapter_content else 0,
            "status": "written",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{novel_id}")
async def list_chapters(novel_id: str):
    """List all chapters for a novel."""
    novel_dir = Path(__file__).parent.parent.parent / "novels" / novel_id
    novel_file = novel_dir / "novel.json"

    if not novel_file.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    novel = load_novel(str(novel_dir))
    chapters = novel.plot_outline.chapters if novel.plot_outline else []

    result = []
    for i, outline in enumerate(chapters):
        content = novel.chapters[i] if i < len(novel.chapters) and novel.chapters[i] else None
        result.append({
            "index": i,
            "title": outline.title if outline else f"Chapter {i + 1}",
            "outline": outline.model_dump() if outline else {},
            "content": content.model_dump() if content else None,
            "word_count": content.word_count if content else 0,
            "status": "written" if content else "pending",
        })

    return {"chapters": result}


@router.get("/{novel_id}/{chapter_index}")
async def get_chapter(novel_id: str, chapter_index: int):
    """Get a specific chapter."""
    novel_dir = Path(__file__).parent.parent.parent / "novels" / novel_id
    novel_file = novel_dir / "novel.json"

    if not novel_file.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    novel = load_novel(str(novel_dir))

    if chapter_index >= len(novel.chapters) or not novel.chapters[chapter_index]:
        raise HTTPException(status_code=404, detail="Chapter not written yet")

    return novel.chapters[chapter_index].model_dump()
