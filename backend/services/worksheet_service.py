"""
Worksheet service for handling worksheet uploads and question extraction.
Processes PDF worksheets and extracts individual questions for semantic search.
"""

import logging
import os
import re
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename
from config.config import Config
from utils.pdf_parser import parse_pdf_file
from utils.embedding_utils import get_embeddings
from utils.faiss_index import add_to_index

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class WorksheetService:
    """Service for handling worksheet-related operations."""
    
    def __init__(self):
        """Initialize the worksheet service."""
        self.upload_folder = Config.UPLOAD_FOLDER
        Config.ensure_upload_folder()
    
    def allowed_pdf_file(self, filename: str) -> bool:
        """
        Check if the uploaded file has an allowed PDF extension.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            bool: True if file extension is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_PDF_EXTENSIONS
    
    def save_pdf_file(self, file) -> Optional[str]:
        """
        Save an uploaded PDF file to the upload folder.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Optional[str]: Path to saved file or None if failed
        """
        try:
            if file and self.allowed_pdf_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.upload_folder, filename)
                file.save(file_path)
                logger.info(f"Saved worksheet file: {file_path}")
                return file_path
            else:
                logger.error(f"Invalid PDF file: {file.filename if file else 'None'}")
                return None
        except Exception as e:
            logger.error(f"Failed to save worksheet file: {e}")
            return None
    
    def extract_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract individual questions from worksheet text.
        
        Args:
            text: Text content from the worksheet
            
        Returns:
            List[Dict[str, Any]]: List of extracted questions
        """
        questions = []
        
        # Common question patterns
        question_patterns = [
            r'(\d+\.\s*)([^?\n]+[?])',  # 1. Question?
            r'([A-Z]\.\s*)([^?\n]+[?])',  # A. Question?
            r'(Question\s+\d+[.:]\s*)([^?\n]+[?])',  # Question 1: Question?
            r'(\d+\)\s*)([^?\n]+[?])',  # 1) Question?
        ]
        
        lines = text.split('\n')
        current_question = None
        question_text = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new question
            is_new_question = False
            question_number = None
            
            for pattern in question_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    is_new_question = True
                    question_number = match.group(1).strip()
                    question_text = match.group(2).strip()
                    break
            
            if is_new_question:
                # Save previous question if exists
                if current_question and question_text.strip():
                    questions.append(current_question)
                
                # Start new question
                current_question = {
                    'number': question_number,
                    'text': question_text,
                    'full_text': line,
                    'options': [],
                    'type': 'multiple_choice' if any(opt in line for opt in ['A.', 'B.', 'C.', 'D.']) else 'text'
                }
            elif current_question:
                # Continue building current question
                current_question['full_text'] += '\n' + line
                
                # Check for multiple choice options
                option_match = re.match(r'^([A-D])[.:]\s*(.+)$', line, re.IGNORECASE)
                if option_match:
                    current_question['options'].append({
                        'letter': option_match.group(1).upper(),
                        'text': option_match.group(2).strip()
                    })
        
        # Add the last question
        if current_question and current_question['text'].strip():
            questions.append(current_question)
        
        logger.info(f"Extracted {len(questions)} questions from worksheet text")
        return questions
    
    def process_worksheet(self, pdf_path: str, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Process a PDF worksheet and extract questions.
        
        Args:
            pdf_path: Path to the PDF file
            title: Optional title for the worksheet
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            logger.info(f"Processing worksheet: {pdf_path}")
            
            # Parse PDF file
            segments = parse_pdf_file(pdf_path)
            
            if not segments:
                return {
                    'success': False,
                    'error': 'No content extracted from PDF file'
                }
            
            # Combine all text for question extraction
            full_text = '\n'.join([seg.get('text', '') for seg in segments])
            
            # Extract questions
            questions = self.extract_questions(full_text)
            
            if not questions:
                return {
                    'success': False,
                    'error': 'No questions found in worksheet'
                }
            
            # Prepare questions for embedding
            question_texts = []
            question_metadata = []
            
            for i, question in enumerate(questions):
                text = question.get('text', '').strip()
                if text:
                    question_texts.append(text)
                    question_metadata.append({
                        'type': 'worksheet_question',
                        'source': 'pdf_parser',
                        'file_path': pdf_path,
                        'question_index': i,
                        'question_number': question.get('number', ''),
                        'question_type': question.get('type', ''),
                        'title': title or os.path.basename(pdf_path),
                        'user_id': user_id,
                        'content': text[:200] + '...' if len(text) > 200 else text,
                        'options': question.get('options', []),
                        'full_text': question.get('full_text', '')
                    })
            
            # Generate embeddings for questions
            if question_texts:
                try:
                    embeddings = get_embeddings(question_texts)
                    add_to_index(embeddings, question_metadata)
                    logger.info(f"Added {len(embeddings)} worksheet question embeddings to index")
                except Exception as e:
                    logger.error(f"Failed to create embeddings for worksheet questions: {e}")
            
            # Calculate statistics
            total_chars = sum(len(text) for text in question_texts)
            total_words = sum(len(text.split()) for text in question_texts)
            question_types = list(set(q.get('type', '') for q in questions))
            
            # Prepare response
            response = {
                'success': True,
                'file_path': pdf_path,
                'title': title or os.path.basename(pdf_path),
                'questions_count': len(questions),
                'total_characters': total_chars,
                'total_words': total_words,
                'avg_chars_per_question': total_chars / len(questions) if questions else 0,
                'avg_words_per_question': total_words / len(questions) if questions else 0,
                'question_types': question_types,
                'questions': questions
            }
            
            logger.info(f"Successfully processed worksheet {pdf_path} with {len(questions)} questions")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process worksheet {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_and_process_worksheet(self, file, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Upload and process a PDF worksheet in one operation.
        
        Args:
            file: Uploaded file object
            title: Optional title for the worksheet
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            # Save the uploaded file
            pdf_path = self.save_pdf_file(file)
            
            if not pdf_path:
                return {
                    'success': False,
                    'error': 'Failed to save uploaded worksheet file'
                }
            
            # Process the worksheet
            return self.process_worksheet(pdf_path, title, user_id)
            
        except Exception as e:
            logger.error(f"Failed to upload and process worksheet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_worksheet_questions(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get all questions from a processed worksheet.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict[str, Any]: Worksheet questions
        """
        try:
            segments = parse_pdf_file(pdf_path)
            
            if not segments:
                return {
                    'success': False,
                    'error': 'No content found in PDF file'
                }
            
            # Combine all text for question extraction
            full_text = '\n'.join([seg.get('text', '') for seg in segments])
            
            # Extract questions
            questions = self.extract_questions(full_text)
            
            if questions:
                return {
                    'success': True,
                    'questions': questions,
                    'count': len(questions),
                    'file_path': pdf_path
                }
            else:
                return {
                    'success': False,
                    'error': 'No questions found in worksheet'
                }
                
        except Exception as e:
            logger.error(f"Failed to get worksheet questions from {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_question_by_index(self, pdf_path: str, question_index: int) -> Dict[str, Any]:
        """
        Get a specific question by its index.
        
        Args:
            pdf_path: Path to the PDF file
            question_index: Index of the question to retrieve
            
        Returns:
            Dict[str, Any]: Question information
        """
        try:
            questions_result = self.get_worksheet_questions(pdf_path)
            
            if not questions_result['success']:
                return questions_result
            
            questions = questions_result['questions']
            
            if 0 <= question_index < len(questions):
                return {
                    'success': True,
                    'question': questions[question_index],
                    'index': question_index,
                    'total_questions': len(questions)
                }
            else:
                return {
                    'success': False,
                    'error': f'Question index {question_index} out of range (0-{len(questions)-1})'
                }
                
        except Exception as e:
            logger.error(f"Failed to get question {question_index} from {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_questions_by_topic(self, topic: str, user_id: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for worksheet questions related to a specific topic.
        
        Args:
            topic: Topic to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            from utils.faiss_index import search_by_text, get_single_embedding
            
            # Search for relevant worksheet questions
            results = search_by_text(
                topic, 
                k=max_results, 
                embedding_func=get_single_embedding
            )
            
            # Filter by user_id if provided
            if user_id:
                results = [r for r in results if r.get('user_id') == user_id]
            
            # Filter for worksheet questions only
            question_results = [r for r in results if r.get('type') == 'worksheet_question']
            
            return {
                'success': True,
                'results': question_results,
                'count': len(question_results),
                'topic': topic,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to search worksheet questions by topic: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global worksheet service instance
worksheet_service = WorksheetService()


def upload_worksheet(file, title: str = None, user_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to upload and process a worksheet.
    
    Args:
        file: Uploaded file object
        title: Optional title for the worksheet
        user_id: Optional user ID for tracking
        
    Returns:
        Dict[str, Any]: Processing results
    """
    return worksheet_service.upload_and_process_worksheet(file, title, user_id)


def get_worksheet_questions(pdf_path: str) -> Dict[str, Any]:
    """
    Convenience function to get worksheet questions.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dict[str, Any]: Worksheet questions
    """
    return worksheet_service.get_worksheet_questions(pdf_path) 