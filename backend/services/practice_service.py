"""
Practice service for generating personalized practice questions.
Uses Gemini API to create questions based on weak areas and study material.
"""

import logging
from typing import Dict, Any, Optional, List
from utils.gemini_client import gemini_client
from services.review_service import review_service

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class PracticeService:
    """Service for handling practice question generation."""
    
    def __init__(self):
        """Initialize the practice service."""
        pass
    
    def generate_practice_questions(self, topic: str, difficulty: str = "medium", 
                                  num_questions: int = 5, context: str = "", 
                                  user_id: str = None) -> Dict[str, Any]:
        """
        Generate practice questions for a given topic.
        
        Args:
            topic: Topic to generate questions for
            difficulty: Difficulty level (easy, medium, hard)
            num_questions: Number of questions to generate
            context: Additional context or study material
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Generated practice questions
        """
        try:
            logger.info(f"Generating {num_questions} {difficulty} practice questions for topic: {topic}")
            
            # Generate questions using Gemini
            questions = gemini_client.generate_practice_questions(
                topic, difficulty, num_questions, context
            )
            
            if not questions:
                return {
                    'success': False,
                    'error': 'Failed to generate practice questions'
                }
            
            # Add metadata to questions
            for i, question in enumerate(questions):
                question['id'] = f"practice_{i}_{topic.replace(' ', '_')}"
                question['topic'] = topic
                question['difficulty'] = difficulty
                question['user_id'] = user_id
                question['generated_at'] = time.time()
            
            response = {
                'success': True,
                'questions': questions,
                'count': len(questions),
                'topic': topic,
                'difficulty': difficulty,
                'user_id': user_id
            }
            
            logger.info(f"Successfully generated {len(questions)} practice questions")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate practice questions: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_questions_from_weak_areas(self, weak_areas: List[str], 
                                         study_material: str = "", 
                                         user_id: str = None) -> Dict[str, Any]:
        """
        Generate practice questions based on identified weak areas.
        
        Args:
            weak_areas: List of weak areas/topics
            study_material: Study material context
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Generated practice questions
        """
        try:
            if not weak_areas:
                return {
                    'success': False,
                    'error': 'No weak areas provided'
                }
            
            logger.info(f"Generating questions for weak areas: {weak_areas}")
            
            all_questions = []
            
            # Generate questions for each weak area
            for area in weak_areas:
                # Generate 2-3 questions per weak area
                num_questions = min(3, max(2, 10 // len(weak_areas)))
                
                questions = gemini_client.generate_practice_questions(
                    area, "medium", num_questions, study_material
                )
                
                if questions:
                    # Add metadata
                    for i, question in enumerate(questions):
                        question['id'] = f"weak_area_{area.replace(' ', '_')}_{i}"
                        question['topic'] = area
                        question['weak_area'] = True
                        question['user_id'] = user_id
                        question['generated_at'] = time.time()
                    
                    all_questions.extend(questions)
            
            if not all_questions:
                return {
                    'success': False,
                    'error': 'Failed to generate questions for weak areas'
                }
            
            response = {
                'success': True,
                'questions': all_questions,
                'count': len(all_questions),
                'weak_areas': weak_areas,
                'user_id': user_id
            }
            
            logger.info(f"Generated {len(all_questions)} questions for {len(weak_areas)} weak areas")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate questions from weak areas: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_questions_from_worksheet(self, worksheet_questions: List[Dict[str, Any]], 
                                        user_id: str = None) -> Dict[str, Any]:
        """
        Generate additional practice questions based on worksheet questions.
        
        Args:
            worksheet_questions: List of worksheet questions
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Generated practice questions
        """
        try:
            if not worksheet_questions:
                return {
                    'success': False,
                    'error': 'No worksheet questions provided'
                }
            
            logger.info(f"Generating practice questions from {len(worksheet_questions)} worksheet questions")
            
            all_questions = []
            
            # Analyze each worksheet question and generate related practice questions
            for i, worksheet_q in enumerate(worksheet_questions):
                question_text = worksheet_q.get('text', '')
                
                if not question_text:
                    continue
                
                # Get related content for context
                related_content = review_service.get_comprehensive_review(question_text, user_id)
                
                # Extract context from related content
                context_parts = []
                if related_content['success']:
                    video_content = related_content['video_content']['results']
                    note_content = related_content['note_content']['results']
                    
                    # Add top video content
                    for video in video_content[:2]:
                        context_parts.append(f"Video: {video.get('content', '')}")
                    
                    # Add top note content
                    for note in note_content[:2]:
                        context_parts.append(f"Notes: {note.get('content', '')}")
                
                context = "\n".join(context_parts)
                
                # Generate 1-2 related practice questions
                related_questions = gemini_client.generate_practice_questions(
                    f"Related to: {question_text[:100]}",
                    "medium",
                    2,
                    context
                )
                
                if related_questions:
                    # Add metadata
                    for j, question in enumerate(related_questions):
                        question['id'] = f"worksheet_related_{i}_{j}"
                        question['related_to_worksheet'] = True
                        question['worksheet_question_index'] = i
                        question['worksheet_question'] = question_text[:200]
                        question['user_id'] = user_id
                        question['generated_at'] = time.time()
                    
                    all_questions.extend(related_questions)
            
            if not all_questions:
                return {
                    'success': False,
                    'error': 'Failed to generate related practice questions'
                }
            
            response = {
                'success': True,
                'questions': all_questions,
                'count': len(all_questions),
                'source_worksheet_questions': len(worksheet_questions),
                'user_id': user_id
            }
            
            logger.info(f"Generated {len(all_questions)} practice questions from worksheet")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate questions from worksheet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_user_responses(self, user_responses: List[Dict[str, Any]], 
                             study_material: str = "") -> Dict[str, Any]:
        """
        Analyze user responses to practice questions and provide feedback.
        
        Args:
            user_responses: List of user responses with questions and answers
            study_material: Study material context
            
        Returns:
            Dict[str, Any]: Analysis results and recommendations
        """
        try:
            if not user_responses:
                return {
                    'success': False,
                    'error': 'No user responses provided'
                }
            
            logger.info(f"Analyzing {len(user_responses)} user responses")
            
            # Analyze weak areas using Gemini
            analysis = gemini_client.analyze_weak_areas(study_material, user_responses)
            
            if not analysis:
                return {
                    'success': False,
                    'error': 'Failed to analyze user responses'
                }
            
            # Calculate performance metrics
            correct_count = sum(1 for response in user_responses if response.get('correct', False))
            total_questions = len(user_responses)
            accuracy = correct_count / total_questions if total_questions > 0 else 0
            
            # Add performance metrics to analysis
            analysis['performance_metrics'] = {
                'total_questions': total_questions,
                'correct_answers': correct_count,
                'incorrect_answers': total_questions - correct_count,
                'accuracy_percentage': round(accuracy * 100, 1),
                'accuracy_decimal': accuracy
            }
            
            response = {
                'success': True,
                'analysis': analysis,
                'user_responses_count': len(user_responses)
            }
            
            logger.info(f"Successfully analyzed user responses with {accuracy:.1%} accuracy")
            return response
            
        except Exception as e:
            logger.error(f"Failed to analyze user responses: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_explanation(self, question: str, correct_answer: str, 
                           user_answer: str = None) -> Dict[str, Any]:
        """
        Generate an explanation for a question and answer.
        
        Args:
            question: The question text
            correct_answer: The correct answer
            user_answer: The user's answer (optional)
            
        Returns:
            Dict[str, Any]: Generated explanation
        """
        try:
            explanation = gemini_client.generate_explanation(question, correct_answer, user_answer)
            
            if explanation:
                response = {
                    'success': True,
                    'explanation': explanation,
                    'question': question,
                    'correct_answer': correct_answer,
                    'user_answer': user_answer
                }
            else:
                response = {
                    'success': False,
                    'error': 'Failed to generate explanation'
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_practice_session(self, topics: List[str], difficulty: str = "medium", 
                              num_questions_per_topic: int = 3, user_id: str = None) -> Dict[str, Any]:
        """
        Create a comprehensive practice session with questions from multiple topics.
        
        Args:
            topics: List of topics to include
            difficulty: Difficulty level
            num_questions_per_topic: Number of questions per topic
            user_id: Optional user ID for tracking
            
        Returns:
            Dict[str, Any]: Practice session with questions
        """
        try:
            if not topics:
                return {
                    'success': False,
                    'error': 'No topics provided'
                }
            
            logger.info(f"Creating practice session for topics: {topics}")
            
            session_questions = []
            
            # Generate questions for each topic
            for topic in topics:
                questions = gemini_client.generate_practice_questions(
                    topic, difficulty, num_questions_per_topic
                )
                
                if questions:
                    # Add session metadata
                    for i, question in enumerate(questions):
                        question['id'] = f"session_{topic.replace(' ', '_')}_{i}"
                        question['topic'] = topic
                        question['session_topic'] = topic
                        question['difficulty'] = difficulty
                        question['user_id'] = user_id
                        question['generated_at'] = time.time()
                    
                    session_questions.extend(questions)
            
            if not session_questions:
                return {
                    'success': False,
                    'error': 'Failed to generate session questions'
                }
            
            # Create session metadata
            session_id = f"session_{int(time.time())}"
            
            response = {
                'success': True,
                'session_id': session_id,
                'questions': session_questions,
                'count': len(session_questions),
                'topics': topics,
                'difficulty': difficulty,
                'user_id': user_id,
                'created_at': time.time()
            }
            
            logger.info(f"Created practice session {session_id} with {len(session_questions)} questions")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create practice session: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global practice service instance
practice_service = PracticeService()


def generate_practice_questions(topic: str, difficulty: str = "medium", 
                              num_questions: int = 5, context: str = "", 
                              user_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to generate practice questions.
    
    Args:
        topic: Topic to generate questions for
        difficulty: Difficulty level
        num_questions: Number of questions
        context: Additional context
        user_id: Optional user ID
        
    Returns:
        Dict[str, Any]: Generated practice questions
    """
    return practice_service.generate_practice_questions(topic, difficulty, num_questions, context, user_id)


def analyze_user_responses(user_responses: List[Dict[str, Any]], 
                         study_material: str = "") -> Dict[str, Any]:
    """
    Convenience function to analyze user responses.
    
    Args:
        user_responses: List of user responses
        study_material: Study material context
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    return practice_service.analyze_user_responses(user_responses, study_material) 