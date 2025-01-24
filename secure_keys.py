import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key():
    """
    Retrieve OpenAI API key from environment variable.
    
    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    return api_key

def validate_api_key(key):
    """
    Validate the format of the OpenAI API key.
    
    Args:
        key (str): API key to validate
    
    Returns:
        bool: True if key is valid, False otherwise
    """
    return isinstance(key, str) and key.startswith("sk-") and len(key) > 40
