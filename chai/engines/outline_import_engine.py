"""Outline import engine for importing existing story outlines.

This engine handles importing story outlines from various formats (JSON, YAML,
Markdown, plain text) and provides functionality to continue writing from
where the user left off.
"""

import json
import re
import uuid
import yaml
from datetime import datetime
from typing import Optional

from chai.models.outline_import import (
    ImportFormat,
    ImportSource,
    OutlineValidationStatus,
    ChapterWritingStatus,
    ImportedVolume,
    ImportedChapter,
    ImportedScene,
    ImportedPlotThread,
    ImportedForeshadowing,
    ImportedCharacter,
    ImportedWorldSetting,
    RawOutlineData,
    OutlineImportResult,
    ContinuationContext,
    OutlineAnalysis,
    OutlineMergeRequest,
)
from chai.models.story_outline import (
    StoryOutline,
    StoryOutlineType,
    OutlineStatus,
    VolumeOutline,
    ChapterOutline,
    SceneOutline,
    PlotThread,
    ForeshadowingElement,
    ForeshadowingType,
    ForeshadowingStatus,
    PlotThreadType,
    TensionLevel,
    ScenePurpose,
)
from chai.models.novel import Novel, Volume, Chapter
from chai.services import AIService


class OutlineImportEngine:
    """Engine for importing existing story outlines and continuing writing.

    This engine supports:
    - Importing outlines from JSON, YAML, Markdown, and plain text formats
    - Parsing and validating imported outline structure
    - Analyzing writing progress from imported outline
    - Providing continuation context for resuming writing
    - Merging imported outlines with existing project data
    """

    # Markdown chapter pattern
    CHAPTER_PATTERN = re.compile(r'^第?[一二三四五六七八九十百千\d]+章|^Chapter\s+\d+|^第\d+话', re.IGNORECASE)
    VOLUME_PATTERN = re.compile(r'^第?[一二三四五六七八九十百千\d]+卷|^Volume\s+\d+|^第\d+部', re.IGNORECASE)

    def __init__(self, ai_service: Optional[AIService] = None):
        """Initialize outline import engine.

        Args:
            ai_service: Optional AI service for generating missing outline elements
        """
        self.ai_service = ai_service

    async def import_outline(
        self,
        content: str,
        import_format: ImportFormat,
        source: ImportSource = ImportSource.USER_FILE,
        original_file_name: Optional[str] = None,
    ) -> OutlineImportResult:
        """Import a story outline from content.

        Args:
            content: The outline content to import
            import_format: Format of the content
            source: Source of the import
            original_file_name: Original file name if applicable

        Returns:
            OutlineImportResult with import statistics and validation
        """
        raw_data = RawOutlineData(
            source_format=import_format,
            source=source,
            original_file_name=original_file_name,
        )

        try:
            # Parse based on format
            if import_format == ImportFormat.JSON:
                parsed = self._parse_json(content)
            elif import_format == ImportFormat.YAML:
                parsed = self._parse_yaml(content)
            elif import_format == ImportFormat.MARKDOWN:
                parsed = self._parse_markdown(content)
            elif import_format == ImportFormat.PLAIN_TEXT:
                parsed = self._parse_plain_text(content)
            elif import_format == ImportFormat.CHAPTER_OUTLINE:
                parsed = self._parse_chapter_outline(content)
            else:
                return OutlineImportResult(
                    success=False,
                    import_format=import_format,
                    source=source,
                    validation_status=OutlineValidationStatus.INVALID,
                    validation_errors=[f"Unsupported format: {import_format}"],
                )

            # Extract raw data
            raw_data.title = parsed.get("title", raw_data.title)
            raw_data.genre = parsed.get("genre", raw_data.genre)
            raw_data.theme = parsed.get("theme", raw_data.theme)
            raw_data.description = parsed.get("description", raw_data.description)
            raw_data.outline_type = parsed.get("outline_type", raw_data.outline_type)
            raw_data.target_word_count = parsed.get("target_word_count", raw_data.target_word_count)
            raw_data.target_chapter_count = parsed.get("target_chapter_count", raw_data.target_chapter_count)
            raw_data.volumes_data = parsed.get("volumes", [])
            raw_data.chapters_data = parsed.get("chapters", [])
            raw_data.scenes_data = parsed.get("scenes", [])
            raw_data.plot_threads_data = parsed.get("plot_threads", [])
            raw_data.foreshadowing_data = parsed.get("foreshadowing", [])
            raw_data.characters_data = parsed.get("characters", [])
            raw_data.world_setting_data = parsed.get("world_setting")

            # Validate and analyze
            validation_result = self._validate_raw_outline(raw_data)
            analysis = self._analyze_outline(raw_data)
            continuation = self._build_continuation_context(raw_data)

            # Count chapters by status
            total = len(raw_data.chapters_data)
            completed = sum(1 for c in raw_data.chapters_data if c.get("status") == "complete")
            partial = sum(1 for c in raw_data.chapters_data if c.get("status") == "partial" or c.get("content"))
            pending = total - completed - partial

            return OutlineImportResult(
                success=True,
                outline_id=f"imported_{uuid.uuid4().hex[:8]}",
                import_format=import_format,
                source=source,
                validation_status=validation_result["status"],
                validation_errors=validation_result.get("errors", []),
                validation_warnings=validation_result.get("warnings", []),
                total_chapters=total,
                completed_chapters=completed,
                partial_chapters=partial,
                pending_chapters=pending,
                writing_status_summary=analysis,
                next_chapter_to_write=continuation.get("next_chapter"),
                continuation_context=continuation,
                raw_data=raw_data,
            )

        except Exception as e:
            return OutlineImportResult(
                success=False,
                import_format=import_format,
                source=source,
                validation_status=OutlineValidationStatus.INVALID,
                validation_errors=[f"Import failed: {str(e)}"],
            )

    def _parse_json(self, content: str) -> dict:
        """Parse JSON content into dict."""
        data = json.loads(content)

        # Handle nested JSON strings (common when outline is serialized)
        if isinstance(data, str):
            data = json.loads(data)

        return data

    def _parse_yaml(self, content: str) -> dict:
        """Parse YAML content into dict."""
        return yaml.safe_load(content)

    def _parse_markdown(self, content: str) -> dict:
        """Parse Markdown outline into dict structure."""
        lines = content.strip().split('\n')
        result = {
            "title": "",
            "chapters": [],
            "volumes": [],
            "plot_threads": [],
            "foreshadowing": [],
        }

        current_volume = None
        current_chapter = None
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Title
            if line.startswith('# '):
                result["title"] = line[2:].strip()
                continue

            # Volume header
            if self.VOLUME_PATTERN.match(line):
                vol_match = re.search(r'第([一二三四五六七八九十百千\d]+)卷|Volume\s+(\d+)', line, re.IGNORECASE)
                if vol_match:
                    vol_num = vol_match.group(1) or vol_match.group(2)
                    if vol_num.isdigit():
                        vol_num = int(vol_num)
                    else:
                        vol_num = self._chinese_to_number(vol_num)
                    current_volume = {
                        "number": vol_num,
                        "title": line.replace('#', '').strip(),
                        "description": "",
                        "chapter_start": 0,
                        "chapter_end": 0,
                    }
                    result["volumes"].append(current_volume)
                continue

            # Chapter header
            if self.CHAPTER_PATTERN.match(line):
                ch_match = re.search(r'第?([一二三四五六七八九十百千\d]+)章|第(\d+)话|Chapter\s+(\d+)', line, re.IGNORECASE)
                if ch_match:
                    ch_num = ch_match.group(1) or ch_match.group(2) or ch_match.group(3)
                    if ch_num.isdigit():
                        ch_num = int(ch_num)
                    else:
                        ch_num = self._chinese_to_number(ch_num)
                    current_chapter = {
                        "number": ch_num,
                        "title": line.replace('#', '').strip(),
                        "summary": "",
                        "status": "pending",
                    }
                    result["chapters"].append(current_chapter)
                    if current_volume:
                        if current_volume.get("chapter_start") == 0:
                            current_volume["chapter_start"] = ch_num
                        current_volume["chapter_end"] = ch_num
                continue

            # Section content
            if current_chapter:
                if line.startswith('## '):
                    current_section = line[3:].strip().lower()
                    continue
                if current_section == "summary" or (not current_section and line.startswith('- ')):
                    current_chapter["summary"] += line.lstrip('- ').strip() + " "

        return result

    def _parse_plain_text(self, content: str) -> dict:
        """Parse plain text outline into dict structure."""
        lines = content.strip().split('\n')
        result = {
            "chapters": [],
            "plot_threads": [],
        }

        current_chapter = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Chapter pattern
            ch_match = re.search(r'第?([一二三四五六七八九十百千\d]+)章|第(\d+)话|Chapter\s+(\d+)|^\[(\d+)\]', line, re.IGNORECASE)
            if ch_match:
                ch_num = ch_match.group(1) or ch_match.group(2) or ch_match.group(3) or ch_match.group(4)
                if ch_num.isdigit():
                    ch_num = int(ch_num)
                else:
                    ch_num = self._chinese_to_number(ch_num)

                # Extract title after chapter number
                title_match = re.search(r'章[：:]\s*(.+?)(?:\s*\[|$)', line)
                title = title_match.group(1).strip() if title_match else line

                current_chapter = {
                    "number": ch_num,
                    "title": title,
                    "summary": "",
                    "status": "pending",
                }
                result["chapters"].append(current_chapter)
                continue

            # Summary line
            if current_chapter and line:
                current_chapter["summary"] += line + " "

        return result

    def _parse_chapter_outline(self, content: str) -> dict:
        """Parse chapter-based outline format."""
        # Try to detect format from content
        if content.strip().startswith('{'):
            return self._parse_json(content)
        elif content.strip().startswith('---'):
            return self._parse_yaml(content)
        elif '#' in content[:100]:
            return self._parse_markdown(content)
        else:
            return self._parse_plain_text(content)

    def _chinese_to_number(self, chinese: str) -> int:
        """Convert Chinese number to integer."""
        chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000,
        }
        result = 0
        temp = 0
        for char in chinese:
            if char in chinese_nums:
                val = chinese_nums[char]
                if val >= 100:
                    temp = temp * val if temp else val
                else:
                    temp += val
        return result + temp

    def _validate_raw_outline(self, raw: RawOutlineData) -> dict:
        """Validate raw outline data."""
        errors = []
        warnings = []

        # Check basic required fields
        if not raw.title:
            warnings.append("Title is missing")

        if not raw.genre:
            warnings.append("Genre is not specified")

        # Check chapters
        if not raw.chapters_data:
            warnings.append("No chapters found in outline")
            return {"status": OutlineValidationStatus.EMPTY, "errors": errors, "warnings": warnings}

        # Check chapter numbers
        chapter_numbers = [c.get("number") for c in raw.chapters_data]
        chapter_numbers = [n for n in chapter_numbers if n is not None]

        if len(chapter_numbers) != len(set(chapter_numbers)):
            duplicates = set([n for n in chapter_numbers if chapter_numbers.count(n) > 1])
            warnings.append(f"Duplicate chapter numbers found: {duplicates}")

        # Check for gaps in chapter numbers
        if chapter_numbers:
            min_ch, max_ch = min(chapter_numbers), max(chapter_numbers)
            expected_range = set(range(min_ch, max_ch + 1))
            actual = set(chapter_numbers)
            missing = expected_range - actual
            if missing:
                warnings.append(f"Missing chapter numbers: {sorted(missing)}")

        # Validate chapter structure
        for i, chapter in enumerate(raw.chapters_data):
            if not chapter.get("number"):
                errors.append(f"Chapter {i} is missing chapter number")
            if not chapter.get("title"):
                warnings.append(f"Chapter {chapter.get('number', i+1)} is missing title")

        if errors:
            return {"status": OutlineValidationStatus.INVALID, "errors": errors, "warnings": warnings}
        elif warnings:
            return {"status": OutlineValidationStatus.PARTIAL, "errors": errors, "warnings": warnings}
        else:
            return {"status": OutlineValidationStatus.VALID, "errors": errors, "warnings": warnings}

    def _analyze_outline(self, raw: RawOutlineData) -> dict:
        """Analyze imported outline structure."""
        analysis = {
            "total_chapters": len(raw.chapters_data),
            "chapters_with_summaries": 0,
            "chapters_with_content": 0,
            "chapters_empty": 0,
            "total_word_count": 0,
        }

        for chapter in raw.chapters_data:
            summary = chapter.get("summary", "")
            content = chapter.get("content", "")
            word_count = chapter.get("word_count", 0)

            if content and len(content) > 100:
                analysis["chapters_with_content"] += 1
                analysis["total_word_count"] += word_count or len(content)
            elif summary and len(summary) > 20:
                analysis["chapters_with_summaries"] += 1
            else:
                analysis["chapters_empty"] += 1

        if analysis["total_chapters"] > 0:
            analysis["writing_progress_percentage"] = (
                analysis["chapters_with_content"] / analysis["total_chapters"] * 100
            )
            analysis["average_chapter_word_count"] = (
                analysis["total_word_count"] / max(1, analysis["chapters_with_content"])
            )
        else:
            analysis["writing_progress_percentage"] = 0
            analysis["average_chapter_word_count"] = 0

        return analysis

    def _build_continuation_context(self, raw: RawOutlineData) -> dict:
        """Build continuation context from imported outline."""
        chapters = sorted(raw.chapters_data, key=lambda x: x.get("number", 0))

        # Find next chapter to write
        next_chapter = None
        last_written = None
        last_content = None

        for chapter in chapters:
            content = chapter.get("content", "")
            status = chapter.get("status", "pending")

            if status == "complete" or (content and len(content) > 100):
                last_written = chapter.get("number")
                last_content = content[-500:] if content else None
            elif next_chapter is None:
                next_chapter = chapter.get("number")

        # Get pending chapters
        pending = [
            {"number": c.get("number"), "title": c.get("title", f"第{c.get('number')}章")}
            for c in chapters
            if not c.get("content") or len(c.get("content", "")) < 100
        ]

        # Get active plot threads
        active_threads = []
        if last_written:
            for thread in raw.plot_threads_data:
                chapters_active = thread.get("chapters_active", [])
                if any(c > last_written for c in chapters_active):
                    active_threads.append(thread.get("name", ""))

        # Get pending foreshadowing (as list of strings for model compatibility)
        pending_foreshadowing = [
            f.get("element", "")
            for f in raw.foreshadowing_data
            if f.get("status") != "payed_off" and f.get("chapter_payoff", 0) > (last_written or 0)
        ]

        return {
            "story_title": raw.title or "未命名小说",
            "genre": raw.genre or "unknown",
            "next_chapter": next_chapter or (last_written + 1 if last_written else 1),
            "last_written_chapter": last_written,
            "last_content_excerpt": last_content,
            "pending_chapters": pending,
            "active_plot_threads": active_threads,
            "pending_foreshadowing": pending_foreshadowing,
        }

    def convert_to_story_outline(self, import_result: OutlineImportResult) -> StoryOutline:
        """Convert import result to StoryOutline model.

        Args:
            import_result: Result from import_outline()

        Returns:
            StoryOutline model ready for the writing system
        """
        raw = import_result.raw_data
        if not raw:
            raise ValueError("No raw outline data in import result")

        outline_id = import_result.outline_id

        # Convert volumes
        volumes = []
        for vol_data in raw.volumes_data:
            volumes.append(VolumeOutline(
                id=f"{outline_id}_vol_{vol_data.get('number', len(volumes)+1)}",
                number=vol_data.get("number", len(volumes)+1),
                title=vol_data.get("title", f"第{len(volumes)+1}卷"),
                chapter_start=vol_data.get("chapter_start", 0),
                chapter_end=vol_data.get("chapter_end", 0),
                description=vol_data.get("description", ""),
                theme=vol_data.get("theme", ""),
                central_conflict=vol_data.get("central_conflict", ""),
                status=OutlineStatus.PENDING,
            ))

        # Convert chapters
        chapters = []
        for ch_data in raw.chapters_data:
            tension_str = ch_data.get("tension_level", "moderate")
            try:
                tension = TensionLevel(tension_str)
            except ValueError:
                tension = TensionLevel.MODERATE

            chapters.append(ChapterOutline(
                id=f"{outline_id}_ch_{ch_data.get('number', len(chapters)+1)}",
                number=ch_data.get("number", len(chapters)+1),
                title=ch_data.get("title", f"第{len(chapters)+1}章"),
                is_prologue=ch_data.get("is_prologue", False),
                is_epilogue=ch_data.get("is_epilogue", False),
                is_bridge=ch_data.get("is_bridge", False),
                summary=ch_data.get("summary", ""),
                pov_character=ch_data.get("pov_character"),
                characters_involved=ch_data.get("characters_involved", []),
                tension_level=tension,
                pacing_notes=ch_data.get("pacing_notes", ""),
                scene_summaries=ch_data.get("scene_summaries", []),
                plot_threads_advanced=ch_data.get("plot_threads_advanced", []),
                foreshadowing_planted=ch_data.get("foreshadowing_planted", []),
                foreshadowing_payoffs=ch_data.get("foreshadowing_payoffs", []),
                status=OutlineStatus.PENDING,
                target_word_count=ch_data.get("target_word_count", 3000),
            ))

        # Convert plot threads
        plot_threads = []
        for thread_data in raw.plot_threads_data:
            try:
                thread_type = PlotThreadType(thread_data.get("thread_type", "subplot"))
            except ValueError:
                thread_type = PlotThreadType.SUBPLOT

            plot_threads.append(PlotThread(
                id=f"{outline_id}_thread_{len(plot_threads)}",
                name=thread_data.get("name", "未命名线索"),
                thread_type=thread_type,
                description=thread_data.get("description", ""),
                chapters_active=thread_data.get("chapters_active", []),
                status=OutlineStatus.PENDING,
                current_state=thread_data.get("current_state", ""),
                key_events=thread_data.get("key_events", []),
            ))

        # Convert foreshadowing
        foreshadowing_elements = []
        for fore_data in raw.foreshadowing_data:
            try:
                fore_type = ForeshadowingType(fore_data.get("foreshadowing_type", "indirect"))
            except ValueError:
                fore_type = ForeshadowingType.INDIRECT

            try:
                fore_status = ForeshadowingStatus(fore_data.get("status", "planted"))
            except ValueError:
                fore_status = ForeshadowingStatus.PLANTED

            foreshadowing_elements.append(ForeshadowingElement(
                id=f"{outline_id}_fore_{len(foreshadowing_elements)}",
                element=fore_data.get("element", ""),
                foreshadowing_type=fore_type,
                chapter_planted=fore_data.get("chapter_planted", 1),
                scene_location=fore_data.get("scene_location", ""),
                description=fore_data.get("description", ""),
                chapter_payoff=fore_data.get("chapter_payoff"),
                payoff_description=fore_data.get("payoff_description", ""),
                status=fore_status,
                subtlety_level=fore_data.get("subtlety_level", 0.5),
            ))

        # Try to parse outline type
        try:
            outline_type = StoryOutlineType(raw.outline_type)
        except ValueError:
            outline_type = StoryOutlineType.THREE_ACT

        return StoryOutline(
            id=outline_id,
            title=raw.title or "导入大纲",
            genre=raw.genre or "unknown",
            theme=raw.theme or "",
            outline_type=outline_type,
            target_word_count=raw.target_word_count,
            target_chapter_count=raw.target_chapter_count or len(chapters),
            volumes=volumes,
            chapters=chapters,
            plot_threads=plot_threads,
            foreshadowing_elements=foreshadowing_elements,
            status=OutlineStatus.IN_PROGRESS,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def get_continuation_context(
        self,
        import_result: OutlineImportResult,
        written_content: Optional[dict] = None,
    ) -> ContinuationContext:
        """Get detailed continuation context for resuming writing.

        Args:
            import_result: Result from import_outline()
            written_content: Optional dict of chapter_number -> content for
                           updating continuation context

        Returns:
            ContinuationContext with detailed information for continuing
        """
        raw = import_result.raw_data
        if not raw:
            return ContinuationContext(
                story_title="未命名小说",
                genre="unknown",
            )

        context = self._build_continuation_context(raw)

        # Build written chapters summary
        written_summary = []
        for chapter in sorted(raw.chapters_data, key=lambda x: x.get("number", 0)):
            content = chapter.get("content", "")
            if written_content:
                content = written_content.get(chapter.get("number"), content)

            if content and len(content) > 100:
                written_summary.append({
                    "chapter": chapter.get("number"),
                    "title": chapter.get("title", f"第{chapter.get('number')}章"),
                    "word_count": chapter.get("word_count") or len(content),
                    "summary": chapter.get("summary", "")[:100],
                })

        # Character states from imported outline
        character_states = {}
        for char in raw.characters_data:
            character_states[char.get("name", "")] = {
                "role": char.get("role", "supporting"),
                "description": char.get("description", ""),
            }

        return ContinuationContext(
            story_title=raw.title or "未命名小说",
            genre=raw.genre or "unknown",
            last_written_chapter=context.get("last_written_chapter"),
            last_written_scene=None,
            written_chapters_summary=written_summary,
            last_content_excerpt=context.get("last_content_excerpt"),
            pending_chapters=[
                ImportedChapter(**c)
                for c in raw.chapters_data
                if not c.get("content") or len(c.get("content", "")) < 100
            ],
            active_plot_threads=context.get("active_plot_threads", []),
            pending_foreshadowing=context.get("pending_foreshadowing", []),
            character_states=character_states,
            world_context=raw.world_setting_data.get("description", "") if raw.world_setting_data else "",
        )

    def get_next_chapter_to_write(
        self,
        import_result: OutlineImportResult,
    ) -> Optional[ImportedChapter]:
        """Get the next chapter that should be written.

        Args:
            import_result: Result from import_outline()

        Returns:
            ImportedChapter for the next chapter to write, or None
        """
        raw = import_result.raw_data
        if not raw:
            return None

        # Sort chapters by number
        chapters = sorted(raw.chapters_data, key=lambda x: x.get("number", 0))

        # Find first incomplete chapter
        for chapter in chapters:
            content = chapter.get("content", "")
            status = chapter.get("status", "pending")

            if status != "complete" and (not content or len(content) < 100):
                return ImportedChapter(**chapter)

        return None

    def merge_with_existing_project(
        self,
        import_result: OutlineImportResult,
        existing_outline: Optional[StoryOutline] = None,
        request: Optional[OutlineMergeRequest] = None,
    ) -> StoryOutline:
        """Merge imported outline with existing project.

        Args:
            import_result: Result from import_outline()
            existing_outline: Optional existing StoryOutline to merge with
            request: Optional merge request with specific instructions

        Returns:
            Merged StoryOutline
        """
        imported_outline = self.convert_to_story_outline(import_result)

        if not existing_outline:
            return imported_outline

        if not request:
            request = OutlineMergeRequest(
                imported_outline=import_result.raw_data,
                preserve_existing_content=True,
                fill_missing_outline=True,
            )

        # Merge chapters - prefer existing for completed chapters
        existing_chapters = {c.number: c for c in existing_outline.chapters}
        merged_chapters = []

        for imported_ch in imported_outline.chapters:
            existing_ch = existing_chapters.get(imported_ch.number)

            if existing_ch and request.preserve_existing_content:
                # Keep existing chapter content
                merged_chapters.append(existing_ch)
            else:
                merged_chapters.append(imported_ch)

        # Sort by chapter number
        merged_chapters.sort(key=lambda c: c.number)

        # Merge volumes
        existing_volumes = {v.number: v for v in existing_outline.volumes}
        merged_volumes = list(existing_outline.volumes)

        for imported_vol in imported_outline.volumes:
            if imported_vol.number not in existing_volumes:
                merged_volumes.append(imported_vol)

        merged_volumes.sort(key=lambda v: v.number)

        # Merge plot threads - combine all
        merged_threads = list(existing_outline.plot_threads)
        imported_thread_ids = {t.name for t in merged_threads}

        for imported_thread in imported_outline.plot_threads:
            if imported_thread.name not in imported_thread_ids:
                merged_threads.append(imported_thread)

        # Merge foreshadowing
        merged_foreshadowing = list(existing_outline.foreshadowing_elements)
        imported_fore_ids = {f.element for f in merged_foreshadowing}

        for imported_fore in imported_outline.foreshadowing_elements:
            if imported_fore.element not in imported_fore_ids:
                merged_foreshadowing.append(imported_fore)

        # Build merged outline
        return StoryOutline(
            id=existing_outline.id,
            title=existing_outline.title,
            genre=existing_outline.genre,
            theme=existing_outline.theme,
            outline_type=existing_outline.outline_type,
            target_word_count=existing_outline.target_word_count,
            target_chapter_count=existing_outline.target_chapter_count,
            volumes=merged_volumes,
            chapters=merged_chapters,
            scenes=existing_outline.scenes,
            plot_threads=merged_threads,
            foreshadowing_elements=merged_foreshadowing,
            main_character_ids=existing_outline.main_character_ids,
            supporting_character_ids=existing_outline.supporting_character_ids,
            antagonist_ids=existing_outline.antagonist_ids,
            world_setting_id=existing_outline.world_setting_id,
            status=OutlineStatus.IN_PROGRESS,
            updated_at=datetime.now().isoformat(),
        )

    def export_outline_summary(self, import_result: OutlineImportResult) -> str:
        """Export a human-readable summary of the imported outline.

        Args:
            import_result: Result from import_outline()

        Returns:
            Summary string
        """
        if not import_result.success:
            return f"导入失败: {import_result.validation_errors}"

        raw = import_result.raw_data
        if not raw:
            return "导入成功，但无原始数据"

        lines = [
            f"《{raw.title or '未命名小说'}》",
            f"类型：{raw.genre or '未指定'}",
            f"主题：{raw.theme or '未指定'}",
            f"",
            f"导入格式：{import_result.import_format.value}",
            f"验证状态：{import_result.validation_status.value}",
            f"",
            f"=== 章节概览 ===",
            f"总章节数：{import_result.total_chapters}",
            f"已完成：{import_result.completed_chapters}",
            f"部分完成：{import_result.partial_chapters}",
            f"待写作：{import_result.pending_chapters}",
            f"写作进度：{import_result.writing_status_summary.get('writing_progress_percentage', 0):.1f}%",
            f"",
            f"=== 续写位置 ===",
        ]

        next_ch = import_result.next_chapter_to_write
        if next_ch:
            lines.append(f"建议从第 {next_ch} 章开始继续写作")
        else:
            lines.append("所有章节已完成")

        if import_result.continuation_context.get("pending_chapters"):
            pending = import_result.continuation_context["pending_chapters"][:3]
            lines.append("待写章节：")
            for p in pending:
                lines.append(f"  - 第{p.get('number')}章: {p.get('title', '未命名')}")

        return "\n".join(lines)