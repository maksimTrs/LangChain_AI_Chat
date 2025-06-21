# 🎨 Image Generation Feature Guide

## Quick Reference 🚀

```bash
# 🎮 GPU Users (RTX 4090, etc.)
docker-compose --profile gpu up --build

# 💻 CPU Users  
docker-compose up --build

# 🧪 Test setup (optional)
docker-compose run --rm app python setup_image_generation.py
```

## Overview

This project now includes **local image generation** using Stable Diffusion models from Hugging Face. Generate high-quality images directly in your chat interface without needing external APIs or services.

## 🚀 Quick Start

### 1. Setup (One-time)

**For GPU users (RTX 4090, RTX 3060, etc.):**
```bash
# Use GPU profile for best performance
docker-compose --profile gpu up --build
```

**For CPU-only users:**
```bash
# Use default (CPU) profile
docker-compose up --build
```

**Optional**: Test setup before starting:
```bash
# Only if you want to verify setup first
docker-compose run --rm app python setup_image_generation.py
```

### 2. Using Image Generation

1. **Load the Model**: In the sidebar, click "🔄 Load Image Model"
2. **Generate Images**: In chat, use commands like:
   - `generate image of a sunset over mountains`
   - `create picture of a cat wearing a hat`
   - `draw a futuristic city`
   - `illustrate a peaceful garden`

### 3. Download Images

- Images appear directly in the chat
- Click "📥 Download Image" to save locally
- Images are also saved in `./data/generated_images/`

## 🔧 Configuration

### Environment Variables

You can customize image generation by setting these environment variables:

```bash
# Image generation settings
IMAGE_MODEL=runwayml/stable-diffusion-v1-5  # HuggingFace model ID
IMAGE_HEIGHT=512                              # Image height in pixels
IMAGE_WIDTH=512                               # Image width in pixels  
IMAGE_STEPS=20                                # Number of inference steps
IMAGE_GUIDANCE_SCALE=7.5                      # How closely to follow prompt
IMAGE_OUTPUT_DIR=./data/generated_images      # Where to save images
```

### Supported Models

The system works with any Stable Diffusion model from Hugging Face:

| Model | Description | VRAM Required |
|-------|-------------|---------------|
| `runwayml/stable-diffusion-v1-5` | **Recommended** - Best balance of quality and speed | ~4GB |
| `stabilityai/stable-diffusion-2-1` | Higher quality, newer model | ~5GB |
| `stabilityai/stable-diffusion-xl-base-1.0` | Highest quality, larger images | ~8GB |

## 💻 System Requirements

### Minimum Requirements
- **RAM**: 8GB+ system RAM
- **Storage**: 5GB+ free space (for model downloads)
- **Python**: 3.9+

### Recommended (GPU)
- **GPU**: NVIDIA with 4GB+ VRAM
- **CUDA**: Compatible CUDA installation
- **RAM**: 16GB+ system RAM

### CPU-Only Mode
- Works but **much slower** (2-10 minutes per image)
- Reduce image size to 256x256 for faster generation
- Use fewer steps (10-15) for speed

## 🐳 Docker Configuration

### Single File with Profiles 🎯

We use **Docker Compose profiles** for clean GPU/CPU switching in one file:

**For GPU Users (RTX 4090, etc.):**
```bash
# Use GPU profile - enables NVIDIA GPU acceleration
docker-compose --profile gpu up --build
```

**For CPU Users:**
```bash
# Use default profile - CPU-only mode
docker-compose up --build
```

**Prerequisites for GPU profile:**
1. NVIDIA GPU (GTX/RTX series)  
2. NVIDIA Docker runtime installed
3. nvidia-container-toolkit installed

**⚠️ Important**: The GPU profile will **fail with an error** if NVIDIA Docker runtime is not installed.

**Need GPU setup help?** Install NVIDIA Container Toolkit:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test: docker run --rm --gpus all nvidia/cuda:11.0-base-ubuntu20.04 nvidia-smi
```

## 🎯 Usage Examples

### Basic Commands
```
generate image of a red sports car
create picture of a mountain landscape
draw a cartoon robot
illustrate a cozy coffee shop
```

### Advanced Prompts
```
generate image of a photorealistic portrait of a woman with blue eyes, professional lighting, high detail
create picture of a fantasy castle on a floating island, magical atmosphere, sunset lighting
draw a cyberpunk city street with neon lights, rain, futuristic cars
```

## 🛠️ Troubleshooting

### Common Issues

**1. "Image generation model not loaded"**
- Click "🔄 Load Image Model" in the sidebar
- Wait for the model to download (first time only)

**2. "CUDA out of memory"**
- Click "🧹 Clear GPU Memory" in sidebar
- Reduce image size or steps in config
- Close other GPU-intensive applications

**3. Very slow generation**
- You're likely using CPU mode
- Consider getting a GPU or reducing image size
- Use fewer steps (10-15) for faster generation

**4. Poor image quality**
- Increase the number of steps (30-50)
- Use more descriptive prompts
- Try different models

### Performance Tips

**🎮 GPU Users (RTX 4090, etc.):**
- Monitor VRAM usage in sidebar
- Use "Clear GPU Memory" if needed
- Higher steps (30-50) = better quality
- Try larger images (1024x1024) with high-end GPUs

**💻 CPU Users:**
- Use smaller images (256x256 or 384x384)
- Reduce steps to 10-15 for speed
- Be patient - CPU generation takes 2-10 minutes

## 📝 Technical Details

### Architecture

The image generation system consists of:

1. **ImageGenerator Class** (`app/image_generator.py`)
   - Handles model loading and image generation
   - Optimizes memory usage
   - Manages device selection (GPU/CPU)

2. **Streamlit Integration** (`main.py`)
   - Detects image generation requests in chat
   - Displays generated images
   - Provides download functionality

3. **Configuration System** (`app/config.py`)
   - Centralizes all image generation settings
   - Allows environment variable customization

### Memory Management

- **GPU Memory**: Automatic slicing and CPU offloading
- **Model Caching**: Uses Streamlit's caching for efficiency
- **Memory Cleanup**: Manual GPU memory clearing available

### File Organization

```
data/
├── generated_images/     # All generated images
├── chathistory.db       # Chat history database
└── ...

app/
├── image_generator.py   # Image generation logic
├── config.py           # Configuration with image settings
├── chatbot.py          # Chat functionality
└── ...
```

## 🔐 Privacy & Security

- **100% Local**: No data sent to external services
- **No API Keys**: No external API dependencies
- **Offline Capable**: Works without internet (after initial model download)
- **Your Data**: All images and chats stay on your machine

## 🆚 Comparison with Original Instructions

### What We Fixed:

1. **✅ Docker Integration**: Replaced venv with Docker-based setup
2. **✅ UI Integration**: Full Streamlit chat interface integration
3. **✅ Memory Optimization**: Added GPU memory management
4. **✅ Error Handling**: Comprehensive error handling and user feedback
5. **✅ File Management**: Automatic file organization and download
6. **✅ Device Detection**: Smart GPU/CPU detection and optimization

### What We Improved:

1. **Better UX**: Seamless chat interface vs standalone script
2. **Configuration**: Environment variable configuration
3. **Performance**: Optimized for Docker containers
4. **Monitoring**: Real-time device and memory monitoring
5. **Flexibility**: Support for multiple models and settings

## 🎉 Enjoy Creating!

You now have a complete local image generation system integrated with your AI chat! The setup addresses all the concerns from the original instructions and provides a much more user-friendly experience.

Happy generating! 🎨✨ 