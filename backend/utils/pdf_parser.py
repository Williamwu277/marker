"""
PDF parser utility for extracting and segmenting text from PDF files.
Uses pdfplumber for text extraction with heading detection and fallback chunking.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
import pdfplumber
from config.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for extracting and segmenting text from PDF files."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize the PDF parser.
        
        Args:
            chunk_size: Maximum size of text chunks in characters
            overlap: Overlap between consecutive chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = '\n'.join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF: {pdf_path}")
            return full_text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise
    
    def detect_headings(self, text: str) -> List[Tuple[int, str, str]]:
        """
        Detect headings in the text using common patterns.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List[Tuple[int, str, str]]: List of (position, heading_text, level) tuples
        """
        headings = []
        lines = text.split('\n')
        
        # Common heading patterns
        heading_patterns = [
            (r'^(\d+\.\s+)(.+)$', 'numbered'),  # 1. Heading
            (r'^([A-Z][A-Z\s]+)$', 'uppercase'),  # ALL CAPS HEADING
            (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$', 'title_case'),  # Title Case Heading
            (r'^(Chapter\s+\d+.*)$', 'chapter'),  # Chapter headings
            (r'^(Section\s+\d+.*)$', 'section'),  # Section headings
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            for pattern, level in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    headings.append((i, line, level))
                    break
        
        logger.debug(f"Detected {len(headings)} headings in text")
        return headings
    
    def segment_by_headings(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by detected headings.
        
        Args:
            text: Text content to segment
            
        Returns:
            List[Dict[str, Any]]: List of segments with metadata
        """
        headings = self.detect_headings(text)
        lines = text.split('\n')
        segments = []
        
        if not headings:
            # Fallback to chunking if no headings detected
            return self.chunk_text(text)
        
        # Add start and end positions
        heading_positions = [0] + [h[0] for h in headings] + [len(lines)]
        
        for i in range(len(headings)):
            start_pos = heading_positions[i]
            end_pos = heading_positions[i + 1]
            
            # Extract segment text
            segment_lines = lines[start_pos:end_pos]
            segment_text = '\n'.join(segment_lines).strip()
            
            if segment_text:
                segments.append({
                    'text': segment_text,
                    'heading': headings[i][1],
                    'level': headings[i][2],
                    'start_line': start_pos,
                    'end_line': end_pos - 1,
                    'type': 'heading_based'
                })
        
        # Handle text after last heading
        if headings:
            last_heading_pos = headings[-1][0]
            remaining_lines = lines[last_heading_pos + 1:]
            remaining_text = '\n'.join(remaining_lines).strip()
            
            if remaining_text:
                segments.append({
                    'text': remaining_text,
                    'heading': 'Additional Content',
                    'level': 'content',
                    'start_line': last_heading_pos + 1,
                    'end_line': len(lines) - 1,
                    'type': 'heading_based'
                })
        
        logger.info(f"Created {len(segments)} segments based on headings")
        return segments
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller segments with overlap.
        
        Args:
            text: Text content to chunk
            
        Returns:
            List[Dict[str, Any]]: List of text chunks with metadata
        """
        if len(text) <= self.chunk_size:
            return [{
                'text': text,
                'heading': 'Content',
                'level': 'chunk',
                'start_char': 0,
                'end_char': len(text),
                'type': 'chunked'
            }]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_endings = ['.', '!', '?', '\n\n']
                for ending in sentence_endings:
                    last_ending = text.rfind(ending, start, end)
                    if last_ending > start + self.chunk_size * 0.7:  # Only break if we're at least 70% through
                        end = last_ending + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'heading': f'Chunk {len(chunks) + 1}',
                    'level': 'chunk',
                    'start_char': start,
                    'end_char': end,
                    'type': 'chunked'
                })
            
            start = end - self.overlap
            if start >= len(text):
                break
        
        logger.info(f"Created {len(chunks)} text chunks")
        return chunks
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Parse a PDF file and return segmented content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List[Dict[str, Any]]: List of text segments with metadata
        """
        try:
            # Extract text from PDF
            text = self.extract_text(pdf_path)
            
            if not text.strip():
                logger.warning(f"No text content found in PDF: {pdf_path}")
                return []
            
            # Try to segment by headings first
            segments = self.segment_by_headings(text)
            
            # If no segments created, fall back to chunking
            if not segments:
                segments = self.chunk_text(text)
            
            # Add file metadata to each segment
            for segment in segments:
                segment['source_file'] = pdf_path
                segment['text_length'] = len(segment['text'])
            
            logger.info(f"Successfully parsed PDF {pdf_path} into {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {e}")
            raise
    
    def get_text_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the parsed text segments.
        
        Args:
            segments: List of text segments
            
        Returns:
            Dict[str, Any]: Statistics about the segments
        """
        if not segments:
            return {}
        
        total_chars = sum(len(seg['text']) for seg in segments)
        total_words = sum(len(seg['text'].split()) for seg in segments)
        
        return {
            'total_segments': len(segments),
            'total_characters': total_chars,
            'total_words': total_words,
            'avg_chars_per_segment': total_chars / len(segments),
            'avg_words_per_segment': total_words / len(segments),
            'segment_types': list(set(seg['type'] for seg in segments)),
            'heading_levels': list(set(seg['level'] for seg in segments))
        }


# Global PDF parser instance
pdf_parser = PDFParser()


def parse_pdf_file(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Convenience function to parse a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List[Dict[str, Any]]: List of text segments
    """
    return pdf_parser.parse_pdf(pdf_path) 