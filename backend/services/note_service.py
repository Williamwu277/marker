"""
Note service for handling PDF note uploads and processing.
Integrates with PDF parser for text extraction and embedding.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename
from config.config import Config
from utils.pdf_parser import parse_pdf_file
from utils.embedding_utils import get_embeddings
from utils.faiss_index import add_to_index

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class NoteService:
    """Service for handling note-related operations."""
    
    def __init__(self):
        """Initialize the note service."""
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
                logger.info(f"Saved PDF file: {file_path}")
                return file_path
            else:
                logger.error(f"Invalid PDF file: {file.filename if file else 'None'}")
                return None
        except Exception as e:
            logger.error(f"Failed to save PDF file: {e}")
            return None
    
    def process_notes(self, pdf_path: str, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Process a PDF file and extract note segments.
        
        Args:
            pdf_path: Path to the PDF file
            title: Optional title for the notes
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            logger.info(f"Processing notes: {pdf_path}")
            
            # Parse PDF file
            segments = parse_pdf_file(pdf_path)
            
            if not segments:
                return {
                    'success': False,
                    'error': 'No content extracted from PDF file'
                }
            
            # Prepare segments for embedding
            segment_texts = []
            segment_metadata = []
            
            for i, segment in enumerate(segments):
                text = segment.get('text', '').strip()
                if text:
                    segment_texts.append(text)
                    segment_metadata.append({
                        'type': 'note_segment',
                        'source': 'pdf_parser',
                        'file_path': pdf_path,
                        'segment_index': i,
                        'heading': segment.get('heading', ''),
                        'level': segment.get('level', ''),
                        'segment_type': segment.get('type', ''),
                        'title': title or os.path.basename(pdf_path),
                        'user_id': user_id,
                        'content': text[:200] + '...' if len(text) > 200 else text,
                        'text_length': segment.get('text_length', len(text))
                    })
            
            # Generate embeddings for segments
            if segment_texts:
                try:
                    embeddings = get_embeddings(segment_texts)
                    add_to_index(embeddings, segment_metadata)
                    logger.info(f"Added {len(embeddings)} note segment embeddings to index")
                except Exception as e:
                    logger.error(f"Failed to create embeddings for note segments: {e}")
            
            # Calculate statistics
            total_chars = sum(len(text) for text in segment_texts)
            total_words = sum(len(text.split()) for text in segment_texts)
            
            # Prepare response
            response = {
                'success': True,
                'file_path': pdf_path,
                'title': title or os.path.basename(pdf_path),
                'segments_count': len(segments),
                'total_characters': total_chars,
                'total_words': total_words,
                'avg_chars_per_segment': total_chars / len(segments) if segments else 0,
                'avg_words_per_segment': total_words / len(segments) if segments else 0,
                'segment_types': list(set(seg.get('type', '') for seg in segments)),
                'heading_levels': list(set(seg.get('level', '') for seg in segments))
            }
            
            logger.info(f"Successfully processed notes {pdf_path} with {len(segments)} segments")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process notes {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_and_process_notes(self, file, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Upload and process a PDF file in one operation.
        
        Args:
            file: Uploaded file object
            title: Optional title for the notes
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
                    'error': 'Failed to save uploaded PDF file'
                }
            
            # Process the notes
            return self.process_notes(pdf_path, title, user_id)
            
        except Exception as e:
            logger.error(f"Failed to upload and process notes: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_note_statistics(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get statistics about a processed PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict[str, Any]: Note statistics
        """
        try:
            segments = parse_pdf_file(pdf_path)
            
            if not segments:
                return {
                    'success': False,
                    'error': 'No content found in PDF file'
                }
            
            # Calculate statistics
            total_chars = sum(len(seg.get('text', '')) for seg in segments)
            total_words = sum(len(seg.get('text', '').split()) for seg in segments)
            
            stats = {
                'success': True,
                'file_path': pdf_path,
                'total_segments': len(segments),
                'total_characters': total_chars,
                'total_words': total_words,
                'avg_chars_per_segment': total_chars / len(segments) if segments else 0,
                'avg_words_per_segment': total_words / len(segments) if segments else 0,
                'segment_types': list(set(seg.get('type', '') for seg in segments)),
                'heading_levels': list(set(seg.get('level', '') for seg in segments)),
                'headings': [seg.get('heading', '') for seg in segments if seg.get('heading')]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get note statistics for {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_note_segments(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract and return note segments from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict[str, Any]: Note segments
        """
        try:
            segments = parse_pdf_file(pdf_path)
            
            if segments:
                return {
                    'success': True,
                    'segments': segments,
                    'count': len(segments),
                    'file_path': pdf_path
                }
            else:
                return {
                    'success': False,
                    'error': 'No segments extracted from PDF file'
                }
                
        except Exception as e:
            logger.error(f"Failed to extract note segments from {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_notes_by_topic(self, topic: str, user_id: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for note segments related to a specific topic.
        
        Args:
            topic: Topic to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            from utils.faiss_index import search_by_text, get_single_embedding
            
            # Search for relevant note segments
            results = search_by_text(
                topic, 
                k=max_results, 
                embedding_func=get_single_embedding
            )
            
            # Filter by user_id if provided
            if user_id:
                results = [r for r in results if r.get('user_id') == user_id]
            
            # Filter for note segments only
            note_results = [r for r in results if r.get('type') == 'note_segment']
            
            return {
                'success': True,
                'results': note_results,
                'count': len(note_results),
                'topic': topic,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Failed to search notes by topic: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_note_headings(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get all headings from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict[str, Any]: Note headings
        """
        try:
            segments = parse_pdf_file(pdf_path)
            
            if not segments:
                return {
                    'success': False,
                    'error': 'No content found in PDF file'
                }
            
            # Extract headings
            headings = []
            for segment in segments:
                heading = segment.get('heading', '').strip()
                level = segment.get('level', '')
                if heading and heading != 'Content':
                    headings.append({
                        'text': heading,
                        'level': level,
                        'segment_index': segment.get('segment_index', 0)
                    })
            
            return {
                'success': True,
                'headings': headings,
                'count': len(headings),
                'file_path': pdf_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get note headings from {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global note service instance
note_service = NoteService()


def upload_notes(file, title: str = None, user_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to upload and process notes.
    
    Args:
        file: Uploaded file object
        title: Optional title for the notes
        user_id: Optional user ID for tracking
        
    Returns:
        Dict[str, Any]: Processing results
    """
    return note_service.upload_and_process_notes(file, title, user_id)


def get_note_statistics(pdf_path: str) -> Dict[str, Any]:
    """
    Convenience function to get note statistics.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dict[str, Any]: Note statistics
    """
    return note_service.get_note_statistics(pdf_path) 