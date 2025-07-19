"""
Configuration module for Study Space backend.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""
    
    # API Keys
    TWELVE_LABS_API_KEY: str = os.getenv('TWELVE_LABS_API_KEY', '')
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    
    # Flask Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Vector Database Configuration
    VECTOR_DIMENSION: int = int(os.getenv('VECTOR_DIMENSION', '768'))
    FAISS_INDEX_PATH: str = os.getenv('FAISS_INDEX_PATH', './data/faiss_index')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Allowed file extensions
    ALLOWED_VIDEO_EXTENSIONS: set = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    ALLOWED_PDF_EXTENSIONS: set = {'pdf'}
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_keys = ['TWELVE_LABS_API_KEY', 'GEMINI_API_KEY']
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"Warning: Missing required API keys: {missing_keys}")
            return False
        
        return True
    
    @classmethod
    def get_upload_path(cls, filename: str) -> str:
        """
        Get the full path for uploaded files.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            str: Full path to the uploaded file
        """
        return os.path.join(cls.UPLOAD_FOLDER, filename)
    
    @classmethod
    def ensure_upload_folder(cls) -> None:
        """Ensure the upload folder exists."""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.FAISS_INDEX_PATH), exist_ok=True) 