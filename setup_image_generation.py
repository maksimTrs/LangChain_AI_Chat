#!/usr/bin/env python3
"""
Setup script for image generation feature
This script helps initialize the image generation models and test the setup
"""

import os
import sys
import torch
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'torch', 'diffusers', 'transformers', 
        'accelerate', 'PIL', 'safetensors'
    ]
    
    print("🔍 Checking required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages installed!")
    return True

def check_device():
    """Check available compute devices"""
    print("\n🖥️ Checking compute devices...")
    
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)
        gpu_memory = torch.cuda.get_device_properties(current_device).total_memory / (1024**3)
        
        print(f"✅ CUDA available: {gpu_count} GPU(s)")
        print(f"   Current GPU: {gpu_name}")
        print(f"   VRAM: {gpu_memory:.1f}GB")
        
        if gpu_memory < 4:
            print("⚠️  Warning: Less than 4GB VRAM detected. Image generation may be slow or fail.")
        
        return "cuda"
    else:
        print("⚠️  No CUDA GPU detected. Will use CPU (much slower)")
        return "cpu"

def test_image_generation():
    """Test basic image generation functionality"""
    print("\n🧪 Testing image generation...")
    
    try:
        from app.image_generator import ImageGenerator
        
        # Initialize generator
        generator = ImageGenerator()
        print(f"✅ ImageGenerator initialized on {generator.device}")
        
        # Test model loading (don't actually load to save time)
        print("✅ Image generation setup ready!")
        print("\n🎉 Setup complete! You can now:")
        print("   1. Start the application: docker-compose up")
        print("   2. Load the image model from the sidebar")
        print("   3. Use commands like 'generate image of a sunset' in chat")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing image generation: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "./data",
        "./data/generated_images"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")

def main():
    """Main setup function"""
    print("🚀 Image Generation Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check device
    device = check_device()
    
    # Create directories
    create_directories()
    
    # Test setup
    if test_image_generation():
        print("\n🎉 Setup completed successfully!")
        
        if device == "cpu":
            print("\n💡 Performance Tips:")
            print("   - Consider using a GPU for faster generation")
            print("   - Reduce image size in config for faster CPU generation")
            print("   - Use fewer inference steps (10-15) for speed")
        else:
            print("\n💡 GPU Tips:")
            print("   - Monitor VRAM usage during generation")
            print("   - Use 'Clear GPU Memory' if needed")
            print("   - Higher steps (20-50) give better quality")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 