import os
import time
import pdfplumber
import nltk

def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as file:
        text = ""
        for page in file.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text

def sent_chunk(text: str) -> str:
    nltk.download("punkt")
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return ""
    # Simple summary: return the first sentence
    return sentences[0]
