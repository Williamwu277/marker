"""
Gemini API client for generating practice questions and AI-powered content.
Handles secure API communication with error handling and retries.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import requests
from config.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with the Gemini API."""
    
    def __init__(self, api_key: str = None, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key
            base_url: Base URL for the Gemini API
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.base_url = base_url
        self.model = "models/gemini-pro"
        self.max_retries = 3
        self.retry_delay = 1
        
        if not self.api_key:
            logger.warning("No Gemini API key provided")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Gemini API with retry logic.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Optional[Dict[str, Any]]: API response or None if failed
        """
        if not self.api_key:
            logger.error("No API key available for Gemini requests")
            return None
        
        url = f"{self.base_url}/{endpoint}?key={self.api_key}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Gemini API request successful: {endpoint}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Gemini API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All retry attempts failed for Gemini API request: {endpoint}")
                    return None
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using the Gemini API.
        
        Args:
            prompt: Text prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Optional[str]: Generated text or None if failed
        """
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        endpoint = f"{self.model}:generateContent"
        response = self._make_request(endpoint, data)
        
        if response and 'candidates' in response:
            try:
                generated_text = response['candidates'][0]['content']['parts'][0]['text']
                return generated_text
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Gemini response: {e}")
                return None
        
        return None
    
    def generate_practice_questions(self, topic: str, difficulty: str = "medium", 
                                  num_questions: int = 5, context: str = "") -> List[Dict[str, Any]]:
        """
        Generate practice questions for a given topic.
        
        Args:
            topic: Topic to generate questions for
            difficulty: Difficulty level (easy, medium, hard)
            num_questions: Number of questions to generate
            context: Additional context or study material
            
        Returns:
            List[Dict[str, Any]]: List of practice questions with answers
        """
        prompt = f"""
        Generate {num_questions} {difficulty} difficulty practice questions about {topic}.
        
        Context: {context}
        
        For each question, provide:
        1. A clear, well-formulated question
        2. Multiple choice options (A, B, C, D)
        3. The correct answer
        4. A brief explanation of why the answer is correct
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "question": "Question text here",
                "options": {{
                    "A": "Option A",
                    "B": "Option B", 
                    "C": "Option C",
                    "D": "Option D"
                }},
                "correct_answer": "A",
                "explanation": "Explanation of why this answer is correct"
            }}
        ]
        
        Make sure the questions are relevant to the topic and appropriate for {difficulty} difficulty level.
        """
        
        response_text = self.generate_text(prompt, max_tokens=2000, temperature=0.7)
        
        if not response_text:
            logger.error("Failed to generate practice questions")
            return []
        
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                logger.info(f"Generated {len(questions)} practice questions for topic: {topic}")
                return questions
            else:
                logger.warning("No valid JSON found in Gemini response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse practice questions JSON: {e}")
            return []
    
    def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Optional[str]: Generated summary or None if failed
        """
        prompt = f"""
        Please provide a concise summary of the following text in {max_length} words or less:
        
        {text}
        
        Focus on the key points and main ideas.
        """
        
        summary = self.generate_text(prompt, max_tokens=max_length, temperature=0.3)
        if summary:
            logger.info(f"Generated summary of {len(text)} characters")
        
        return summary
    
    def analyze_weak_areas(self, study_material: str, user_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user responses to identify weak areas.
        
        Args:
            study_material: The study material that was covered
            user_responses: List of user responses with questions and answers
            
        Returns:
            Dict[str, Any]: Analysis of weak areas and recommendations
        """
        # Create a summary of user performance
        correct_count = sum(1 for response in user_responses if response.get('correct', False))
        total_questions = len(user_responses)
        accuracy = correct_count / total_questions if total_questions > 0 else 0
        
        # Identify incorrect answers for analysis
        incorrect_questions = [
            response for response in user_responses 
            if not response.get('correct', False)
        ]
        
        prompt = f"""
        Analyze the following study session to identify weak areas and provide recommendations:
        
        Study Material: {study_material}
        
        User Performance:
        - Total Questions: {total_questions}
        - Correct Answers: {correct_count}
        - Accuracy: {accuracy:.1%}
        
        Incorrect Questions:
        {chr(10).join([f"- Q: {q.get('question', 'N/A')} | User Answer: {q.get('user_answer', 'N/A')} | Correct: {q.get('correct_answer', 'N/A')}" for q in incorrect_questions])}
        
        Please provide:
        1. A list of weak areas/topics that need more focus
        2. Specific recommendations for improvement
        3. Suggested study strategies
        4. Priority topics to review
        
        Format as JSON:
        {{
            "weak_areas": ["area1", "area2"],
            "recommendations": ["rec1", "rec2"],
            "study_strategies": ["strategy1", "strategy2"],
            "priority_topics": ["topic1", "topic2"],
            "overall_assessment": "brief assessment"
        }}
        """
        
        response_text = self.generate_text(prompt, max_tokens=1500, temperature=0.5)
        
        if not response_text:
            return {
                "weak_areas": [],
                "recommendations": ["Review the material more thoroughly"],
                "study_strategies": ["Practice with more questions"],
                "priority_topics": [],
                "overall_assessment": "Unable to analyze performance"
            }
        
        try:
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['accuracy'] = accuracy
                analysis['total_questions'] = total_questions
                analysis['correct_count'] = correct_count
                return analysis
            else:
                logger.warning("No valid JSON found in analysis response")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            return {}
    
    def generate_explanation(self, question: str, correct_answer: str, 
                           user_answer: str = None) -> Optional[str]:
        """
        Generate an explanation for a question and answer.
        
        Args:
            question: The question text
            correct_answer: The correct answer
            user_answer: The user's answer (optional)
            
        Returns:
            Optional[str]: Generated explanation or None if failed
        """
        if user_answer:
            prompt = f"""
            Question: {question}
            Correct Answer: {correct_answer}
            User's Answer: {user_answer}
            
            Please provide a clear explanation of why the correct answer is right.
            If the user's answer was incorrect, explain why it's wrong and how to arrive at the correct answer.
            """
        else:
            prompt = f"""
            Question: {question}
            Correct Answer: {correct_answer}
            
            Please provide a clear explanation of why this answer is correct.
            Include the reasoning and any relevant concepts.
            """
        
        explanation = self.generate_text(prompt, max_tokens=800, temperature=0.4)
        return explanation


# Global Gemini client instance
gemini_client = GeminiClient()


def generate_practice_questions(topic: str, difficulty: str = "medium", 
                              num_questions: int = 5, context: str = "") -> List[Dict[str, Any]]:
    """
    Convenience function to generate practice questions.
    
    Args:
        topic: Topic to generate questions for
        difficulty: Difficulty level
        num_questions: Number of questions
        context: Additional context
        
    Returns:
        List[Dict[str, Any]]: List of practice questions
    """
    return gemini_client.generate_practice_questions(topic, difficulty, num_questions, context)


def analyze_weak_areas(study_material: str, user_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to analyze weak areas.
    
    Args:
        study_material: Study material covered
        user_responses: User responses to analyze
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    return gemini_client.analyze_weak_areas(study_material, user_responses) 