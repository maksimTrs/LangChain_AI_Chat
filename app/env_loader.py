from dotenv import load_dotenv
import os

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv('.env')
    
def get_env_variable(key, default=None):
    """Get environment variable with optional default value"""
    return os.getenv(key, default)

def print_env_variable(key):
    """Print environment variable value for debugging"""
    value = os.getenv(key)
    if value:
        print(f"{key}: {value}")
    else:
        print(f"{key}: Not found")

if __name__ == "__main__":
    # Example usage
    load_environment()
    print_env_variable("LANGSMITH_API_KEY")