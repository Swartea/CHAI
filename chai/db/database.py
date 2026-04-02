"""File-based database for storing book deconstruction results.

Uses JSON files for persistence. Suitable for single-user local storage.
For production, consider migrating to SQLite or a proper database.
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from chai.models.deconstruct import (
    CharacterTemplate,
    PlotPattern,
    WorldTemplate,
    DeconstructionResult,
)


DATA_DIR = Path.home() / ".chai" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class DeconstructDB:
    """File-based database for deconstruction templates and results."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the database.

        Args:
            data_dir: Directory for data files. Defaults to ~/.chai/data
        """
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._character_file = self.data_dir / "character_templates.json"
        self._plot_file = self.data_dir / "plot_patterns.json"
        self._world_file = self.data_dir / "world_templates.json"
        self._results_file = self.data_dir / "deconstruction_results.json"
        self._lock = threading.Lock()

    def _read_json(self, path: Path) -> dict:
        """Read JSON data from file."""
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: dict) -> None:
        """Write JSON data to file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    # --- Character Templates ---

    def save_character_template(self, template: CharacterTemplate) -> None:
        """Save a character template."""
        with self._lock:
            data = self._read_json(self._character_file)
            data[template.id] = template.model_dump(mode="json")
            self._write_json(self._character_file, data)

    def get_character_template(self, template_id: str) -> Optional[CharacterTemplate]:
        """Get a character template by ID."""
        data = self._read_json(self._character_file)
        item = data.get(template_id)
        if item:
            return CharacterTemplate(**item)
        return None

    def get_character_templates(
        self,
        genre: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[CharacterTemplate]:
        """Get character templates with optional filters."""
        data = self._read_json(self._character_file)
        results = []
        for item in data.values():
            if genre and item.get("genre") != genre:
                continue
            if template_type and item.get("template_type") != template_type:
                continue
            results.append(CharacterTemplate(**item))
        results.sort(key=lambda t: t.usage_count, reverse=True)
        return results[:limit]

    def increment_character_usage(self, template_id: str) -> None:
        """Increment usage count for a character template."""
        with self._lock:
            data = self._read_json(self._character_file)
            if template_id in data:
                data[template_id]["usage_count"] = data[template_id].get("usage_count", 0) + 1
                data[template_id]["updated_at"] = datetime.now().isoformat()
                self._write_json(self._character_file, data)

    # --- Plot Patterns ---

    def save_plot_pattern(self, pattern: PlotPattern) -> None:
        """Save a plot pattern."""
        with self._lock:
            data = self._read_json(self._plot_file)
            data[pattern.id] = pattern.model_dump(mode="json")
            self._write_json(self._plot_file, data)

    def get_plot_pattern(self, pattern_id: str) -> Optional[PlotPattern]:
        """Get a plot pattern by ID."""
        data = self._read_json(self._plot_file)
        item = data.get(pattern_id)
        if item:
            return PlotPattern(**item)
        return None

    def get_plot_patterns(
        self,
        genre: Optional[str] = None,
        pattern_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[PlotPattern]:
        """Get plot patterns with optional filters."""
        data = self._read_json(self._plot_file)
        results = []
        for item in data.values():
            if genre and item.get("genre") != genre:
                continue
            if pattern_type and item.get("pattern_type") != pattern_type:
                continue
            results.append(PlotPattern(**item))
        results.sort(key=lambda p: p.usage_count, reverse=True)
        return results[:limit]

    def increment_plot_usage(self, pattern_id: str) -> None:
        """Increment usage count for a plot pattern."""
        with self._lock:
            data = self._read_json(self._plot_file)
            if pattern_id in data:
                data[pattern_id]["usage_count"] = data[pattern_id].get("usage_count", 0) + 1
                data[pattern_id]["updated_at"] = datetime.now().isoformat()
                self._write_json(self._plot_file, data)

    # --- World Templates ---

    def save_world_template(self, template: WorldTemplate) -> None:
        """Save a world template."""
        with self._lock:
            data = self._read_json(self._world_file)
            data[template.id] = template.model_dump(mode="json")
            self._write_json(self._world_file, data)

    def get_world_template(self, template_id: str) -> Optional[WorldTemplate]:
        """Get a world template by ID."""
        data = self._read_json(self._world_file)
        item = data.get(template_id)
        if item:
            return WorldTemplate(**item)
        return None

    def get_world_templates(
        self,
        genre: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[WorldTemplate]:
        """Get world templates with optional filters."""
        data = self._read_json(self._world_file)
        results = []
        for item in data.values():
            if genre and item.get("genre") != genre:
                continue
            if template_type and item.get("template_type") != template_type:
                continue
            results.append(WorldTemplate(**item))
        results.sort(key=lambda t: t.usage_count, reverse=True)
        return results[:limit]

    def increment_world_usage(self, template_id: str) -> None:
        """Increment usage count for a world template."""
        with self._lock:
            data = self._read_json(self._world_file)
            if template_id in data:
                data[template_id]["usage_count"] = data[template_id].get("usage_count", 0) + 1
                data[template_id]["updated_at"] = datetime.now().isoformat()
                self._write_json(self._world_file, data)

    # --- Deconstruction Results ---

    def save_result(self, result: DeconstructionResult) -> None:
        """Save a deconstruction result."""
        with self._lock:
            data = self._read_json(self._results_file)
            data[result.id] = result.model_dump(mode="json")
            self._write_json(self._results_file, data)

    def get_result(self, result_id: str) -> Optional[DeconstructionResult]:
        """Get a deconstruction result by ID."""
        data = self._read_json(self._results_file)
        item = data.get(result_id)
        if item:
            return DeconstructionResult(**item)
        return None

    def get_results(
        self,
        genre: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[DeconstructionResult]:
        """Get deconstruction results with optional filters."""
        data = self._read_json(self._results_file)
        results = []
        for item in data.values():
            if genre and item.get("genre_classification") != genre:
                continue
            if status and item.get("status") != status:
                continue
            results.append(DeconstructionResult(**item))
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit]

    # --- Stats ---

    def get_stats(self) -> dict:
        """Get database statistics."""
        char_data = self._read_json(self._character_file)
        plot_data = self._read_json(self._plot_file)
        world_data = self._read_json(self._world_file)
        result_data = self._read_json(self._results_file)

        return {
            "character_templates": len(char_data),
            "plot_patterns": len(plot_data),
            "world_templates": len(world_data),
            "deconstruction_results": len(result_data),
            "data_dir": str(self.data_dir),
        }

    # --- Bulk Operations ---

    def save_result_with_templates(
        self,
        result: DeconstructionResult,
    ) -> None:
        """Save a deconstruction result along with all extracted templates."""
        self.save_result(result)

        for char_tmpl in result.character_templates:
            self.save_character_template(char_tmpl)

        for plot_pat in result.plot_patterns:
            self.save_plot_pattern(plot_pat)

        if result.world_template:
            self.save_world_template(result.world_template)

    def get_all_templates_for_genre(self, genre: str) -> dict:
        """Get all templates for a specific genre.

        Returns dict with 'characters', 'plots', 'worlds' keys.
        """
        return {
            "characters": self.get_character_templates(genre=genre, limit=100),
            "plots": self.get_plot_patterns(genre=genre, limit=100),
            "worlds": self.get_world_templates(genre=genre, limit=100),
        }


# --- Default Database Instance ---

_default_db: Optional[DeconstructDB] = None


def get_default_db() -> DeconstructDB:
    """Get the default database instance."""
    global _default_db
    if _default_db is None:
        _default_db = DeconstructDB()
    return _default_db
