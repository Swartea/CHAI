"""EPUB manuscript export engine.

This module provides comprehensive EPUB export functionality with support for
metadata, navigation, chapter formatting, CSS styling, and multiple output
templates following the EPUB 2.0/3.0 specifications.
"""

import zipfile
import html
from datetime import datetime
from pathlib import Path
from typing import Optional

from chai.models import Novel, Volume, Chapter, Scene
from chai.models.epub_export import (
    EPUBTemplate,
    EPUBExportConfig,
    EPUBExportResult,
    EPUBMetadata,
    EPUBChapterRef,
    EPUBVolumeRef,
    EPUBNavPoint,
    EPUBSpineItem,
    EPUBManifestItem,
    EPUBTemplateStyles,
    EPUBCSSStyle,
)


class EPUBManuscriptEngine:
    """Engine for generating EPUB formatted manuscripts."""

    def __init__(self, config: Optional[EPUBExportConfig] = None):
        """Initialize the EPUB manuscript engine.

        Args:
            config: Export configuration. Uses defaults if not provided.
        """
        self.config = config or EPUBExportConfig()
        self._css_style = self._get_css_template()

    def generate_manuscript(self, novel: Novel) -> EPUBExportResult:
        """Generate a complete EPUB manuscript.

        Args:
            novel: The novel to export.

        Returns:
            EPUBExportResult with the generated EPUB metadata and references.
        """
        result = EPUBExportResult(config=self.config)

        # Generate metadata
        if self.config.template != EPUBTemplate.SIMPLE:
            result.metadata = self._create_metadata(novel)

        # Generate volume and chapter references
        result.volumes = self._create_volume_refs(novel)

        # Calculate total word count
        result.word_count = sum(c.word_count for v in novel.volumes for c in v.chapters)

        return result

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export manuscript to an EPUB file.

        Args:
            novel: The novel to export.
            output_path: Path to write the EPUB file.

        Returns:
            Path to the created EPUB file.
        """
        path = Path(output_path)
        result = self.generate_manuscript(novel)

        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as epub:
            self._write_mimetype(epub)
            self._write_container(epub)

            # Write content.opf
            self._write_content_opf(epub, novel, result)

            # Write navigation document (EPUB 3.0)
            if self.config.include_table_of_contents:
                self._write_navigation(epub, novel, result)

            # Write NCX (EPUB 2.0 backward compatibility)
            self._write_ncx(epub, novel, result)

            # Write CSS
            self._write_css(epub)

            # Write front matter
            if result.metadata:
                self._write_front_matter(epub, result.metadata)

            # Write chapters
            self._write_chapters(epub, novel, result)

            # Write back matter
            if self.config.template == EPUBTemplate.DETAILED and result.metadata:
                self._write_back_matter(epub, novel, result.metadata)

        result.success = True
        result.output_path = str(path)
        result.file_size = path.stat().st_size

        return path

    def _get_css_template(self) -> EPUBCSSStyle:
        """Get CSS template based on configuration."""
        if self.config.template == EPUBTemplate.SIMPLE:
            return EPUBTemplateStyles.get_simple_css()
        elif self.config.template == EPUBTemplate.DETAILED:
            return EPUBTemplateStyles.get_detailed_css()
        else:
            return EPUBTemplateStyles.get_standard_css()

    def _assemble_css(self) -> str:
        """Assemble complete CSS from template."""
        parts = [
            "/* Base styles */",
            self._css_style.body,
            "/* Heading styles */",
            self._css_style.h1,
            self._css_style.h2,
            self._css_style.h3,
            "/* Paragraph styles */",
            self._css_style.p,
            self._css_style.p_first,
            "/* Special elements */",
            self._css_style.scene_break,
            self._css_style.chapter_title,
            self._css_style.volume_title,
            self._css_style.front_matter,
            self._css_style.back_matter,
            self._css_style.toc,
        ]
        return "\n".join(parts)

    def _create_metadata(self, novel: Novel) -> EPUBMetadata:
        """Create EPUB metadata."""
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)

        return EPUBMetadata(
            title=novel.title,
            author=getattr(novel, 'author', 'CHAI'),
            language="zh-CN",
            publisher="CHAI - AI Novel Writer",
            publish_date=datetime.now().strftime("%Y-%m-%d"),
            genre=novel.genre,
            description=getattr(novel, 'description', ''),
            rights="© CHAI",
            total_words=total_words,
            total_chapters=total_chapters,
            total_volumes=len(novel.volumes),
            creation_date=datetime.now().strftime("%Y-%m-%d"),
        )

    def _create_volume_refs(self, novel: Novel) -> list[EPUBVolumeRef]:
        """Create volume and chapter references."""
        volumes = []

        for volume in novel.volumes:
            chapters = []
            for chapter in volume.chapters:
                chapters.append(EPUBChapterRef(
                    chapter_id=f"ch_{chapter.number:03d}",
                    chapter_number=chapter.number,
                    chapter_title=chapter.title,
                    is_prologue=chapter.is_prologue,
                    is_epilogue=chapter.is_epilogue,
                    file_path=f"chapter_{chapter.number:03d}.xhtml",
                ))

            volumes.append(EPUBVolumeRef(
                volume_id=f"vol_{volume.number:03d}",
                volume_number=volume.number,
                volume_title=volume.title,
                description=volume.description or "",
                chapters=chapters,
            ))

        return volumes

    def _write_mimetype(self, epub: zipfile.ZipFile) -> None:
        """Write mimetype file (must be first and uncompressed)."""
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

    def _write_container(self, epub: zipfile.ZipFile) -> None:
        """Write container.xml file."""
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        epub.writestr("META-INF/container.xml", container_xml)

    def _write_content_opf(self, epub: zipfile.ZipFile, novel: Novel, result: EPUBExportResult) -> None:
        """Write content.opf file."""
        uuid = f"urn:uuid:{novel.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Build manifest
        manifest_items = [
            EPUBManifestItem(id="ncx", href="toc.ncx", media_type="application/x-dtbncx+xml"),
            EPUBManifestItem(id="nav", href="nav.xhtml", media_type="application/xhtml+xml"),
            EPUBManifestItem(id="css", href="styles.css", media_type="text/css"),
        ]

        # Add front/back matter
        if result.metadata and self.config.template != EPUBTemplate.SIMPLE:
            manifest_items.append(EPUBManifestItem(id="front", href="front.xhtml", media_type="application/xhtml+xml"))
            manifest_items.append(EPUBManifestItem(id="back", href="back.xhtml", media_type="application/xhtml+xml"))

        # Add chapters
        for volume in novel.volumes:
            for chapter in volume.chapters:
                manifest_items.append(EPUBManifestItem(
                    id=f"ch_{chapter.number:03d}",
                    href=f"chapter_{chapter.number:03d}.xhtml",
                    media_type="application/xhtml+xml",
                ))

        # Build spine
        spine_items = [EPUBSpineItem(idref="nav", linear=False)]  # nav is not linear

        if result.metadata and self.config.template != EPUBTemplate.SIMPLE:
            spine_items.insert(0, EPUBSpineItem(idref="front", linear=True))
            spine_items.append(EPUBSpineItem(idref="back", linear=True))

        for volume in novel.volumes:
            for chapter in volume.chapters:
                spine_items.append(EPUBSpineItem(idref=f"ch_{chapter.number:03d}", linear=True))

        # Render manifest
        manifest_xml = []
        for item in manifest_items:
            manifest_xml.append(f'        <item id="{item.id}" href="{item.href}" media-type="{item.media_type}"/>')

        # Render spine
        spine_xml = []
        for item in spine_items:
            linear = "yes" if item.linear else "no"
            spine_xml.append(f'        <itemref idref="{item.idref}" linear="{linear}"/>')

        # Build metadata
        if result.metadata:
            metadata_xml = f"""    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{html.escape(result.metadata.title)}</dc:title>
        <dc:language>{result.metadata.language}</dc:language>
        <dc:identifier id="BookId">{uuid}</dc:identifier>
        <dc:creator>CHAI - AI Novel Writer</dc:creator>
        <dc:publisher>{html.escape(result.metadata.publisher)}</dc:publisher>
        <dc:subject>{html.escape(result.metadata.genre)}</dc:subject>
        <dc:date>{result.metadata.publish_date}</dc:date>
        <dc:rights>{html.escape(result.metadata.rights)}</dc:rights>
    </metadata>"""
        else:
            metadata_xml = f"""    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{html.escape(novel.title)}</dc:title>
        <dc:language>zh-CN</dc:language>
        <dc:identifier id="BookId">{uuid}</dc:identifier>
        <dc:creator>CHAI</dc:creator>
        <dc:subject>{html.escape(novel.genre)}</dc:subject>
    </metadata>"""

        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
{metadata_xml}
    <manifest>
{"\n".join(manifest_xml)}
    </manifest>
    <spine toc="ncx">
{"\n".join(spine_xml)}
    </spine>
</package>"""

        epub.writestr("OEBPS/content.opf", content_opf)

    def _write_navigation(self, epub: zipfile.ZipFile, novel: Novel, result: EPUBExportResult) -> None:
        """Write EPUB 3.0 navigation document."""
        nav_points = []

        # Add front matter link if present
        if result.metadata and self.config.template != EPUBTemplate.SIMPLE:
            nav_points.append("""        <li><a href="front.xhtml">扉页</a></li>""")

        # Volume and chapter navigation
        for volume in novel.volumes:
            if len(novel.volumes) > 1:
                nav_points.append(f"""        <li><a href="chapter_{volume.chapters[0].number:03d}.xhtml">{html.escape(volume.title)}</a>""")
                nav_points.append("            <ol>")

            for chapter in volume.chapters:
                nav_points.append(f"""            <li><a href="chapter_{chapter.number:03d}.xhtml">{html.escape(chapter.title)}</a></li>""")

            if len(novel.volumes) > 1:
                nav_points.append("            </ol>")
                nav_points.append("        </li>")

        # Add back matter link if present
        if result.metadata and self.config.template == EPUBTemplate.DETAILED:
            nav_points.append("""        <li><a href="back.xhtml">附录</a></li>""")

        nav_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>目录</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>目录</h1>
        <ol>
{'\n'.join(nav_points)}
        </ol>
    </nav>
