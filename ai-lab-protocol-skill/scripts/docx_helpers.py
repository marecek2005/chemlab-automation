"""Reusable paragraph/table styling and native editable Word equations."""
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def new_document():
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin = section.right_margin = Cm(2)
    for name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Caption']:
        style = document.styles[name]
        style.font.name = 'Times New Roman'
        style.font.color.rgb = RGBColor(0, 0, 0)
    document.styles['Normal'].font.size = Pt(11)
    document.styles['Normal'].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    document.styles['Normal'].paragraph_format.space_after = Pt(5)
    document.styles['Normal'].paragraph_format.line_spacing = 1.08
    document.styles['Title'].font.size = Pt(17)
    document.styles['Heading 1'].font.size = Pt(12)
    return document

def math_run(text, upright=False):
    element = OxmlElement('m:r')
    properties = OxmlElement('m:rPr')
    style = OxmlElement('m:sty')
    style.set(qn('m:val'), 'p' if upright else 'i')
    properties.append(style)
    element.append(properties)
    child = OxmlElement('m:t')
    child.text = str(text)
    element.append(child)
    return element

def group(tag, children):
    element = OxmlElement(tag)
    for child in children:
        element.append(child)
    return element

def fraction(numerator, denominator):
    return group('m:f', [group('m:num', numerator), group('m:den', denominator)])

def subscript(base, index, index_upright=True):
    return group('m:sSub', [group('m:e', [math_run(base)]), group('m:sub', [math_run(index, upright=index_upright)])])

def parentheses(expression):
    props = OxmlElement('m:dPr')
    for tag, value in [('m:begChr', '('), ('m:endChr', ')')]:
        child = OxmlElement(tag)
        child.set(qn('m:val'), value)
        props.append(child)
    return group('m:d', [props, group('m:e', expression)])

def squared(expression):
    return group('m:sSup', [group('m:e', [parentheses(expression)]), group('m:sup', [math_run('2', upright=True)])])

def equation(document, children, number):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph._p.append(group('m:oMath', list(children) + [math_run(f'    ({number})', upright=True)]))
    return paragraph

def style_table(table):
    properties = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement('w:' + side)
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:color'), 'D9D9D9')
        borders.append(border)
    properties.append(borders)
    for i, row in enumerate(table.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(3)
                for run in paragraph.runs:
                    run.font.size = Pt(10.5)
                    run.bold = i == 0
            if i == 0:
                shade = OxmlElement('w:shd')
                shade.set(qn('w:fill'), 'EDEDED')
                cell._tc.get_or_add_tcPr().append(shade)
