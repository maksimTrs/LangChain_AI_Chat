import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b-q4_K_M')
    CHAT_MEMORY_SIZE = int(os.getenv('CHAT_MEMORY_SIZE', '10'))
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        required_vars = ['OLLAMA_BASE_URL', 'OLLAMA_MODEL']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return True