</body>
</html>"""

        epub.writestr("OEBPS/nav.xhtml", nav_content)

    def _write_ncx(self, epub: zipfile.ZipFile, novel: Novel, result: EPUBExportResult) -> None:
        """Write NCX file for EPUB 2.0 compatibility."""
        nav_points = []
        play_order = 1

        # Add front matter to play order if present
        if result.metadata and self.config.template != EPUBTemplate.SIMPLE:
            nav_points.append(f"""        <navPoint id="navpoint-front" playOrder="{play_order}">
            <navLabel><text>扉页</text></navLabel>
            <content src="front.xhtml"/>
        </navPoint>""")
            play_order += 1

        # Volume and chapter navigation
        for volume in novel.volumes:
            for chapter in volume.chapters:
                title = chapter.title
                if chapter.is_prologue:
                    title = f"序章：{title.replace('序章：', '')}"
                elif chapter.is_epilogue:
                    title = f"尾声：{title.replace('尾声：', '')}"

                nav_points.append(f"""        <navPoint id="navpoint-{chapter.number}" playOrder="{play_order}">
            <navLabel><text>{html.escape(title)}</text></navLabel>
            <content src="chapter_{chapter.number:03d}.xhtml"/>
        </navPoint>""")
                play_order += 1

        # Add back matter to play order if present
        if result.metadata and self.config.template == EPUBTemplate.DETAILED:
            nav_points.append(f"""        <navPoint id="navpoint-back" playOrder="{play_order}">
            <navLabel><text>附录</text></navLabel>
            <content src="back.xhtml"/>
        </navPoint>""")

        nav_points_str = "\n".join(nav_points)

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{novel.id}"/>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{html.escape(novel.title)}</text></docTitle>
    <navMap>
{nav_points_str}
    </navMap>
</ncx>"""

        epub.writestr("OEBPS/toc.ncx", toc_ncx)

    def _write_css(self, epub: zipfile.ZipFile) -> None:
        """Write CSS stylesheet."""
        css = self._assemble_css()
        epub.writestr("OEBPS/styles.css", css)

    def _write_front_matter(self, epub: zipfile.ZipFile, metadata: EPUBMetadata) -> None:
        """Write front matter (title page)."""
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{html.escape(metadata.title)}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="front-matter">
        <h1>{html.escape(metadata.title)}</h1>
        <h2>{html.escape(metadata.subtitle)}</h2>
        <p class="author">{html.escape(metadata.author)}</p>
        <div class="meta">
            <p>类型：{html.escape(metadata.genre)}</p>
            <p>总字数：{metadata.total_words:,} 字</p>
            <p>章节数：{metadata.total_chapters} 章</p>
            <p>卷数：{metadata.total_volumes} 卷</p>
            <p>创作日期：{metadata.creation_date}</p>
        </div>
    </div>
