"""
Review service for semantic search and content retrieval.
Enables finding related study material based on worksheet questions.
"""

import logging
from typing import Dict, Any, Optional, List
from utils.faiss_index import search_by_text, get_single_embedding
from utils.embedding_utils import get_single_embedding as get_embedding

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class ReviewService:
    """Service for handling review and content retrieval operations."""
    
    def __init__(self):
        """Initialize the review service."""
        pass
    
    def get_related_content(self, question_text: str, user_id: str = None, 
                          max_results: int = 10, content_types: List[str] = None) -> Dict[str, Any]:
        """
        Find related study content based on a question.
        
        Args:
            question_text: Text of the question to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results to return
            content_types: List of content types to search (video_segment, note_segment, etc.)
            
        Returns:
            Dict[str, Any]: Related content results
        """
        try:
            logger.info(f"Searching for content related to question: {question_text[:100]}...")
            
            # Search for related content
            results = search_by_text(
                question_text,
                k=max_results * 2,  # Get more results to filter
                embedding_func=get_single_embedding
            )
            
            if not results:
                return {
                    'success': True,
                    'results': [],
                    'count': 0,
                    'question': question_text
                }
            
            # Filter by user_id if provided
            if user_id:
                results = [r for r in results if r.get('user_id') == user_id]
            
            # Filter by content types if specified
            if content_types:
                results = [r for r in results if r.get('type') in content_types]
            
            # Limit results
            results = results[:max_results]
            
            # Group results by type
            grouped_results = {}
            for result in results:
                content_type = result.get('type', 'unknown')
                if content_type not in grouped_results:
                    grouped_results[content_type] = []
                grouped_results[content_type].append(result)
            
            # Calculate relevance scores
            for result in results:
                similarity = result.get('similarity_score', 0)
                result['relevance_percentage'] = round(similarity * 100, 1)
                
                # Add relevance level
                if similarity >= 0.8:
                    result['relevance_level'] = 'high'
                elif similarity >= 0.6:
                    result['relevance_level'] = 'medium'
                else:
                    result['relevance_level'] = 'low'
            
            response = {
                'success': True,
                'results': results,
                'count': len(results),
                'question': question_text,
                'grouped_results': grouped_results,
                'user_id': user_id
            }
            
            logger.info(f"Found {len(results)} related content items for question")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get related content: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_related_video_content(self, question_text: str, user_id: str = None, 
                                max_results: int = 5) -> Dict[str, Any]:
        """
        Find related video content based on a question.
        
        Args:
            question_text: Text of the question to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Related video content results
        """
        return self.get_related_content(
            question_text, 
            user_id, 
            max_results, 
            content_types=['video_segment']
        )
    
    def get_related_note_content(self, question_text: str, user_id: str = None, 
                               max_results: int = 5) -> Dict[str, Any]:
        """
        Find related note content based on a question.
        
        Args:
            question_text: Text of the question to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Related note content results
        """
        return self.get_related_content(
            question_text, 
            user_id, 
            max_results, 
            content_types=['note_segment']
        )
    
    def get_comprehensive_review(self, question_text: str, user_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive review materials for a question.
        
        Args:
            question_text: Text of the question to search for
            user_id: Optional user ID to filter results
            
        Returns:
            Dict[str, Any]: Comprehensive review results
        """
        try:
            # Get related content from all sources
            all_content = self.get_related_content(question_text, user_id, max_results=20)
            
            if not all_content['success']:
                return all_content
            
            results = all_content['results']
            
            # Separate by content type
            video_content = [r for r in results if r.get('type') == 'video_segment']
            note_content = [r for r in results if r.get('type') == 'note_segment']
            
            # Get top results for each type
            top_video = video_content[:3] if video_content else []
            top_notes = note_content[:3] if note_content else []
            
            # Calculate overall relevance
            if results:
                avg_similarity = sum(r.get('similarity_score', 0) for r in results) / len(results)
                overall_relevance = round(avg_similarity * 100, 1)
            else:
                overall_relevance = 0
            
            # Prepare comprehensive response
            response = {
                'success': True,
                'question': question_text,
                'overall_relevance': overall_relevance,
                'video_content': {
                    'count': len(top_video),
                    'results': top_video
                },
                'note_content': {
                    'count': len(top_notes),
                    'results': top_notes
                },
                'total_content_found': len(results),
                'user_id': user_id
            }
            
            logger.info(f"Generated comprehensive review for question with {len(results)} total content items")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive review: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_by_topic(self, topic: str, user_id: str = None, 
                       max_results: int = 15) -> Dict[str, Any]:
        """
        Search for study content by topic.
        
        Args:
            topic: Topic to search for
            user_id: Optional user ID to filter results
            max_results: Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            logger.info(f"Searching for content related to topic: {topic}")
            
            # Search for related content
            results = search_by_text(
                topic,
                k=max_results,
                embedding_func=get_single_embedding
            )
            
            if not results:
                return {
                    'success': True,
                    'results': [],
                    'count': 0,
                    'topic': topic
                }
            
            # Filter by user_id if provided
            if user_id:
                results = [r for r in results if r.get('user_id') == user_id]
            
            # Group by content type
            grouped_results = {}
            for result in results:
                content_type = result.get('type', 'unknown')
                if content_type not in grouped_results:
                    grouped_results[content_type] = []
                grouped_results[content_type].append(result)
            
            # Add relevance information
            for result in results:
                similarity = result.get('similarity_score', 0)
                result['relevance_percentage'] = round(similarity * 100, 1)
                
                if similarity >= 0.8:
                    result['relevance_level'] = 'high'
                elif similarity >= 0.6:
                    result['relevance_level'] = 'medium'
                else:
                    result['relevance_level'] = 'low'
            
            response = {
                'success': True,
                'results': results,
                'count': len(results),
                'topic': topic,
                'grouped_results': grouped_results,
                'user_id': user_id
            }
            
            logger.info(f"Found {len(results)} content items for topic: {topic}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to search by topic: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_study_recommendations(self, question_text: str, user_id: str = None) -> Dict[str, Any]:
        """
        Get personalized study recommendations based on a question.
        
        Args:
            question_text: Text of the question
            user_id: Optional user ID for personalization
            
        Returns:
            Dict[str, Any]: Study recommendations
        """
        try:
            # Get related content
            content_results = self.get_comprehensive_review(question_text, user_id)
            
            if not content_results['success']:
                return content_results
            
            # Analyze content to generate recommendations
            video_content = content_results['video_content']['results']
            note_content = content_results['note_content']['results']
            
            recommendations = []
            
            # Video recommendations
            if video_content:
                high_relevance_videos = [v for v in video_content if v.get('relevance_level') == 'high']
                if high_relevance_videos:
                    recommendations.append({
                        'type': 'video_review',
                        'title': 'Review Related Video Content',
                        'description': f'Watch {len(high_relevance_videos)} highly relevant video segments',
                        'content': high_relevance_videos[:2],
                        'priority': 'high'
                    })
            
            # Note recommendations
            if note_content:
                high_relevance_notes = [n for n in note_content if n.get('relevance_level') == 'high']
                if high_relevance_notes:
                    recommendations.append({
                        'type': 'note_review',
                        'title': 'Review Related Notes',
                        'description': f'Study {len(high_relevance_notes)} highly relevant note sections',
                        'content': high_relevance_notes[:2],
                        'priority': 'high'
                    })
            
            # General study recommendations
            if not recommendations:
                recommendations.append({
                    'type': 'general_study',
                    'title': 'General Study Recommendation',
                    'description': 'Review your uploaded study materials for this topic',
                    'priority': 'medium'
                })
            
            response = {
                'success': True,
                'question': question_text,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'user_id': user_id
            }
            
            logger.info(f"Generated {len(recommendations)} study recommendations")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get study recommendations: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global review service instance
review_service = ReviewService()


def get_related_content(question_text: str, user_id: str = None, 
                       max_results: int = 10, content_types: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get related content.
    
    Args:
        question_text: Text of the question to search for
        user_id: Optional user ID to filter results
        max_results: Maximum number of results
        content_types: List of content types to search
        
    Returns:
        Dict[str, Any]: Related content results
    """
    return review_service.get_related_content(question_text, user_id, max_results, content_types)


def get_comprehensive_review(question_text: str, user_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to get comprehensive review.
    
    Args:
        question_text: Text of the question
        user_id: Optional user ID for personalization
        
    Returns:
        Dict[str, Any]: Comprehensive review results
    """
    return review_service.get_comprehensive_review(question_text, user_id) 