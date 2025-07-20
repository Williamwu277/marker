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
    canvas.drawString(inch, height - 0.35*inch, "Marker • Practice Questions")
    # Footer band
    canvas.setFillColor(COLOR_NOTEBOOK)
    canvas.rect(0, 0, width, 0.3*inch, fill=1, stroke=0)
    canvas.setFillColor(COLOR_FOREGROUND)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawCentredString(width/2, 0.1*inch, f"Generated on {datetime.utcnow():%Y-%m-%d}")
    canvas.restoreState()

def make_question_header(number: int, difficulty: str, styles, content_width):
    """Create header for each question with difficulty indicator."""
    difficulty_colors = {
        'easy': colors.HexColor('#90EE90'),    # Light green
        'medium': colors.HexColor('#FFD700'),   # Gold
        'hard': colors.HexColor('#FFB6C1')      # Light red
    }
    
    header_text = f'Question {number} <font color="{difficulty_colors[difficulty]}">[{difficulty}]</font>'
    tbl = Table([[Paragraph(header_text, styles['CustomHeading2'])]],
                colWidths=[content_width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',      (0, 0), (-1, -1), COLOR_NOTEBOOK),
        ('LEFTPADDING',     (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',    (0, 0), (-1, -1), 6),
        ('TOPPADDING',      (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',   (0, 0), (-1, -1), 6),
    ]))
    return tbl

def make_multiple_choice_block(choices, styles, content_width):
    """Create a block for multiple choice options."""
    data = []
    for i, choice in enumerate(choices):
        letter = chr(65 + i)  # A, B, C, D...
        text = f"{letter}. {choice}"
        data.append([Paragraph(text, styles['CustomBody'])])
    
    tbl = Table(data, colWidths=[content_width * 0.95], hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BOX',            (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ('LEFTPADDING',    (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 6),
        ('TOPPADDING',     (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 4),
    ]))
    return tbl

def make_question_block(question_num: int, difficulty: str, question_text: str, 
                       choices: list, styles: dict, width: float, include_answers: bool, answer: str = None):
    """Creates a complete question block that stays together"""
    elements = []
    
    # Add question header
    elements.append(make_question_header(question_num, difficulty, styles, width))
    elements.append(Paragraph(question_text, styles['CustomBody']))
    
    # Add multiple choice or space for answer
    if choices:
        elements.append(make_multiple_choice_block(choices, styles, width))
    else:
        elements.append(Spacer(1, inch))
    
    # Add answer if requested
    if include_answers and answer:
        elements.append(Paragraph(f"<b>Answer:</b> {answer}", styles['CustomBody']))
    
    elements.append(Spacer(1, 0.25*inch))
    return KeepTogether(elements)

def generate_worksheet_from_xml(xml_string: str, output_filename: str = "worksheet.pdf", include_answers: bool = False) -> str:
    """Generate practice worksheet PDF from XML."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output path
    output_path = os.path.join(output_dir, output_filename)

    # Parse XML
    root = ET.fromstring(xml_string)
    questions = root.findall('Question')

    # Document setup
    doc = BaseDocTemplate(output_path, pagesize=letter,
                         rightMargin=inch, leftMargin=inch,
                         topMargin=inch, bottomMargin=inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='main')
    doc.addPageTemplates([PageTemplate(id='pt', frames=[frame], onPage=draw_page)])

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('CustomTitle', 
                            parent=styles['Heading1'],
                            fontName='Helvetica-Bold',
                            fontSize=20,
                            textColor=COLOR_PRIMARY,
                            spaceAfter=18))
    styles.add(ParagraphStyle('CustomHeading2',
                            parent=styles['Heading2'],
                            fontName='Helvetica-Bold',
                            fontSize=14,
                            textColor=COLOR_FOREGROUND,
                            spaceBefore=0,
                            spaceAfter=0))
    styles.add(ParagraphStyle('CustomBody',
                            parent=styles['BodyText'],
                            fontName='Helvetica',
                            fontSize=12,
                            leading=16,
                            textColor=COLOR_FOREGROUND,
                            spaceAfter=8))

    # Build story
    story = []
    story.append(Paragraph("Practice Questions", styles['CustomTitle']))
    
    for i, question in enumerate(questions, 1):
        q_type = question.get('type')
        difficulty = question.get('difficulty')
        question_text = question.find('QuestionText').text
        answer = question.find('Answer').text if include_answers else None
        
        # Get choices for multiple choice questions
        choices = None
        if q_type == "multiple_choice":
            choices = [choice.text for choice in question.findall('Choices/Choice')]
        
        # Create question block that stays together
        question_block = make_question_block(
            question_num=i,
            difficulty=difficulty,
            question_text=question_text,
            choices=choices,
            styles=styles,
            width=doc.width,
            include_answers=include_answers,
            answer=answer
        )
        
        story.append(question_block)

    doc.build(story)
    return output_path