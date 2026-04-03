"""Book deconstruction endpoints."""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chai.crawler import FanqieCrawler
from chai.engines import BookDeconstructor
from chai.db import DeconstructDB


router = APIRouter()


class DeconstructRequest(BaseModel):
    entry_id: str = None
    entry_name: str = None
    genre: str = None
    max_books: int = 5


@router.post("/run")
async def run_deconstruct(req: DeconstructRequest):
    """Deconstruct books from Fanqie hot list."""
    try:
        crawler = FanqieCrawler()
        deconstructor = BookDeconstructor()
        db = DeconstructDB()

        # Get book list from Fanqie
        if req.entry_id:
            books = await crawler.get_books_by_entry(req.entry_id, req.max_books)
        elif req.entry_name:
            entry = await crawler.search_entry(req.entry_name)
            if entry:
                books = await crawler.get_books_by_entry(entry["id"], req.max_books)
            else:
                raise HTTPException(status_code=404, detail="Entry not found")
        else:
            books = await crawler.get_popular_books(req.genre, req.max_books)

        # Deconstruct each book
        results = []
        for book in books:
            decon_result = await deconstructor.deconstruct_book(book)
            db.save_deconstruction(decon_result)
            results.append(decon_result)

        return {
            "books_analyzed": len(results),
            "results": [r.model_dump() for r in results],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(genre: str = None):
    """List stored templates."""
    db = DeconstructDB()
    templates = db.get_all_templates()

    if genre:
        templates = [t for t in templates if t.get("genre") == genre]

    return {"templates": templates}


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template."""
    db = DeconstructDB()
    template = db.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template
