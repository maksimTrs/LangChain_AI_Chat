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
    
    # Streamlit settings
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', 8501))
    
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