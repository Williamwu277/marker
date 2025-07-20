import xml.etree.ElementTree as ET
import re
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os

# ── Color Scheme ───────────────────────────────────────────────────────────────
COLOR_FOREGROUND = colors.HexColor('#764b2d')
COLOR_PRIMARY    = colors.HexColor('#de8a4e')
COLOR_NOTEBOOK   = colors.HexColor('#efe5dc')
COLOR_ACCENT     = colors.HexColor('#000000')
COLOR_PENCIL     = colors.HexColor('#a3683e')
COLOR_PAPER      = colors.HexColor('#ffffff')

def xml_to_para(text: str) -> str:
    """Convert <emphasis> tags into ReportLab inline markup."""
    if not text:
        return ""
    text = re.sub(r'<emphasis\s+type="italic">(.*?)</emphasis>', r'<i>\1</i>', text, flags=re.DOTALL)
    text = re.sub(r'<emphasis\s+type="underline">(.*?)</emphasis>', r'<u>\1</u>', text, flags=re.DOTALL)
    text = re.sub(r'<emphasis\s+type="bold">(.*?)</emphasis>', r'<b>\1</b>', text, flags=re.DOTALL)
    return text

def get_inner(el):
    """Extract inner XML/text including child tags and tails."""
    if el is None:
        return ''
    parts = [el.text or '']
    for child in el:
        parts.append(ET.tostring(child, encoding='unicode'))
        parts.append(child.tail or '')
    return ''.join(parts)

def draw_page(canvas, doc):
    width, height = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(COLOR_PAPER)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    # Header band
    canvas.setFillColor(COLOR_PRIMARY)
    canvas.rect(0, height - 0.5*inch, width, 0.5*inch, fill=1, stroke=0)
    canvas.setFillColor(COLOR_PAPER)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(inch, height - 0.35*inch, "Marker • Notes")
    # Footer band
    canvas.setFillColor(COLOR_NOTEBOOK)
    canvas.rect(0, 0, width, 0.3*inch, fill=1, stroke=0)
    canvas.setFillColor(COLOR_FOREGROUND)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawCentredString(width/2, 0.1*inch, f"Generated on {datetime.utcnow():%Y-%m-%d}")
    canvas.restoreState()

def make_section_header(title, styles, content_width):
    """Full-width header block, shaded background."""
    tbl = Table([[Paragraph(f'<b>{title}</b>', styles['CustomHeading2'])]],
                colWidths=[content_width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',      (0, 0), (-1, -1), COLOR_NOTEBOOK),
        ('LEFTPADDING',     (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',    (0, 0), (-1, -1), 6),
        ('TOPPADDING',      (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',   (0, 0), (-1, -1), 6),
    ]))
    return tbl

def make_section_block(desc, examples, styles, content_width):
    """
    Single box around description and bullet points.
    """
    # build rows: description then each bullet
    data = [[Paragraph(desc, styles['CustomBody'])]]
    for ex in examples:
        data.append([Paragraph(f'<font color="{COLOR_PENCIL}">•</font> {ex}', styles['CustomBody'])])
    tbl = Table(data, colWidths=[content_width * 0.95], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BOX',            (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ('LEFTPADDING',    (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 6),
        ('TOPPADDING',     (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 4),
        # no inner lines
    ]))
    return tbl

def generate_notes_from_xml(xml_string: str, output_filename: str = "generated_notes.pdf") -> str:
    """Generate PDF with boxed content below headers."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output path
    output_path = os.path.join(output_dir, output_filename)

    root = ET.fromstring(xml_string)
    objective = xml_to_para(get_inner(root.find('Objective')).strip())
    overview  = xml_to_para(get_inner(root.find('Overview')).strip())
    key_concepts = [
        (xml_to_para(get_inner(c.find('Name')).strip()),
         xml_to_para(get_inner(c.find('Definition')).strip()))
        for c in root.findall('KeyConcepts/Concept')
    ]
    sections = [
        (
            xml_to_para(get_inner(sec.find('Title')).strip()),
            xml_to_para(get_inner(sec.find('Description')).strip()),
            [xml_to_para(get_inner(ex).strip()) for ex in sec.findall('Examples/Example')]
        )
        for sec in root.findall('DetailedNotes/Section')
    ]
    summary = xml_to_para(get_inner(root.find('Summary')).strip())

    # Document setup
    doc = BaseDocTemplate(output_path, pagesize=letter,
                          rightMargin=inch, leftMargin=inch,
                          topMargin=inch, bottomMargin=inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='main')
    doc.addPageTemplates([PageTemplate(id='pt', frames=[frame], onPage=draw_page)])

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                              fontName='Helvetica-Bold', fontSize=20,
                              textColor=COLOR_PRIMARY, spaceAfter=18))
    styles.add(ParagraphStyle('CustomHeading2', parent=styles['Heading2'],
                              fontName='Helvetica-Bold', fontSize=14,
                              textColor=COLOR_FOREGROUND,
                              spaceBefore=0, spaceAfter=0))
    styles.add(ParagraphStyle('CustomBody', parent=styles['BodyText'],
                              fontName='Helvetica', fontSize=12,
                              leading=16, textColor=COLOR_FOREGROUND,
                              spaceAfter=8))

    # Build story
    story = []
    story.append(Paragraph("Lecture Notes Overview", styles['CustomTitle']))
    story.append(Paragraph(f"<b>Objective:</b> {objective}", styles['CustomBody']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Overview:</b>", styles['CustomHeading2']))
    story.append(Paragraph(overview, styles['CustomBody']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Key Concepts:</b>", styles['CustomHeading2']))
    for name, definition in key_concepts:
        story.append(Paragraph(f'<font color="{COLOR_PENCIL}">•</font> {name}: {definition}', styles['CustomBody']))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Detailed Notes:</b>", styles['CustomHeading2']))
    for title, desc, examples in sections:
        block = KeepTogether([
            make_section_header(title, styles, doc.width),
            make_section_block(desc, examples, styles, doc.width),
            Spacer(1, 12)
        ])
        story.append(block)

    # Summary
    story.append(KeepTogether([
        Paragraph("<b>Summary:</b>", styles['CustomHeading2']),
        Paragraph(summary, styles['CustomBody'])
    ]))

    doc.build(story)
    return output_path