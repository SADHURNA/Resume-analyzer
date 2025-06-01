# resume_parser.py
import pdfplumber
import docx2txt
from docx import Document
from utils.parser import extract_text_from_pdf, extract_text_from_docx


def extract_text_from_resume(filepath):
    if filepath.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif filepath.endswith('.docx'):
        return extract_text_from_docx(filepath)
    return ''

def extract_text_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text.strip()

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path).strip()