</body>
</html>"""

        epub.writestr("OEBPS/front.xhtml", content)

    def _write_chapters(self, epub: zipfile.ZipFile, novel: Novel, result: EPUBExportResult) -> None:
        """Write chapter content files."""
        for volume in novel.volumes:
            for chapter in volume.chapters:
                chapter_xhtml = self._render_chapter(chapter, volume, result)
                epub.writestr(f"OEBPS/chapter_{chapter.number:03d}.xhtml", chapter_xhtml)

    def _render_chapter(self, chapter: Chapter, volume: Volume, result: EPUBExportResult) -> str:
        """Render a single chapter as XHTML."""
        # Build chapter title
        if chapter.is_prologue:
            title_display = f"序章：{chapter.title.replace('序章：', '')}"
            title_class = "chapter-title prologue"
        elif chapter.is_epilogue:
            title_display = f"尾声：{chapter.title.replace('尾声：', '')}"
            title_class = "chapter-title epilogue"
        else:
            title_display = chapter.title.replace(f"第{chapter.number}章 ", "")
            title_class = "chapter-title"

        # Chapter title section
        title_section = f'<h1 class="{title_class}">{html.escape(title_display)}</h1>'

        # Chapter summary
        summary_section = ""
        if self.config.include_chapter_summaries and chapter.summary and self.config.template != EPUBTemplate.SIMPLE:
            summary_section = f'<p class="chapter-summary">{html.escape(chapter.summary)}</p>'

        # Word count
        meta_section = ""
        if self.config.include_word_counts and self.config.template != EPUBTemplate.SIMPLE:
            meta_section = f'<p class="chapter-meta">{chapter.word_count:,} 字</p>'

        # Chapter content
        if self.config.include_scene_content and chapter.scenes:
            content_html = self._render_scene_content(chapter)
        else:
            content_html = self._render_paragraph_content(chapter.content)

        chapter_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{html.escape(chapter.title)}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    {title_section}
    {summary_section}
    {meta_section}
    <div class="chapter-content">
        {content_html}
    </div>
</body>
</html>"""

        return chapter_xhtml

    def _render_paragraph_content(self, content: str) -> str:
        """Render plain content as HTML paragraphs."""
        if not content:
            return ""

        paragraphs = content.split("\n\n")
        html_parts = []

        for i, p in enumerate(paragraphs):
            p = p.strip()
            if not p:
                continue

            # First paragraph doesn't need indent
            if i == 0 and not self.config.indent_first_line:
                html_parts.append(f'<p class="first">{html.escape(p)}</p>')
            elif self.config.indent_first_line:
                html_parts.append(f'<p>{html.escape(p)}</p>')
            else:
                html_parts.append(f'<p>{html.escape(p)}</p>')

        return "\n".join(html_parts)

    def _render_scene_content(self, chapter: Chapter) -> str:
        """Render content with scene separators."""
        parts = []

        for i, scene in enumerate(chapter.scenes):
            # Scene separator
            if self.config.scene_separators and i > 0:
                parts.append('<p class="scene-break">◆</p>')

            # Scene header
            scene_header = []
            if scene.location:
                scene_header.append(html.escape(scene.location))
            if scene.time_period:
                scene_header.append(html.escape(scene.time_period))
            if scene.mood:
                scene_header.append(html.escape(scene.mood))

            if scene_header:
                parts.append(f'<p class="scene-header">{" · ".join(scene_header)}</p>')

            # Scene content
            scene_html = self._render_paragraph_content(scene.content)
            parts.append(scene_html)

        return "\n".join(parts)

    def _write_back_matter(self, epub: zipfile.ZipFile, novel: Novel, metadata: EPUBMetadata) -> None:
        """Write back matter (appendix with word count statistics)."""
        # Build chapter word count table
        table_rows = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                table_rows.append(
                    f"""            <tr>
                <td>第{chapter.number}章</td>
                <td>{html.escape(chapter.title)}</td>
                <td style="text-align: right;">{chapter.word_count:,}</td>
            </tr>"""
                )

        table_content = "\n".join(table_rows)

        back_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>附录</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="back-matter">
        <h2>章节字数统计</h2>
        <p>总字数：{metadata.total_words:,} 字</p>
        <table class="word-count-table">
            <thead>
                <tr>
                    <th>章节</th>
                    <th>标题</th>
                    <th style="text-align: right;">字数</th>
                </tr>
            </thead>
            <tbody>
{table_content}
            </tbody>
        </table>
    </div>
