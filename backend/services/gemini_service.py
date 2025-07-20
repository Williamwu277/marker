# services/gemini_service.py
from dotenv import load_dotenv

import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from utils.gemini_client import GeminiClient
from services.notes_generation import generate_notes_from_xml
from services.worksheet_generation import generate_worksheet_from_xml


class GeminiService:
    """
    Simple wraxpper around GeminiClient for generating notes,
    practice questions, and written‐work analysis.
    """

    def __init__(self):
        self.client = GeminiClient()

    def generate_notes(self, context: str):
        xml = self.client.generate_notes( context)
        
        # Generate notes with validation retry
        generation_success = False
        generation_attempts = 0
        max_attempts = 3
        
        while not generation_success and generation_attempts < max_attempts:
            try:
                output = generate_notes_from_xml(xml, output_filename="notes.pdf")
                generation_success = True
                print("Wrote notes to", output)
            except Exception as e:
                print(f"Error generating notes: {e}")
                xml = self.client.validate_xml(xml, "notes")
                generation_attempts += 1
                if generation_attempts == max_attempts:
                    raise Exception("Failed to generate notes after maximum attempts")

    def generate_practice_questions(self, context: str):
        xml = self.client.generate_practice_questions(context)
        
        # Generate worksheet without answers
        generation_success = False
        generation_attempts = 0
        max_attempts = 3
        
        while not generation_success and generation_attempts < max_attempts:
            try:
                worksheet = generate_worksheet_from_xml(xml, "worksheet.pdf", include_answers=False)
                generation_success = True
                print("Wrote worksheet to", worksheet)
            except Exception as e:
                print(f"Error generating worksheet: {e}")
                xml = self.client.validate_xml(xml, "questions")
                generation_attempts += 1
                if generation_attempts == max_attempts:
                    raise Exception("Failed to generate worksheet after maximum attempts")
        
        # Generate answer key with validation retry
        generation_success = False
        generation_attempts = 0
        
        while not generation_success and generation_attempts < max_attempts:
            try:
                answer_key = generate_worksheet_from_xml(xml, "answer_key.pdf", include_answers=True)
                generation_success = True
                print("Wrote answer key to", answer_key)
            except Exception as e:
                print(f"Error generating answer key: {e}")
                xml = self.client.validate_xml(xml, "questions")
                generation_attempts += 1
                if generation_attempts == max_attempts:
                    raise Exception("Failed to generate answer key after maximum attempts")