"""
Video service for handling video uploads and processing.
Integrates with Twelve Labs API for video summarization and segmentation.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename
from config.config import Config
from utils.twelve_labs_client import twelve_labs_client
from utils.embedding_utils import get_embeddings
from utils.faiss_index import add_to_index

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class VideoService:
    """Service for handling video-related operations."""
    
    def __init__(self):
        """Initialize the video service."""
        self.upload_folder = Config.UPLOAD_FOLDER
        Config.ensure_upload_folder()
    
    def allowed_video_file(self, filename: str) -> bool:
        """
        Check if the uploaded file has an allowed video extension.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            bool: True if file extension is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_VIDEO_EXTENSIONS
    
    def save_video_file(self, file) -> Optional[str]:
        """
        Save an uploaded video file to the upload folder.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Optional[str]: Path to saved file or None if failed
        """
        try:
            if file and self.allowed_video_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.upload_folder, filename)
                file.save(file_path)
                logger.info(f"Saved video file: {file_path}")
                return file_path
            else:
                logger.error(f"Invalid video file: {file.filename if file else 'None'}")
                return None
        except Exception as e:
            logger.error(f"Failed to save video file: {e}")
            return None
    
    def process_video(self, video_path: str, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Process a video file using Twelve Labs API.
        
        Args:
            video_path: Path to the video file
            title: Optional title for the video
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            logger.info(f"Processing video: {video_path}")
            
            # Process video with Twelve Labs
            results = twelve_labs_client.process_video(video_path, title)
            
            if not results:
                return {
                    'success': False,
                    'error': 'Failed to process video with Twelve Labs API'
                }
            
            # Extract segments for embedding
            segments = results.get('segments', [])
            if segments:
                # Prepare segments for embedding
                segment_texts = []
                segment_metadata = []
                
                for i, segment in enumerate(segments):
                    text = segment.get('text', '').strip()
                    if text:
                        segment_texts.append(text)
                        segment_metadata.append({
                            'type': 'video_segment',
                            'source': 'twelve_labs',
                            'video_id': results.get('video_id'),
                            'segment_index': i,
                            'start_time': segment.get('start', 0),
                            'end_time': segment.get('end', 0),
                            'title': results.get('title', ''),
                            'user_id': user_id,
                            'content': text[:200] + '...' if len(text) > 200 else text
                        })
                
                # Generate embeddings for segments
                if segment_texts:
                    try:
                        embeddings = get_embeddings(segment_texts)
                        add_to_index(embeddings, segment_metadata)
                        logger.info(f"Added {len(embeddings)} video segment embeddings to index")
                    except Exception as e:
                        logger.error(f"Failed to create embeddings for video segments: {e}")
            
            # Prepare response
            response = {
                'success': True,
                'video_id': results.get('video_id'),
                'title': results.get('title'),
                'segments_count': len(segments),
                'summary': results.get('summary', {}),
                'processing_time': results.get('processing_time'),
                'file_path': video_path
            }
            
            logger.info(f"Successfully processed video {results.get('video_id')} with {len(segments)} segments")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process video {video_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_and_process_video(self, file, title: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Upload and process a video file in one operation.
        
        Args:
            file: Uploaded file object
            title: Optional title for the video
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            # Save the uploaded file
            video_path = self.save_video_file(file)
            
            if not video_path:
                return {
                    'success': False,
                    'error': 'Failed to save uploaded video file'
                }
            
            # Process the video
            return self.process_video(video_path, title, user_id)
            
        except Exception as e:
            logger.error(f"Failed to upload and process video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_video_summary(self, video_id: str) -> Dict[str, Any]:
        """
        Get summary information for a processed video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Dict[str, Any]: Video summary information
        """
        try:
            summary = twelve_labs_client.get_video_summary(video_id)
            
            if summary:
                return {
                    'success': True,
                    'summary': summary
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to retrieve video summary'
                }
                
        except Exception as e:
            logger.error(f"Failed to get video summary for {video_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_video_segments(self, video_id: str) -> Dict[str, Any]:
        """
        Get segmented content for a processed video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Dict[str, Any]: Video segments information
        """
        try:
            segments = twelve_labs_client.get_video_segments(video_id)
            
            if segments is not None:
                return {
                    'success': True,
                    'segments': segments,
                    'count': len(segments)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to retrieve video segments'
                }
                
        except Exception as e:
            logger.error(f"Failed to get video segments for {video_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_video_content(self, query: str, video_ids: List[str] = None, 
                           max_results: int = 10) -> Dict[str, Any]:
        """
        Search for content within videos.
        
        Args:
            query: Search query
            video_ids: List of video IDs to search in (optional)
            max_results: Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            results = twelve_labs_client.search_videos(query, video_ids, max_results)
            
            if results is not None:
                return {
                    'success': True,
                    'results': results,
                    'count': len(results),
                    'query': query
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to search video content'
                }
                
        except Exception as e:
            logger.error(f"Failed to search video content: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Dict[str, Any]: Video metadata
        """
        try:
            metadata = twelve_labs_client.get_video_metadata(video_id)
            
            if metadata:
                return {
                    'success': True,
                    'metadata': metadata
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to retrieve video metadata'
                }
                
        except Exception as e:
            logger.error(f"Failed to get video metadata for {video_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global video service instance
video_service = VideoService()


def upload_video(file, title: str = None, user_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to upload and process a video.
    
    Args:
        file: Uploaded file object
        title: Optional title for the video
        user_id: Optional user ID for tracking
        
    Returns:
        Dict[str, Any]: Processing results
    """
    return video_service.upload_and_process_video(file, title, user_id)


def get_video_summary(video_id: str) -> Dict[str, Any]:
    """
    Convenience function to get video summary.
    
    Args:
        video_id: ID of the video
        
    Returns:
        Dict[str, Any]: Video summary
    """
    return video_service.get_video_summary(video_id) 