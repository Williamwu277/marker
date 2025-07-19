"""
Twelve Labs API client for video processing and summarization.
Handles authenticated requests and response processing from the Twelve Labs API.
"""

import logging
import time
import os
from typing import List, Dict, Any, Optional
import requests
from config.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class TwelveLabsClient:
    """Client for interacting with the Twelve Labs API."""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.twelvelabs.io/v1.2"):
        """
        Initialize the Twelve Labs client.
        
        Args:
            api_key: Twelve Labs API key
            base_url: Base URL for the Twelve Labs API
        """
        self.api_key = api_key or Config.TWELVE_LABS_API_KEY
        self.base_url = base_url
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.warning("No Twelve Labs API key provided")
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                     files: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Twelve Labs API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            files: Files to upload
            
        Returns:
            Optional[Dict[str, Any]]: API response or None if failed
        """
        if not self.api_key:
            logger.error("No API key available for Twelve Labs requests")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=60)
                elif method.upper() == "POST":
                    if files:
                        # Remove Content-Type for file uploads
                        headers.pop("Content-Type", None)
                        response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
                    else:
                        response = requests.post(url, headers=headers, json=data, timeout=60)
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Twelve Labs API request successful: {method} {endpoint}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Twelve Labs API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All retry attempts failed for Twelve Labs API request: {method} {endpoint}")
                    return None
    
    def upload_video(self, video_path: str, title: str = None) -> Optional[str]:
        """
        Upload a video to Twelve Labs for processing.
        
        Args:
            video_path: Path to the video file
            title: Optional title for the video
            
        Returns:
            Optional[str]: Video ID if successful, None otherwise
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'title': title or os.path.basename(video_path),
                    'index_id': 'default'  # You can customize this
                }
                
                response = self._make_request("POST", "tasks", data=data, files=files)
                
                if response and 'id' in response:
                    task_id = response['id']
                    logger.info(f"Video upload task created: {task_id}")
                    return task_id
                else:
                    logger.error("Failed to get task ID from upload response")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to upload video {video_path}: {e}")
            return None
    
    def check_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Check the status of a processing task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Optional[Dict[str, Any]]: Task status information
        """
        response = self._make_request("GET", f"tasks/{task_id}")
        
        if response:
            status = response.get('status', 'unknown')
            logger.debug(f"Task {task_id} status: {status}")
            return response
        
        return None
    
    def wait_for_task_completion(self, task_id: str, max_wait_time: int = 300) -> Optional[Dict[str, Any]]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: ID of the task to wait for
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Optional[Dict[str, Any]]: Final task status or None if failed
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_info = self.check_task_status(task_id)
            
            if not status_info:
                logger.error(f"Failed to get status for task {task_id}")
                return None
            
            status = status_info.get('status', 'unknown')
            
            if status == 'ready':
                logger.info(f"Task {task_id} completed successfully")
                return status_info
            elif status == 'failed':
                logger.error(f"Task {task_id} failed")
                return status_info
            elif status in ['pending', 'processing']:
                logger.debug(f"Task {task_id} still processing...")
                time.sleep(10)  # Wait 10 seconds before checking again
            else:
                logger.warning(f"Unknown task status: {status}")
                time.sleep(10)
        
        logger.error(f"Task {task_id} did not complete within {max_wait_time} seconds")
        return None
    
    def get_video_summary(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a processed video.
        
        Args:
            video_id: ID of the processed video
            
        Returns:
            Optional[Dict[str, Any]]: Video summary information
        """
        response = self._make_request("GET", f"videos/{video_id}")
        
        if response:
            logger.info(f"Retrieved summary for video {video_id}")
            return response
        
        return None
    
    def get_video_segments(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get segmented text from a processed video.
        
        Args:
            video_id: ID of the processed video
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of video segments with text
        """
        response = self._make_request("GET", f"videos/{video_id}/segments")
        
        if response and 'segments' in response:
            segments = response['segments']
            logger.info(f"Retrieved {len(segments)} segments for video {video_id}")
            return segments
        
        return None
    
    def process_video(self, video_path: str, title: str = None) -> Optional[Dict[str, Any]]:
        """
        Complete video processing pipeline: upload, wait for completion, and get results.
        
        Args:
            video_path: Path to the video file
            title: Optional title for the video
            
        Returns:
            Optional[Dict[str, Any]]: Complete video processing results
        """
        try:
            # Step 1: Upload video
            logger.info(f"Uploading video: {video_path}")
            task_id = self.upload_video(video_path, title)
            
            if not task_id:
                logger.error("Failed to upload video")
                return None
            
            # Step 2: Wait for processing to complete
            logger.info("Waiting for video processing to complete...")
            task_result = self.wait_for_task_completion(task_id)
            
            if not task_result or task_result.get('status') != 'ready':
                logger.error("Video processing failed or timed out")
                return None
            
            # Step 3: Get video ID from task result
            video_id = task_result.get('video_id')
            if not video_id:
                logger.error("No video ID found in task result")
                return None
            
            # Step 4: Get video summary and segments
            logger.info("Retrieving video content...")
            summary = self.get_video_summary(video_id)
            segments = self.get_video_segments(video_id)
            
            # Step 5: Compile results
            results = {
                'video_id': video_id,
                'task_id': task_id,
                'title': title or os.path.basename(video_path),
                'summary': summary,
                'segments': segments or [],
                'status': 'completed'
            }
            
            logger.info(f"Successfully processed video {video_id} with {len(segments or [])} segments")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process video {video_path}: {e}")
            return None
    
    def search_videos(self, query: str, video_ids: List[str] = None, 
                     max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Search for content within videos.
        
        Args:
            query: Search query
            video_ids: List of video IDs to search in (optional)
            max_results: Maximum number of results to return
            
        Returns:
            Optional[List[Dict[str, Any]]]: Search results
        """
        data = {
            'query': query,
            'max_results': max_results
        }
        
        if video_ids:
            data['video_ids'] = video_ids
        
        response = self._make_request("POST", "search", data=data)
        
        if response and 'data' in response:
            results = response['data']
            logger.info(f"Found {len(results)} search results for query: {query}")
            return results
        
        return None
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Optional[Dict[str, Any]]: Video metadata
        """
        response = self._make_request("GET", f"videos/{video_id}")
        
        if response:
            # Extract relevant metadata
            metadata = {
                'id': response.get('id'),
                'title': response.get('title'),
                'duration': response.get('duration'),
                'created_at': response.get('created_at'),
                'status': response.get('status'),
                'thumbnail_url': response.get('thumbnail_url')
            }
            return metadata
        
        return None


# Global Twelve Labs client instance
twelve_labs_client = TwelveLabsClient()


def process_video_file(video_path: str, title: str = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to process a video file.
    
    Args:
        video_path: Path to the video file
        title: Optional title for the video
        
    Returns:
        Optional[Dict[str, Any]]: Processing results
    """
    return twelve_labs_client.process_video(video_path, title)


def search_video_content(query: str, video_ids: List[str] = None, 
                        max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Convenience function to search video content.
    
    Args:
        query: Search query
        video_ids: List of video IDs to search in
        max_results: Maximum number of results
        
    Returns:
        Optional[List[Dict[str, Any]]]: Search results
    """
    return twelve_labs_client.search_videos(query, video_ids, max_results) 