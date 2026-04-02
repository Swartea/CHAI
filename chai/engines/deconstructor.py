"""Book deconstruction engine.

Deconstructs popular books from Fanqie hot list to extract reusable
character templates, plot patterns, and world setting templates.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from chai.crawler import FanqieCrawler, FanqieHotEntry, FanqieBook
from chai.db import DeconstructDB
from chai.models.deconstruct import (
    CharacterTemplate,
    CharacterTemplateType,
    DeconstructSource,
    DeconstructionResult,
    PlotPattern,
    PlotPatternType,
    WorldTemplate,
    WorldTemplateType,
)
from chai.services import AIService


class BookDeconstructor:
    """Engine for deconstructing popular books and extracting reusable templates."""

    def __init__(
        self,
        ai_service: AIService,
        db: Optional[DeconstructDB] = None,
        crawler: Optional[FanqieCrawler] = None,
    ):
        """Initialize the deconstructor.

        Args:
            ai_service: AI service for deconstruction analysis
            db: Database for storing templates (default: global db)
            crawler: Fanqie crawler for fetching book data
        """
        self.ai_service = ai_service
        self.db = db or DeconstructDB()
        self.crawler = crawler or FanqieCrawler()

    async def close(self) -> None:
        """Close resources."""
        await self.crawler.close()

    async def __aenter__(self) -> "BookDeconstructor":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    def _make_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def _str_to_enum(self, value: str, enum_class, default):
        """Convert string to enum, with fallback to default."""
        try:
            return enum_class(value.lower())
        except ValueError:
            return default

    async def deconstruct_book(
        self,
        book: FanqieBook,
        chapter_samples: Optional[list[str]] = None,
    ) -> DeconstructionResult:
        """Deconstruct a single book and extract templates.

        Args:
            book: Book to deconstruct
            chapter_samples: Optional chapter content samples for analysis

        Returns:
            Deconstruction result with extracted templates
        """
        result_id = self._make_id("decon")
        source = DeconstructSource(
            book_id=book.id,
            book_title=book.title,
            author=book.author,
            platform="fanqie",
            url=f"https://fanqienovel.com/book/{book.id}",
        )

        result = DeconstructionResult(
            id=result_id,
            source=source,
            status="processing",
        )

        try:
            # Call AI to deconstruct the book
            decon_data = await self.ai_service.deconstruct_book(
                book_title=book.title,
                book_synopsis=book.synopsis,
                genre=book.genre,
                chapter_samples=chapter_samples,
            )

            # Parse character templates
            for char_data in decon_data.get("character_templates", []):
                char_type = self._str_to_enum(
                    char_data.get("template_type", "supporting"),
                    CharacterTemplateType,
                    CharacterTemplateType.SUPPORTING,
                )
                template = CharacterTemplate(
                    id=self._make_id("char"),
                    name=char_data.get("name", "未命名模板"),
                    template_type=char_type,
                    genre=book.genre,
                    source=source,
                    age_range=char_data.get("age_range", ""),
                    background_template=char_data.get("background_template", ""),
                    personality_traits=char_data.get("personality_traits", []),
                    strengths=char_data.get("strengths", []),
                    weaknesses=char_data.get("weaknesses", []),
                    speech_pattern=char_data.get("speech_pattern", ""),
                    growth_arc_template=char_data.get("growth_arc_template", ""),
                )
                result.character_templates.append(template)

            # Parse plot patterns
            for plot_data in decon_data.get("plot_patterns", []):
                plot_type = self._str_to_enum(
                    plot_data.get("pattern_type", "three_act"),
                    PlotPatternType,
                    PlotPatternType.THREE_ACT,
                )
                pattern = PlotPattern(
                    id=self._make_id("plot"),
                    name=plot_data.get("name", "未命名模式"),
                    pattern_type=plot_type,
                    genre=book.genre,
                    source=source,
                    description=plot_data.get("description", ""),
                    structure_summary=plot_data.get("structure_summary", ""),
                    key_beat_templates=plot_data.get("key_beat_templates", []),
                    pacing_notes=plot_data.get("pacing_notes", ""),
                    tension_curve=plot_data.get("tension_curve", []),
                )
                result.plot_patterns.append(pattern)

            # Parse world template
            world_data = decon_data.get("world_template")
            if world_data:
                world_type = self._str_to_enum(
                    world_data.get("template_type", "fantasy"),
                    WorldTemplateType,
                    WorldTemplateType.FANTASY,
                )
                world_template = WorldTemplate(
                    id=self._make_id("world"),
                    name=world_data.get("name", "未命名世界观"),
                    template_type=world_type,
                    genre=book.genre,
                    source=source,
                    world_summary=world_data.get("world_summary", ""),
                    geography_template=world_data.get("geography_template", {}),
                    political_template=world_data.get("political_template", {}),
                    cultural_template=world_data.get("cultural_template", {}),
                    magic_system_template=world_data.get("magic_system_template"),
                    recurring_locations=world_data.get("recurring_locations", []),
                    typical_conflicts=world_data.get("typical_conflicts", []),
                )
                result.world_template = world_template

            # Parse overall analysis
            result.genre_classification = decon_data.get("genre_classification", book.genre)
            result.tone_and_style = decon_data.get("tone_and_style", "")
            result.target_audience = decon_data.get("target_audience", "")

            result.status = "completed"

        except Exception as e:
            result.status = f"failed: {str(e)}"

        # Save to database
        self.db.save_result_with_templates(result)

        return result

    async def deconstruct_from_hot_list(
        self,
        entry_id: Optional[str] = None,
        entry_name: Optional[str] = None,
        max_books: int = 5,
        max_chapters_per_book: int = 3,
    ) -> list[DeconstructionResult]:
        """Deconstruct books from a Fanqie hot list entry.

        Args:
            entry_id: Hot list entry ID (fetches from web if None)
            entry_name: Name of the entry (for logging)
            max_books: Maximum number of books to deconstruct
            max_chapters_per_book: Max chapters to fetch per book for analysis

        Returns:
            List of deconstruction results
        """
        print(f"[BookDeconstructor] Fetching books from hot list entry: {entry_name or entry_id}")

        # Get books from entry
        if entry_id:
            books = await self.crawler.get_books_by_entry(entry_id, limit=max_books)
        else:
            # Try to find entry by name
            hot_entries = await self.crawler.get_hot_list(limit=20)
            matched = [e for e in hot_entries if entry_name and entry_name in e.name]
            if matched:
                books = await self.crawler.get_books_by_entry(matched[0].id, limit=max_books)
            else:
                print(f"[BookDeconstructor] Entry not found: {entry_name}")
                return []

        print(f"[BookDeconstructor] Found {len(books)} books")

        results = []
        for book in books:
            print(f"[BookDeconstructor] Deconstructing: {book.title} by {book.author}")

            # Fetch chapter samples for deeper analysis
            chapter_samples = []
            chapters = await self.crawler.get_book_chapters(book.id, limit=max_chapters_per_book)
            # Note: chapter content fetching would require more API access
            # For now, we work with synopsis

            try:
                result = await self.deconstruct_book(book, chapter_samples)
                results.append(result)
                print(f"[BookDeconstructor] Completed: {book.title} - {result.status}")
            except Exception as e:
                print(f"[BookDeconstructor] Failed to deconstruct {book.title}: {e}")

        return results

    async def deconstruct_popular_books(
        self,
        genre: str = "",
        limit: int = 10,
    ) -> list[DeconstructionResult]:
        """Deconstruct popular books from Fanqie.

        Args:
            genre: Genre filter (empty for all genres)
            limit: Maximum number of books to deconstruct

        Returns:
            List of deconstruction results
        """
        print(f"[BookDeconstructor] Fetching popular books (genre={genre or 'all'})")

        books = await self.crawler.get_popular_books(genre=genre, limit=limit)
        print(f"[BookDeconstructor] Found {len(books)} popular books")

        results = []
        for book in books:
            print(f"[BookDeconstructor] Deconstructing: {book.title}")

            try:
                result = await self.deconstruct_book(book)
                results.append(result)
                print(f"[BookDeconstructor] Completed: {book.title} - {result.status}")
            except Exception as e:
                print(f"[BookDeconstructor] Failed: {book.title}: {e}")

        return results

    def get_templates_for_outline(
        self,
        genre: str,
        num_characters: int = 5,
        num_plot_patterns: int = 3,
    ) -> tuple[list[CharacterTemplate], list[PlotPattern], Optional[WorldTemplate]]:
        """Get templates from database for generating an outline.

        Args:
            genre: Genre to get templates for
            num_characters: Number of character templates to return
            num_plot_patterns: Number of plot patterns to return

        Returns:
            Tuple of (character_templates, plot_patterns, world_template)
        """
        char_templates = self.db.get_character_templates(genre=genre, limit=num_characters)
        plot_patterns = self.db.get_plot_patterns(genre=genre, limit=num_plot_patterns)
        world_templates = self.db.get_world_templates(genre=genre, limit=1)
        world_template = world_templates[0] if world_templates else None

        return char_templates, plot_patterns, world_template

    async def generate_outline_with_templates(
        self,
        genre: str,
        theme: str,
    ) -> dict:
        """Generate a novel outline using stored templates.

        Args:
            genre: Novel genre
            theme: Central theme

        Returns:
            Novel outline dict
        """
        char_templates = self.db.get_character_templates(genre=genre, limit=5)
        plot_patterns = self.db.get_plot_patterns(genre=genre, limit=3)
        world_templates = self.db.get_world_templates(genre=genre, limit=1)
        world_template = world_templates[0] if world_templates else None

        char_dicts = [c.model_dump() for c in char_templates]
        plot_dicts = [p.model_dump() for p in plot_patterns]
        world_dict = world_template.model_dump() if world_template else None

        return await self.ai_service.generate_outline_from_templates(
            genre=genre,
            theme=theme,
            character_templates=char_dicts,
            plot_patterns=plot_dicts,
            world_template=world_dict,
        )


async def demo_deconstruct() -> None:
    """Demo: deconstruct books from Fanqie hot list."""
    from chai.services import AIService

    # Note: Requires ANTHROPIC_API_KEY
    api_key = None
    try:
        ai_service = AIService()
    except ValueError:
        print("ANTHROPIC_API_KEY not set, using mock mode")
        return

    async with BookDeconstructor(ai_service) as deconstructor:
        # Deconstruct from popular books
        results = await deconstructor.deconstruct_popular_books(genre="玄幻", limit=2)

        for result in results:
            print(f"Result: {result.source.book_title}")
            print(f"  Characters: {len(result.character_templates)}")
            print(f"  Plots: {len(result.plot_patterns)}")
            print(f"  World: {result.world_template is not None}")
