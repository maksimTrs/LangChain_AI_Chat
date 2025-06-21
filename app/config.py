import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Ollama settings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma:2b')
    OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', 0.7))
    OLLAMA_TOP_P = float(os.getenv('OLLAMA_TOP_P', 0.9))
    OLLAMA_NUM_PREDICT = int(os.getenv('OLLAMA_NUM_PREDICT', 512))
    
    # Chat settings
    CHAT_MEMORY_SIZE = int(os.getenv('CHAT_MEMORY_SIZE', 10))
    MAX_STORED_IMAGES = int(os.getenv('MAX_STORED_IMAGES', 5))  # Maximum base64 images to keep in session
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data/chathistory.db')
    DATABASE_TABLE_NAME = os.getenv('DATABASE_TABLE_NAME', 'message_store')
    
    # Streamlit settings
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
    
    # Image generation settings
    IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'runwayml/stable-diffusion-v1-5')
    IMAGE_HEIGHT = int(os.getenv('IMAGE_HEIGHT', 512))
    IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', 512))
    IMAGE_STEPS = int(os.getenv('IMAGE_STEPS', 20))  # Lower for faster generation
    IMAGE_GUIDANCE_SCALE = float(os.getenv('IMAGE_GUIDANCE_SCALE', 7.5))
    IMAGE_OUTPUT_DIR = os.getenv('IMAGE_OUTPUT_DIR', './data/generated_images')
    IMAGE_AUTO_LOAD = os.getenv('IMAGE_AUTO_LOAD', 'true').lower() == 'true'  # Auto-load model on startup
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings with robust error handling"""
        required_vars = ['OLLAMA_BASE_URL', 'OLLAMA_MODEL']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Configuration validated successfully!")
        return True

# Initial validation when the module is loaded
try:
    Config.validate_config()
except ValueError as e:
    print(e)
    # Optionally, exit if configuration is invalid
    # exit(1)