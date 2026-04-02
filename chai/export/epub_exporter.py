"""EPUB export functionality."""

import zipfile
from pathlib import Path
from datetime import datetime
from chai.models import Novel, Volume, Chapter
from chai.export.markdown_exporter import MarkdownExporter


class EPUBExporter:
    """Export novel to EPUB format."""

    def __init__(self):
        """Initialize EPUB exporter."""
        self.markdown_exporter = MarkdownExporter()

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export novel to an EPUB file."""
        path = Path(output_path)

        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as epub:
            self._write_mimetype(epub)
            self._write_container(epub)
            self._write_content_opf(epub, novel)
            self._write_toc(epub, novel)
            self._write_chapters(epub, novel)

        return path

    def _write_mimetype(self, epub: zipfile.ZipFile) -> None:
        """Write mimetype file."""
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

    def _write_content_opf(self, epub: zipfile.ZipFile, novel: Novel) -> None:
        """Write content.opf file."""
        total_words = sum(c.word_count for v in novel.volumes for c in v.chapters)
        uuid = f"urn:uuid:{novel.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        manifest_items = []
        spine_items = []

        for volume in novel.volumes:
            for chapter in volume.chapters:
                chapter_file = f"chapter_{chapter.number:03d}.xhtml"
                manifest_items.append(
                    f'        <item id="chapter_{chapter.number}" '
                    f'href="{chapter_file}" media-type="application/xhtml+xml"/>'
                )
                spine_items.append(f'        <itemref idref="chapter_{chapter.number}"/>')

        manifest = "\n".join(manifest_items)
        spine = "\n".join(spine_items)

        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{novel.title}</dc:title>
        <dc:language>zh-CN</dc:language>
        <dc:identifier id="BookId">{uuid}</dc:identifier>
        <dc:creator>CHAI - AI Novel Writer</dc:creator>
        <dc:subject>{novel.genre}</dc:subject>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="css" href="styles.css" media-type="text/css"/>
{manifest}
    </manifest>
    <spine toc="ncx">
{spine}
    </spine>
</package>"""

        epub.writestr("OEBPS/content.opf", content_opf)

    def _write_toc(self, epub: zipfile.ZipFile, novel: Novel) -> None:
        """Write table of contents."""
        nav_points = []
        for volume in novel.volumes:
            for chapter in volume.chapters:
                nav_point = f"""        <navPoint id="navpoint-{chapter.number}" playOrder="{chapter.number}">
            <navLabel><text>{chapter.title}</text></navLabel>
            <content src="chapter_{chapter.number:03d}.xhtml"/>
        </navPoint>"""
                nav_points.append(nav_point)

        nav_points_str = "\n".join(nav_points)

        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{novel.id}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>{novel.title}</text></docTitle>
    <navMap>
{nav_points_str}
    </navMap>
</ncx>"""

        epub.writestr("OEBPS/toc.ncx", toc_ncx)

    def _write_chapters(self, epub: zipfile.ZipFile, novel: Novel) -> None:
        """Write chapter content files."""
        css = """body {
    font-family: "SimSun", serif;
    margin: 5%;
    line-height: 1.8;
}
h1 {
    text-align: center;
    margin-top: 2em;
}
h2 {
    text-align: center;
}
p {
    text-indent: 2em;
}"""

        epub.writestr("OEBPS/styles.css", css)

        for volume in novel.volumes:
            for chapter in volume.chapters:
                chapter_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{chapter.title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <h1>{chapter.title}</h1>
    <div class="content">
        {self._content_to_html(chapter.content)}
    </div>
</body>
</html>"""

                epub.writestr(f"OEBPS/chapter_{chapter.number:03d}.xhtml", chapter_xhtml)

    def _content_to_html(self, content: str) -> str:
        """Convert plain text content to HTML paragraphs."""
        paragraphs = content.split("\n\n")
        html_parts = []
        for p in paragraphs:
            p = p.strip()
            if p:
                html_parts.append(f"<p>{p}</p>")
        return "\n".join(html_parts)
