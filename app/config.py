import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from typing import TypeVar

_T = TypeVar('_T', bound='Config')

class Config:
    """Application configuration class"""
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'gemma:2b')
    OLLAMA_TEMPERATURE: float = float(os.getenv('OLLAMA_TEMPERATURE', 0.7))
    OLLAMA_TOP_P: float = float(os.getenv('OLLAMA_TOP_P', 0.9))
    OLLAMA_NUM_PREDICT: int = int(os.getenv('OLLAMA_NUM_PREDICT', 512))
    
    # Chat settings
    CHAT_MEMORY_SIZE: int = int(os.getenv('CHAT_MEMORY_SIZE', 10))
    MAX_STORED_IMAGES: int = int(os.getenv('MAX_STORED_IMAGES', 5))  # Maximum base64 images to keep in session
    
    # Database settings
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data/chathistory.db')
    DATABASE_TABLE_NAME: str = os.getenv('DATABASE_TABLE_NAME', 'message_store')
    
    # Streamlit settings
    STREAMLIT_SERVER_PORT: int = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
    
    # Image generation settings
    IMAGE_MODEL: str = os.getenv('IMAGE_MODEL', 'runwayml/stable-diffusion-v1-5')
    IMAGE_HEIGHT: int = int(os.getenv('IMAGE_HEIGHT', 512))
    IMAGE_WIDTH: int = int(os.getenv('IMAGE_WIDTH', 512))
    IMAGE_STEPS: int = int(os.getenv('IMAGE_STEPS', 20))  # Lower for faster generation
    IMAGE_GUIDANCE_SCALE: float = float(os.getenv('IMAGE_GUIDANCE_SCALE', 7.5))
    IMAGE_OUTPUT_DIR: str = os.getenv('IMAGE_OUTPUT_DIR', './data/generated_images')
    IMAGE_AUTO_LOAD: bool = os.getenv('IMAGE_AUTO_LOAD', 'true').lower() == 'true'  # Auto-load model on startup
    
    @classmethod
    def validate_config(cls: type[_T]) -> bool:
        """Validate configuration settings with robust error handling"""
        required_vars: list[str] = ['OLLAMA_BASE_URL', 'OLLAMA_MODEL']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        
        logger = logging.getLogger(__name__)
        logger.info("✅ Configuration validated successfully!")
        return True

# Initial validation when the module is loaded
# Ensure logger is available for the initial validation
import logging
logger = logging.getLogger(__name__)
try:
    Config.validate_config()
except ValueError as e:
    # Use logging instead of print for errors
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Configuration validation error: {e}", exc_info=True)
    # Optionally, exit if configuration is invalid
    # exit(1)