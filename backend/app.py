from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.parser import Parser
from services.embedding.chunking import NoteClusterer
from services.embedding.faiss_longchain_indexing import FAISS_INDEX as FAISSIndexer
from services.embedding.twelvelabs_embedding import TwelveLabsEmbeddings



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the PDF parser
file_parser = Parser()
ALLOWED_EXTENSIONS = {'pdf', 'png'}

# Initialize text chunker and FAISS indexer
text_chunker = NoteClusterer()
faiss_index = FAISSIndexer()
embedder = TwelveLabsEmbeddings()

def get_file_extension(filename):
    if '.' not in filename:
        raise ValueError(f"Invalid file extension type: {filename}")
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def is_video_file(filename):
    video_extensions = {'mp4'}
    return get_file_extension(filename) in video_extensions

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    Endpoint to upload and process a PDF or PNG file
    Expects: multipart/form-data with 'file' and 'file_name' fields
    Returns: JSON response with success status, message, and generated ID
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_name = request.form.get('file_name')
        file_usage = request.form.get('file_usage')
        
        # Validate inputs
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file_usage or file_usage != "worksheet":
            return jsonify({'error': 'File usage needs to be "worksheet"'}), 400
        
        if not file_name:
            return jsonify({'error': 'File name is required'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and PNG files are allowed'}), 400
        
        # Read file bytes
        file_bytes = file.read()
        
        # Process the PDF or PNG using the worksheet_parsing module
        file_id = None
        file_extension = get_file_extension(file_name)
        if file_extension == 'pdf':
            file_id = file_parser.upload_pdf(file_bytes, file_name, file_usage)
        elif file_extension == 'png':
            file_id = file_parser.upload_png(file_bytes, file_name, file_usage)
        
        return jsonify({
            'success': True,
            'message': f'PDF "{file_name}" uploaded and processed successfully',
            'file_name': file_name,
            'file_id': file_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/get_file', methods=['POST'])
def get_file():
    """
    Endpoint to retrieve processed PDF or PNG data
    Expects: JSON body with 'file_id' field
    Returns: JSON response with file data or error message
    """
    try:
        # Get PDF ID from request body
        data = request.get_json()
        if not data or 'file_id' not in data:
            return jsonify({'error': 'File ID is required in request body'}), 400
        
        file_id = data['file_id']
        
        # Get the PDF data using the worksheet_parsing module
        file_data = file_parser.get_file(file_id)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'file_name': file_data['file_name'],
            'file_type': file_data['file_type'],
            'size': f'{round(file_data['size'] / 1024 / 1024, 2)} MB',
            'uploaded_at': file_data['uploaded_at'],
            'data': file_data['pages']
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/upload_notes', methods=['POST'])
def upload_notes():
    """
    Endpoint to upload a PDF and return extracted info as JSON.
    Expects: multipart/form-data with 'file' and 'file_name'
    Returns: JSON response with extracted info
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_name = request.form.get('file_name')
        file_usage = request.form.get('file_usage')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file_usage or file_usage != "notes":
            return jsonify({'error': 'File usage needs to be "notes"'}), 400

        if not file_name:
            return jsonify({'error': 'File name is required'}), 400

        if get_file_extension(file.filename) != 'pdf':
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        file_bytes = file.read()

        # Use your Parser to extract the info you want
        file_id = file_parser.upload_pdf(file_bytes, file_name, file_usage)
        file_path = file_parser.data[file_id]['temp_path']

        # CHUNK
        chunks = text_chunker.process_pdf(file_path=file_path)
        
        full_text = ""
        for chunk in chunks:
            full_text += chunk['page_text'] + " "
        faiss_index.add_text_chunks_to_index(chunks=chunks, file_path=file_path)
        file_data = file_parser.get_file(file_id)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'file_name': file_data['file_name'],
            'file_type': file_data['file_type'],
            'size': f'{file_data['size'] / 1024 / 1024} MB',
            'uploaded_at': file_data['uploaded_at'],
            'data': file_data['pages'],
            'text_summary': full_text,
            'file_usage': file_data['file_usage']
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    """
    Endpoint to upload a .mp4 video and store metadata.
    Expects: multipart/form-data with 'file' and 'file_name'
    Returns: JSON response with success status and file info
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        file_name = request.form.get('file_name')
        file_usage = request.form.get('file_usage')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file_usage or file_usage != "video":
            return jsonify({'error': 'File usage needs to be "video"'}), 400

        if not file_name:
            return jsonify({'error': 'File name is required'}), 400

        if get_file_extension(file.filename) != 'mp4':
            return jsonify({'error': 'Only MP4 video files are allowed'}), 400

        file_bytes = file.read()

        # Store using parser
        file_id = file_parser.upload_video(file_bytes, file_name, file_usage)
        file_data = file_parser.get_file(file_id)
        file_path = file_data['temp_path']

        # CHUNK
        doc_name = faiss_index.get_video_name(file_path=file_path)
        chunk_embeddings = embedder.embed_video(video=file_path)
        faiss_index.add_video_chunks_to_index(chunk_embeddings, file_path)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'file_name': file_data['file_name'],
            'file_type': file_data['file_type'],
            'size': f'{file_data['size'] / 1024 / 1024} MB',
            'uploaded_at': file_data['uploaded_at'],
            'data': file_data['pages'],
            'file_usage': file_data['file_usage']
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/get_all_files', methods=['GET'])
def get_all_files():
    """
    Endpoint to retrieve all files in the database
    Returns: JSON response with list of files
    """ 
    try:
        files = file_parser.get_all_files()

        files = [
            {
                'id': file['id'],
                'name': file['file_name'],
                'type': 'video' if file['file_type'] == 'video' else 'pdf' if file['file_type'] == 'pdf' else 'png',
                'size': f'{round(file['size'] / 1024 / 1024, 2)} MB',
                'uploadedAt': file['uploaded_at'],
                'thumbnail': None,
                'file_usage': file['file_usage']
            }
            for file in files
        ]

        print(*files)
        print(*files)

        return jsonify({
            'success': True,
            'files': files
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5099)
