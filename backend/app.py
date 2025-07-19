"""
Main Flask application for Study Space backend.
Provides API endpoints for video, note, and worksheet processing.
"""

import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config.config import Config
from services.video_service import video_service
from services.note_service import note_service
from services.worksheet_service import worksheet_service
from services.review_service import review_service
from services.practice_service import practice_service

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Enable CORS
CORS(app)

# Ensure upload folder exists
Config.ensure_upload_folder()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Study Space Backend',
        'version': '1.0.0'
    })


# Video endpoints
@app.route('/upload/video', methods=['POST'])
def upload_video():
    """Upload and process a video file."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        
        result = video_service.upload_and_process_video(file, title, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in upload_video: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/video/summary/<video_id>', methods=['GET'])
def get_video_summary(video_id):
    """Get summary for a processed video."""
    try:
        result = video_service.get_video_summary(video_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_video_summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/video/segments/<video_id>', methods=['GET'])
def get_video_segments(video_id):
    """Get segments for a processed video."""
    try:
        result = video_service.get_video_segments(video_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_video_segments: {e}")
        return jsonify({'error': str(e)}), 500


# Note endpoints
@app.route('/upload/notes', methods=['POST'])
def upload_notes():
    """Upload and process a PDF notes file."""
    try:
        if 'notes' not in request.files:
            return jsonify({'error': 'No notes file provided'}), 400
        
        file = request.files['notes']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        
        result = note_service.upload_and_process_notes(file, title, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in upload_notes: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/notes/statistics', methods=['POST'])
def get_note_statistics():
    """Get statistics for a PDF notes file."""
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path:
            return jsonify({'error': 'PDF path not provided'}), 400
        
        result = note_service.get_note_statistics(pdf_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_note_statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/notes/search', methods=['POST'])
def search_notes():
    """Search notes by topic."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        user_id = data.get('user_id')
        max_results = data.get('max_results', 10)
        
        if not topic:
            return jsonify({'error': 'Topic not provided'}), 400
        
        result = note_service.search_notes_by_topic(topic, user_id, max_results)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in search_notes: {e}")
        return jsonify({'error': str(e)}), 500


# Worksheet endpoints
@app.route('/upload/worksheet', methods=['POST'])
def upload_worksheet():
    """Upload and process a PDF worksheet file."""
    try:
        if 'worksheet' not in request.files:
            return jsonify({'error': 'No worksheet file provided'}), 400
        
        file = request.files['worksheet']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        
        result = worksheet_service.upload_and_process_worksheet(file, title, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in upload_worksheet: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/worksheet/questions', methods=['POST'])
def get_worksheet_questions():
    """Get questions from a worksheet."""
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path:
            return jsonify({'error': 'PDF path not provided'}), 400
        
        result = worksheet_service.get_worksheet_questions(pdf_path)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_worksheet_questions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/worksheet/question/<int:question_index>', methods=['POST'])
def get_worksheet_question(question_index):
    """Get a specific question from a worksheet."""
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path:
            return jsonify({'error': 'PDF path not provided'}), 400
        
        result = worksheet_service.get_question_by_index(pdf_path, question_index)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error in get_worksheet_question: {e}")
        return jsonify({'error': str(e)}), 500


# Review endpoints
@app.route('/review/question', methods=['POST'])
def get_related_content():
    """Get related content for a question."""
    try:
        data = request.get_json()
        question_text = data.get('question_text')
        user_id = data.get('user_id')
        max_results = data.get('max_results', 10)
        content_types = data.get('content_types')
        
        if not question_text:
            return jsonify({'error': 'Question text not provided'}), 400
        
        result = review_service.get_related_content(question_text, user_id, max_results, content_types)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in get_related_content: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/review/comprehensive', methods=['POST'])
def get_comprehensive_review():
    """Get comprehensive review for a question."""
    try:
        data = request.get_json()
        question_text = data.get('question_text')
        user_id = data.get('user_id')
        
        if not question_text:
            return jsonify({'error': 'Question text not provided'}), 400
        
        result = review_service.get_comprehensive_review(question_text, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in get_comprehensive_review: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/review/search', methods=['POST'])
def search_content():
    """Search for content by topic."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        user_id = data.get('user_id')
        max_results = data.get('max_results', 15)
        
        if not topic:
            return jsonify({'error': 'Topic not provided'}), 400
        
        result = review_service.search_by_topic(topic, user_id, max_results)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in search_content: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/review/recommendations', methods=['POST'])
def get_study_recommendations():
    """Get study recommendations for a question."""
    try:
        data = request.get_json()
        question_text = data.get('question_text')
        user_id = data.get('user_id')
        
        if not question_text:
            return jsonify({'error': 'Question text not provided'}), 400
        
        result = review_service.get_study_recommendations(question_text, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in get_study_recommendations: {e}")
        return jsonify({'error': str(e)}), 500


# Practice endpoints
@app.route('/practice/generate', methods=['POST'])
def generate_practice():
    """Generate practice questions."""
    try:
        data = request.get_json()
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'medium')
        num_questions = data.get('num_questions', 5)
        context = data.get('context', '')
        user_id = data.get('user_id')
        
        if not topic:
            return jsonify({'error': 'Topic not provided'}), 400
        
        result = practice_service.generate_practice_questions(
            topic, difficulty, num_questions, context, user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in generate_practice: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/practice/weak-areas', methods=['POST'])
def generate_weak_area_questions():
    """Generate questions from weak areas."""
    try:
        data = request.get_json()
        weak_areas = data.get('weak_areas', [])
        study_material = data.get('study_material', '')
        user_id = data.get('user_id')
        
        if not weak_areas:
            return jsonify({'error': 'Weak areas not provided'}), 400
        
        result = practice_service.generate_questions_from_weak_areas(
            weak_areas, study_material, user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in generate_weak_area_questions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/practice/analyze', methods=['POST'])
def analyze_responses():
    """Analyze user responses to practice questions."""
    try:
        data = request.get_json()
        user_responses = data.get('user_responses', [])
        study_material = data.get('study_material', '')
        
        if not user_responses:
            return jsonify({'error': 'User responses not provided'}), 400
        
        result = practice_service.analyze_user_responses(user_responses, study_material)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in analyze_responses: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/practice/explanation', methods=['POST'])
def generate_explanation():
    """Generate explanation for a question."""
    try:
        data = request.get_json()
        question = data.get('question')
        correct_answer = data.get('correct_answer')
        user_answer = data.get('user_answer')
        
        if not question or not correct_answer:
            return jsonify({'error': 'Question and correct answer required'}), 400
        
        result = practice_service.generate_explanation(question, correct_answer, user_answer)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in generate_explanation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/practice/session', methods=['POST'])
def create_practice_session():
    """Create a comprehensive practice session."""
    try:
        data = request.get_json()
        topics = data.get('topics', [])
        difficulty = data.get('difficulty', 'medium')
        num_questions_per_topic = data.get('num_questions_per_topic', 3)
        user_id = data.get('user_id')
        
        if not topics:
            return jsonify({'error': 'Topics not provided'}), 400
        
        result = practice_service.create_practice_session(
            topics, difficulty, num_questions_per_topic, user_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in create_practice_session: {e}")
        return jsonify({'error': str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    return jsonify({'error': 'File too large'}), 413


if __name__ == '__main__':
    # Validate configuration
    if not Config.validate_config():
        logger.warning("Some API keys are missing. Some features may not work properly.")
    
    # Start the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=Config.DEBUG
    ) 