</body>
</html>"""

        epub.writestr("OEBPS/back.xhtml", back_content)

    def export_chapters_separate(
        self,
        novel: Novel,
        output_dir: str | Path,
        filename_pattern: str = "{volume:03d}_{chapter:03d}_{title}.xhtml"
    ) -> list[Path]:
        """Export each chapter as a separate XHTML file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write chapter files.
            filename_pattern: Pattern for filenames with {volume}, {chapter}, {title} placeholders.

        Returns:
            List of created file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                # Render chapter
                content = self._render_chapter(chapter, volume, EPUBExportResult(config=self.config))

                # Format filename
                title_clean = chapter.title.replace(" ", "_").replace("/", "-")
                filename = filename_pattern.format(
                    volume=volume.number,
                    chapter=chapter.number,
                    title=title_clean
                )
                path = output_dir / filename
                path.write_text(content, encoding="utf-8")
                paths.append(path)

        return paths

    def export_volumes_separate(
        self,
        novel: Novel,
        output_dir: str | Path,
        filename_pattern: str = "{series_title}_第{book_number}册_{book_title}.epub"
    ) -> list[Path]:
        """Export each volume as a separate EPUB book file.

        Args:
            novel: The novel to export.
            output_dir: Directory to write EPUB files.
            filename_pattern: Pattern for filenames with {series_title}, {book_number}, {book_title} placeholders.

        Returns:
            List of created EPUB file paths.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = []

        for book_num, volume in enumerate(novel.volumes, start=1):
            # Format filename
            book_title = volume.title.replace(" ", "_").replace("/", "-")
            series_title = novel.title.replace(" ", "_").replace("/", "-")
            filename = filename_pattern.format(
                series_title=series_title,
                book_number=book_num,
                book_title=book_title
            )
            path = output_dir / filename

            # Export single volume as EPUB
            self._export_single_volume_epub(novel, volume, book_num, path)
            paths.append(path)

        return paths

    def _export_single_volume_epub(
        self,
        novel: Novel,
        volume: Volume,
        book_number: int,
        output_path: Path
    ) -> None:
        """Export a single volume as a complete EPUB file.

        Args:
            novel: The original novel.
            volume: The volume to export.
            book_number: Book number in series (1-indexed).
            output_path: Path for the output EPUB file.
        """
        import zipfile
        import uuid

        path = Path(output_path)
        total_words = sum(c.word_count for c in volume.chapters)

        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as epub:
            self._write_mimetype(epub)
            self._write_container(epub)

            # Create book-specific metadata
            metadata = EPUBMetadata(
                title=novel.title,
                subtitle=f"第{book_number}册：{volume.title}",
                author=getattr(novel, 'author', 'CHAI'),
                language="zh-CN",
                publisher="CHAI - AI Novel Writer",
                publish_date=datetime.now().strftime("%Y-%m-%d"),
                genre=novel.genre,
                description=f"{novel.title} 第{book_number}册：{volume.title}",
                rights="© CHAI",
                total_words=total_words,
                total_chapters=len(volume.chapters),
                total_volumes=1,
                creation_date=datetime.now().strftime("%Y-%m-%d"),
            )

            # Create volume-specific result
            result = EPUBExportResult(config=self.config)
            result.metadata = metadata
            result.word_count = total_words

            # Create volume chapter refs
            chapters = []
            for chapter in volume.chapters:
                chapters.append(EPUBChapterRef(
                    chapter_id=f"ch_{chapter.number:03d}",
                    chapter_number=chapter.number,
                    chapter_title=chapter.title,
                    is_prologue=chapter.is_prologue,
                    is_epilogue=chapter.is_epilogue,
                    file_path=f"chapter_{chapter.number:03d}.xhtml",
                ))

            result.volumes = [EPUBVolumeRef(
                volume_id=f"vol_{volume.number:03d}",
                volume_number=volume.number,
                volume_title=volume.title,
                description=volume.description or "",
                chapters=chapters,
            )]

            # Write content.opf
            self._write_volume_content_opf(epub, novel, volume, metadata, result, book_number)

            # Write navigation document
            if self.config.include_table_of_contents:
                self._write_volume_navigation(epub, volume, result, book_number)

            # Write NCX
            self._write_volume_ncx(epub, volume, metadata, result, book_number)

            # Write CSS
            self._write_css(epub)

            # Write front matter
            if self.config.template != EPUBTemplate.SIMPLE:
                self._write_volume_front_matter(epub, novel, volume, metadata, book_number)

            # Write chapters
            for chapter in volume.chapters:
                chapter_xhtml = self._render_chapter_for_volume(chapter, volume, result)
                epub.writestr(f"OEBPS/chapter_{chapter.number:03d}.xhtml", chapter_xhtml)

            # Write back matter
            if self.config.template == EPUBTemplate.DETAILED:
                self._write_volume_back_matter(epub, volume, metadata)

    def _write_volume_content_opf(
        self,
        epub: zipfile.ZipFile,
        novel: Novel,
        volume: Volume,
        metadata: EPUBMetadata,
        result: EPUBExportResult,
        book_number: int
    ) -> None:
        """Write content.opf for a single volume EPUB."""
        uuid_str = f"urn:uuid:{novel.id}-vol{volume.number}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Build manifest
        manifest_items = [
            EPUBManifestItem(id="ncx", href="toc.ncx", media_type="application/x-dtbncx+xml"),
            EPUBManifestItem(id="nav", href="nav.xhtml", media_type="application/xhtml+xml"),
            EPUBManifestItem(id="css", href="styles.css", media_type="text/css"),
        ]

        if self.config.template != EPUBTemplate.SIMPLE:
            manifest_items.append(EPUBManifestItem(id="front", href="front.xhtml", media_type="application/xhtml+xml"))

        for chapter in volume.chapters:
            manifest_items.append(EPUBManifestItem(
                id=f"ch_{chapter.number:03d}",
                href=f"chapter_{chapter.number:03d}.xhtml",
                media_type="application/xhtml+xml",
            ))

        # Build spine
        spine_items = [EPUBSpineItem(idref="nav", linear=False)]

        if self.config.template != EPUBTemplate.SIMPLE:
            spine_items.insert(0, EPUBSpineItem(idref="front", linear=True))

        for chapter in volume.chapters:
            spine_items.append(EPUBSpineItem(idref=f"ch_{chapter.number:03d}", linear=True))

        # Render manifest
        manifest_xml = []
        for item in manifest_items:
            manifest_xml.append(f'        <item id="{item.id}" href="{item.href}" media-type="{item.media_type}"/>')

        # Render spine
        spine_xml = []
        for item in spine_items:
            linear = "yes" if item.linear else "no"
            spine_xml.append(f'        <itemref idref="{item.idref}" linear="{linear}"/>')

        metadata_xml = f"""    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{html.escape(metadata.title)}</dc:title>
        <dc:language>{metadata.language}</dc:language>
        <dc:identifier id="BookId">{uuid_str}</dc:identifier>
        <dc:creator>CHAI - AI Novel Writer</dc:creator>
        <dc:publisher>{html.escape(metadata.publisher)}</dc:publisher>
        <dc:subject>{html.escape(metadata.genre)}</dc:subject>
        <dc:date>{metadata.publish_date}</dc:date>
        <dc:rights>{html.escape(metadata.rights)}</dc:rights>
    </metadata>"""

        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
{metadata_xml}
    <manifest>
{"\n".join(manifest_xml)}
    </manifest>
    <spine toc="ncx">
{"\n".join(spine_xml)}
    </spine>
</package>"""

        epub.writestr("OEBPS/content.opf", content_opf)

    def _write_volume_navigation(
        self,
        epub: zipfile.ZipFile,
        volume: Volume,
        result: EPUBExportResult,
        book_number: int
    ) -> None:
        """Write EPUB 3.0 navigation document for a single volume."""
        nav_points = []

        if self.config.template != EPUBTemplate.SIMPLE:
            nav_points.append("""        <li><a href="front.xhtml">扉页</a></li>""")

        for chapter in volume.chapters:
            nav_points.append(f"""        <li><a href="chapter_{chapter.number:03d}.xhtml">{html.escape(chapter.title)}</a></li>""")

        nav_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>目录</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>目录</h1>
        <ol>
{'\n'.join(nav_points)}
        </ol>
    </nav>
