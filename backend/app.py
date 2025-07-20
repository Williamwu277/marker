import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.parser import Parser
from functools import wraps
from jose import jwt
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the PDF parser
file_parser = Parser()
ALLOWED_EXTENSIONS = {'pdf', 'png'}

# Auth0 Settings
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
ALGORITHMS = os.environ.get("ALGORITHMS", "RS256").split(",")

def get_file_extension(filename):
    if '.' not in filename:
        raise ValueError(f"Invalid file extension type: {filename}")
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

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
        
        # Validate inputs
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
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
            file_id = file_parser.upload_pdf(file_bytes, file_name)
        elif file_extension == 'png':
            file_id = file_parser.upload_png(file_bytes, file_name)
        
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
            'size': f'{file_data['size'] / 1024 / 1024} MB',
            'uploaded_at': file_data['uploaded_at'],
            'data': file_data['pages']
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
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
                'size': f'{file['size'] / 1024 / 1024} MB',
                'uploadedAt': file['uploaded_at'],
                'thumbnail': None
            }
            for file in files
        ]

        print(*files)

        return jsonify({
            'success': True,
            'files': files
        }), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    

# Auth0 Verification
def verify_jwt(token):
    jsonurl = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = jsonurl.json()
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        except Exception:
            return None

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', "").split("Bearer ")[-1]
        payload = verify_jwt(token)
        if not payload:
            return jsonify({"error": "Unauthorized"}), 401
        return f(payload, *args, **kwargs)
    return decorated

@app.route('/dashboard', methods=['GET']) # TODO: CHANGE THIS TO MATCH WTIH FRONTEND
@requires_auth
def protected_route(payload):
    return jsonify({
        "message": "Access granted!",
        "user": payload
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5099)
