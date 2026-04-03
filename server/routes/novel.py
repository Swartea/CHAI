"""Novel management endpoints."""

import sys
import asyncio
import subprocess
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chai.services import AIService
from chai.engines import StoryPlanner, NovelEngine
from chai.models import Novel


router = APIRouter()


class CreateNovelRequest(BaseModel):
    genre: str = "玄幻"
    theme: str
    title: Optional[str] = None


class NovelResponse(BaseModel):
    id: str
    title: str
    genre: str
    theme: str
    status: str
    chapters_total: int
    chapters_written: int


@router.post("/create", response_model=NovelResponse)
async def create_novel(req: CreateNovelRequest):
    """Create a new novel project."""
    try:
        ai_service = AIService()
        planner = StoryPlanner(ai_service)

        # Generate world
        world = await planner.create_world(req.genre, req.theme)

        # Generate characters
        characters = await planner.create_characters(world, req.genre)

        # Generate plot
        plot = await planner.create_plot_outline(world, characters, req.genre, req.theme)

        # Create novel
        novel = Novel(
            id=f"novel_{world.name}",
            title=req.title or f"{req.theme}：{world.name}",
            genre=req.genre,
            theme=req.theme,
            world=world,
            characters=characters,
            plot_outline=plot,
        )

        # Save
        from chai.utils import save_novel
        save_novel(novel, f"novels/{novel.id}")

        return NovelResponse(
            id=novel.id,
            title=novel.title,
            genre=novel.genre,
            theme=novel.theme,
            status="created",
            chapters_total=len(plot.chapters) if plot.chapters else 0,
            chapters_written=0,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_novels():
    """List all novels."""
    novels_dir = Path(__file__).parent.parent.parent / "novels"
    novels = []

    if novels_dir.exists():
        for d in novels_dir.iterdir():
            if d.is_dir():
                novel_file = d / "novel.json"
                if novel_file.exists():
                    try:
                        data = json.loads(novel_file.read_text())
                        novels.append(data)
                    except:
                        pass

    return {"novels": novels}


@router.get("/{novel_id}")
async def get_novel(novel_id: str):
    """Get novel details."""
    novel_file = Path(__file__).parent.parent.parent / "novels" / novel_id / "novel.json"

    if not novel_file.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    return json.loads(novel_file.read_text())


@router.delete("/{novel_id}")
async def delete_novel(novel_id: str):
    """Delete a novel."""
    import shutil
    novel_dir = Path(__file__).parent.parent.parent / "novels" / novel_id

    if not novel_dir.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    shutil.rmtree(novel_dir)
    return {"status": "deleted", "id": novel_id}