</body>
</html>"""

        epub.writestr("OEBPS/nav.xhtml", nav_content)

    def _write_volume_ncx(
        self,
        epub: zipfile.ZipFile,
        volume: Volume,
        metadata: EPUBMetadata,
        result: EPUBExportResult,
        book_number: int
    ) -> None:
        """Write NCX file for a single volume EPUB."""
        nav_points = []
        play_order = 1

        if self.config.template != EPUBTemplate.SIMPLE:
            nav_points.append(f"""        <navPoint id="navpoint-front" playOrder="{play_order}">
            <navLabel><text>扉页</text></navLabel>
            <content src="front.xhtml"/>
        </navPoint>""")
            play_order += 1

        for chapter in volume.chapters:
            title = chapter.title
            if chapter.is_prologue:
                title = f"序章：{title.replace('序章：', '')}"
            elif chapter.is_epilogue:
                title = f"尾声：{title.replace('尾声：', '')}"

            nav_points.append(f"""        <navPoint id="navpoint-{chapter.number}" playOrder="{play_order}">
            <navLabel><text>{html.escape(title)}</text></navLabel>
            <content src="chapter_{chapter.number:03d}.xhtml"/>
        </navPoint>""")
            play_order += 1

        nav_points_str = "\n".join(nav_points)

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{metadata.title}"/>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{html.escape(metadata.title)} - {html.escape(metadata.subtitle)}</text></docTitle>
    <navMap>
{nav_points_str}
    </navMap>
</ncx>"""

        epub.writestr("OEBPS/toc.ncx", toc_ncx)

    def _write_volume_front_matter(
        self,
        epub: zipfile.ZipFile,
        novel: Novel,
        volume: Volume,
        metadata: EPUBMetadata,
        book_number: int
    ) -> None:
        """Write front matter for a single volume EPUB."""
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{html.escape(metadata.title)}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="front-matter">
        <h1>{html.escape(novel.title)}</h1>
        <h2>{html.escape(metadata.subtitle)}</h2>
        <p class="author">{html.escape(metadata.author)}</p>
        <div class="meta">
            <p>类型：{html.escape(metadata.genre)}</p>
            <p>本册字数：{metadata.total_words:,} 字</p>
            <p>本册章节：{metadata.total_chapters} 章</p>
            <p>创作日期：{metadata.creation_date}</p>
        </div>
    </div>
