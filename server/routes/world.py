"""World building endpoints."""

import sys
import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chai.services import AIService
from chai.engines import WorldBuilder


router = APIRouter()


class BuildWorldRequest(BaseModel):
    genre: str = "玄幻"
    theme: str


@router.post("/build")
async def build_world(req: BuildWorldRequest):
    """Build a world setting."""
    try:
        ai_service = AIService()
        builder = WorldBuilder(ai_service)

        world = await builder.build_world(req.genre, req.theme)

        return {
            "name": world.name,
            "genre": world.genre,
            "summary": world.model_dump(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{novel_id}")
async def get_world(novel_id: str):
    """Get world setting for a novel."""
    novel_file = Path(__file__).parent.parent.parent / "novels" / novel_id / "novel.json"

    if not novel_file.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    import json
    data = json.loads(novel_file.read_text())

    return data.get("world", {})


@router.put("/{novel_id}")
async def update_world(novel_id: str, world_data: dict):
    """Update world setting."""
    novel_dir = Path(__file__).parent.parent.parent / "novels" / novel_id
    novel_file = novel_dir / "novel.json"

    if not novel_file.exists():
        raise HTTPException(status_code=404, detail="Novel not found")

    import json
    data = json.loads(novel_file.read_text())
    data["world"] = world_data
    novel_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    return {"status": "updated"}
