"""PDF export functionality using reportlab."""

from pathlib import Path
from chai.models import Novel, Volume, Chapter
from chai.export.markdown_exporter import MarkdownExporter


class PDFExporter:
    """Export novel to PDF format."""

    def __init__(self):
        """Initialize PDF exporter."""
        self.markdown_exporter = MarkdownExporter()

    def export_to_file(self, novel: Novel, output_path: str | Path) -> Path:
        """Export novel to a PDF file."""
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install it with: pip install reportlab"
            )

        path = Path(output_path)

        try:
            pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/STKaiti.ttc'))
            font = 'SimSun'
        except:
            font = 'Helvetica'

        doc = SimpleDocTemplate(
            str(path),
            pagesize=A5,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        styles = {
            'title': ParagraphStyle(
                'Title',
                fontName=font,
                fontSize=24,
                alignment=1,
                spaceAfter=30,
            ),
            'chapter': ParagraphStyle(
                'Chapter',
                fontName=font,
                fontSize=16,
                alignment=1,
                spaceBefore=20,
                spaceAfter=20,
            ),
            'body': ParagraphStyle(
                'Body',
                fontName=font,
                fontSize=11,
                leading=18,
                firstLineIndent=22,
                spaceAfter=10,
            ),
        }

        story = []

        story.append(Paragraph(novel.title, styles['title']))
        story.append(Spacer(1, 20))

        for volume in novel.volumes:
            for chapter in volume.chapters:
                story.append(Paragraph(chapter.title, styles['chapter']))

                paragraphs = chapter.content.split("\n\n")
                for p in paragraphs:
                    p = p.strip()
                    if p:
                        story.append(Paragraph(p, styles['body']))

                story.append(Spacer(1, 15))

            story.append(PageBreak())

        doc.build(story)
        return path
