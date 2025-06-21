import torch
import os
import time
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from diffusers import DiffusionPipeline, StableDiffusionPipeline
from PIL import Image
import streamlit as st
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# Forward declaration for type hint if StableDiffusionPipeline is not directly imported at top level for it
# However, it is imported, so direct usage is fine.
# StableDiffusionPipeline = "diffusers.StableDiffusionPipeline"

class ImageGenerator:
    """Image generation class using HuggingFace diffusers"""

    config: Config
    pipeline: Optional[StableDiffusionPipeline]
    device: Optional[str]
    model_loaded: bool
    output_dir: Path
    
    def __init__(self) -> None:
        self.config = Config()
        self.pipeline = None
        self.device = None # Will be set in _setup_device
        self.model_loaded = False
        
        # Setup output directory
        self.output_dir = Path(self.config.IMAGE_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize device
        self._setup_device()
        
    def _setup_device(self) -> None:
        """Setup and detect optimal device for image generation"""
        if torch.cuda.is_available():
            self.device = "cuda"
            # Check VRAM availability
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            logger.info(f"🎮 GPU detected: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
        else:
            self.device = "cpu"
            logger.info("💻 Using CPU for image generation (this will be slower)")
    
    @st.cache_resource
    def load_model(_self) -> bool:
        """Load and cache the image generation model"""
        if _self.model_loaded:
            # This message is fine, no need to change
            # logger.debug("Image model already loaded.")
            return True
            
        try:
            logger.info(f"🔄 Loading image model: {_self.config.IMAGE_MODEL} on device: {_self.device}")
            
            # Load model with appropriate settings for device
            if _self.device == "cuda":
                _self.pipeline = StableDiffusionPipeline.from_pretrained(
                    _self.config.IMAGE_MODEL,
                    torch_dtype=torch.float16,  # Use half precision for GPU
                    safety_checker=None,  # Disable for faster loading
                    requires_safety_checker=False
                )
                # Enable memory efficient attention for lower VRAM usage
                _self.pipeline.enable_attention_slicing()
                # Use model CPU offload to automatically manage GPU memory
                # This handles device placement automatically, so no manual .to() calls needed
                _self.pipeline.enable_model_cpu_offload()
            else:
                _self.pipeline = StableDiffusionPipeline.from_pretrained(
                    _self.config.IMAGE_MODEL,
                    torch_dtype=torch.float32,  # Use full precision for CPU
                    safety_checker=None,
                    requires_safety_checker=False
                )
                # For CPU-only, explicitly move the pipeline
                _self.pipeline = _self.pipeline.to(_self.device)
                
            _self.model_loaded = True
            
            logger.info(f"✅ Image model loaded successfully on {_self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load image model: {str(e)}", exc_info=True)
            _self.model_loaded = False
            return False
    
    def generate_image(
        self, 
        prompt: str, 
        negative_prompt: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        Generate an image from text prompt
        
        Returns:
            Tuple of (PIL Image, filepath) or (None, error_message)
        """
        if not self.model_loaded:
            if not self.load_model():
                return None, "Failed to load image generation model"
        
        try:
            # Use config defaults if not provided
            width = width or self.config.IMAGE_WIDTH
            height = height or self.config.IMAGE_HEIGHT
            steps = steps or self.config.IMAGE_STEPS
            guidance_scale = guidance_scale or self.config.IMAGE_GUIDANCE_SCALE
            
            # Set seed for reproducibility if provided
            if seed is not None:
                torch.manual_seed(seed)
            
            logger.info(f"🎨 Generating image with prompt: '{prompt[:50]}...' on device {self.device}")
            start_time = time.time()
            
            # Generate image
            with torch.autocast(self.device if self.device == "cuda" else "cpu"):
                result = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=steps,
                    guidance_scale=guidance_scale,
                    num_images_per_prompt=1
                )
                
            image = result.images[0]
            generation_time = time.time() - start_time
            
            # Save image with unique filename
            filename = self._generate_filename(prompt)
            filepath = self.output_dir / filename
            image.save(filepath, "PNG")
            
            logger.info(f"✅ Image generated in {generation_time:.2f}s: {filename}")
            return image, str(filepath)
            
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return None, error_msg
    
from typing import Dict, Any # Add Dict, Any

# ... (other imports)

# ... (inside ImageGenerator class)
    def _generate_filename(self, prompt: str) -> str:
        """Generate a unique filename based on prompt and timestamp"""
        # Create hash of prompt for uniqueness
        prompt_hash: str = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp: int = int(time.time())
        
        # Clean prompt for filename (take first 30 chars, remove special characters)
        clean_prompt: str = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_prompt = clean_prompt.replace(' ', '_')
        
        return f"{clean_prompt}_{prompt_hash}_{timestamp}.png"
    
    def is_model_loaded(self) -> bool:
        """Check if the model is loaded and ready"""
        return self.model_loaded
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the device being used"""
        info: Dict[str, Any] = {
            "device": self.device,
            "model_loaded": self.model_loaded,
            "output_dir": str(self.output_dir)
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB",
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / (1024**3):.1f}GB",
                "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0) / (1024**3):.1f}GB"
            })
        
        return info
    
    def clear_memory(self) -> None:
        """Clear GPU memory if using CUDA"""
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("🧹 GPU memory cleared")
    
    def unload_model(self) -> bool:
        """Properly unload the model and clear memory"""
        try:
            if self.model_loaded and self.pipeline is not None:
                # Clear the pipeline
                del self.pipeline
                self.pipeline = None
                self.model_loaded = False
                
                # Clear GPU memory
                self.clear_memory()
                
                # Clear Streamlit cache
                if hasattr(st, 'cache_resource'):
                    st.cache_resource.clear() # This clears all resources, be cautious
                    logger.info("Cleared all Streamlit cache resources during image model unload.")
                
                logger.info("🧹 Image model unloaded successfully")
                return True
            logger.info("Attempted to unload model, but no model was loaded or pipeline was None.")
            return True
        except Exception as e:
            logger.error(f"❌ Error unloading model: {str(e)}", exc_info=True)
            return False
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.unload_model()
        except Exception:
            pass  # Ignore errors during cleanup 