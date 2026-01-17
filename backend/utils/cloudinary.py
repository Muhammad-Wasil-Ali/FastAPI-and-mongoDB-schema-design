# config/cloudinary_config.py
import cloudinary
import os
from dotenv import load_dotenv

load_dotenv()

def configure_cloudinary():
    """Configure Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUD_NAME"),
        api_key=os.getenv("CLOUD_API_KEY"),
        api_secret=os.getenv("CLOUD_SECRET"),
        secure=True  # Use HTTPS
    )
    
    # Verify configuration
    config = cloudinary.config()
    print("✅ Cloudinary configured successfully")
    print(f"   Cloud Name: {config.cloud_name}")
    print(f"   API Key: {config.api_key}")
    return config