</body>
</html>"""

        epub.writestr("OEBPS/front.xhtml", content)

    def _render_chapter_for_volume(
        self,
        chapter: Chapter,
        volume: Volume,
        result: EPUBExportResult
    ) -> str:
        """Render a single chapter as XHTML for volume-specific EPUB."""
        # Build chapter title
        if chapter.is_prologue:
            title_display = f"序章：{chapter.title.replace('序章：', '')}"
            title_class = "chapter-title prologue"
        elif chapter.is_epilogue:
            title_display = f"尾声：{chapter.title.replace('尾声：', '')}"
            title_class = "chapter-title epilogue"
        else:
            title_display = chapter.title.replace(f"第{chapter.number}章 ", "")
            title_class = "chapter-title"

        title_section = f'<h1 class="{title_class}">{html.escape(title_display)}</h1>'

        summary_section = ""
        if self.config.include_chapter_summaries and chapter.summary and self.config.template != EPUBTemplate.SIMPLE:
            summary_section = f'<p class="chapter-summary">{html.escape(chapter.summary)}</p>'

        meta_section = ""
        if self.config.include_word_counts and self.config.template != EPUBTemplate.SIMPLE:
            meta_section = f'<p class="chapter-meta">{chapter.word_count:,} 字</p>'

        if self.config.include_scene_content and chapter.scenes:
            content_html = self._render_scene_content(chapter)
        else:
            content_html = self._render_paragraph_content(chapter.content)

        chapter_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{html.escape(chapter.title)}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    {title_section}
    {summary_section}
    {meta_section}
    <div class="chapter-content">
        {content_html}
    </div>
</body>
</html>"""

        return chapter_xhtml

    def _write_volume_back_matter(
        self,
        epub: zipfile.ZipFile,
        volume: Volume,
        metadata: EPUBMetadata
    ) -> None:
        """Write back matter for a single volume EPUB."""
        table_rows = []
        for chapter in volume.chapters:
            table_rows.append(
                f"""            <tr>
                <td>第{chapter.number}章</td>
                <td>{html.escape(chapter.title)}</td>
                <td style="text-align: right;">{chapter.word_count:,}</td>
            </tr>"""
            )

        table_content = "\n".join(table_rows)

        back_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>附录</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="back-matter">
        <h2>章节字数统计</h2>
        <p>本册总字数：{metadata.total_words:,} 字</p>
        <table class="word-count-table">
            <thead>
                <tr>
                    <th>章节</th>
                    <th>标题</th>
                    <th style="text-align: right;">字数</th>
                </tr>
            </thead>
            <tbody>
{table_content}
            </tbody>
        </table>
    </div>
</body>
</html>"""

        epub.writestr("OEBPS/back.xhtml", back_content)

    def get_manuscript_summary(self, novel: Novel) -> dict:
        """Get a summary of the EPUB that would be generated.

        Args:
            novel: The novel to summarize.

        Returns:
            Dictionary with EPUB statistics.
        """
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        total_chapters = sum(len(v.chapters) for v in novel.volumes)
        total_scenes = sum(len(c.scenes) for v in novel.volumes for c in v.chapters)

        return {
            "title": novel.title,
            "genre": novel.genre,
            "total_volumes": len(novel.volumes),
            "total_chapters": total_chapters,
            "total_scenes": total_scenes,
            "total_words": total_words,
            "average_chapter_words": total_words // total_chapters if total_chapters else 0,
            "has_prologue": novel.has_prologue,
            "has_epilogue": novel.has_epilogue,
            "epub_version": self.config.epub_version,
            "template": self.config.template.value,
        }
