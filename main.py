import streamlit as st
from app.chatbot import OllamaChatbot
from app.config import Config
from app.image_generator import ImageGenerator
import asyncio
import uuid
import nest_asyncio
import re
import time
import os
from PIL import Image

from typing import Optional, List, Dict, Any # Add necessary types

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# --- Setup Logging ---
# IMPORTANT: This should be one of the first imports and calls
import logging
from app.logging_config import setup_logging
setup_logging() # Initialize logging configuration
logger = logging.getLogger(__name__)


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Chatbot with Ollama",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Custom CSS ---
def load_css(file_path):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        logger.warning(f"CSS file not found at {file_path}. Skipping custom styles.")
        st.warning(f"CSS file not found at {file_path}")

load_css("static/style.css")

# --- Session State Initialization ---
def init_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id: str = str(uuid.uuid4())
    if "chatbot" not in st.session_state:
        st.session_state.chatbot: Optional[OllamaChatbot] = None
    if "messages" not in st.session_state:
        # Messages can contain text (role, content) or image data too
        st.session_state.messages: List[Dict[str, Any]] = []
    if "user_id" not in st.session_state:
        st.session_state.user_id: str = "User" # Default user ID
    if "selected_role" not in st.session_state:
        st.session_state.selected_role: str = "Beginner" # Default role
    if "image_generator" not in st.session_state:
        st.session_state.image_generator: Optional[ImageGenerator] = None

init_session_state()

# --- Chatbot Initialization ---
@st.cache_resource
def get_chatbot(_user_id: str, _role: str) -> OllamaChatbot:
    """Initialize and cache the chatbot instance"""
    try:
        logger.info(f"Attempting to initialize chatbot for user_id: {_user_id}, role: {_role}")
        chatbot = OllamaChatbot(session_id=_user_id)
        # update_system_prompt now logs success/failure internally
        if not chatbot.update_system_prompt(_role): # It returns bool
             logger.warning(f"Chatbot initialized but failed to set role: {_role} for user_id: {_user_id}")
        logger.info(f"Chatbot initialized successfully for user_id: {_user_id}")
        return chatbot
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot for user_id: {_user_id}: {str(e)}", exc_info=True)
        st.error(f"❌ Failed to initialize chatbot: {str(e)}")
        st.info("Please make sure Ollama is running and the model is available.")
        st.stop()

# --- Image Generator Initialization ---
@st.cache_resource
def get_image_generator() -> ImageGenerator:
    """Initialize and cache the image generator instance"""
    generator: ImageGenerator = ImageGenerator()
    
    # Auto-load model if enabled in config
    if generator.config.IMAGE_AUTO_LOAD and not generator.is_model_loaded():
        logger.info("🚀 Auto-loading image generation model as per config.")
        # Show user-friendly message
        st.info("🚀 Loading Stable Diffusion model for image generation...")
        # load_model now logs internally
        success = generator.load_model()
        if success:
            logger.info("✅ Image generation model auto-loaded successfully.")
            st.success("✅ Image generation ready!")
        else:
            logger.error("❌ Failed to auto-load image model.")
            st.error("❌ Failed to load image model")
    
    return generator

# --- UI Components ---
def render_sidebar(chatbot: OllamaChatbot, image_generator: ImageGenerator) -> None:
    """Render the sidebar UI components"""
    with st.sidebar:
        st.header("🛠️ Configuration")
        
        # User identification
        st.subheader("👤 User Settings")
        if "user_id" not in st.session_state:
            st.session_state.user_id = "User"
        
        user_id = st.text_input(
            "Enter name/sessionId:",
            value=st.session_state.user_id,
            key="user_id_input",
            help="Your name or session ID for conversation identification"
        )
        
        if user_id != st.session_state.user_id:
            st.session_state.user_id = user_id
            # Clear cache to reinitialize chatbot with new user
            st.cache_resource.clear()
            st.rerun()
        
        # Role selection for system prompt
        st.subheader("🎯 Response Style")
        role_options = ["Beginner", "Expert", "PhD"]
        if "selected_role" not in st.session_state:
            st.session_state.selected_role = "Beginner"
        
        selected_role = st.radio(
            "How detailed should the answers be?",
            role_options,
            index=role_options.index(st.session_state.selected_role),
            key="role_selector",
            help="Choose the complexity level of responses"
        )
        
        if selected_role != st.session_state.selected_role:
            st.session_state.selected_role = selected_role
            # Clear cache to reinitialize chatbot with new role
            st.cache_resource.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Model selection
        st.subheader("🤖 Model Selection")
        available_models = chatbot.get_available_models()
        
        if available_models:
            current_model = chatbot.config.OLLAMA_MODEL
            try:
                current_index = available_models.index(current_model)
            except ValueError:
                current_index = 0
            
            selected_model = st.selectbox(
                "Choose Model:",
                available_models,
                index=current_index,
                key="model_selector",
                help="Select an AI model to use for conversations"
            )
            
            if selected_model != current_model:
                logger.info(f"User selected new model: {selected_model}. Current: {current_model}")
                with st.spinner(f'🔄 Switching to {selected_model}...'):
                    # switch_model logs internally
                    if chatbot.switch_model(selected_model):
                        logger.info(f"Successfully switched model to {selected_model}")
                        st.success(f"✅ Switched to {selected_model}")
                        st.rerun()
                    else:
                        logger.error(f"Failed to switch model to {selected_model} in UI.")
                        st.error(f"❌ Failed to switch to {selected_model}")
        else:
            logger.warning("No models available from Ollama to display in sidebar.")
            st.warning("⚠️ No models available")
        
        st.markdown("---")
        
        # Model information
        st.write(f"**Current Model:** {chatbot.config.OLLAMA_MODEL}")
        st.write(f"**Memory Size:** {chatbot.config.CHAT_MEMORY_SIZE} messages")
        st.write(f"**Response Level:** {st.session_state.selected_role}")
        
        with st.expander("📊 Conversation Summary"):
            st.json(chatbot.get_conversation_summary())
            
        st.markdown("---")
        
        # Image generation settings
        st.subheader("🎨 Image Generation")
        
        # Load model button and status
        if not image_generator.is_model_loaded():
            st.info("🔄 Image model not loaded")
            if st.button("🔄 Load Image Model", type="primary"):
                    logger.info("User clicked 'Load Image Model'")
                with st.spinner("Loading image generation model..."):
                        # load_model logs internally
                    if image_generator.load_model():
                            logger.info("Image model loaded successfully by user action.")
                        st.success("✅ Image model loaded!")
                        st.rerun()
                    else:
                            logger.error("Failed to load image model by user action.")
                        st.error("❌ Failed to load image model")
        else:
            st.success("✅ Image model ready")
            
            # Show auto-load status
            if image_generator.config.IMAGE_AUTO_LOAD:
                st.caption("🚀 Auto-load enabled - model loads on startup")
            
            # Model management buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Unload Model", type="secondary"):
                    logger.info("User clicked 'Unload Model'")
                    # unload_model logs internally
                    if image_generator.unload_model():
                        logger.info("Image model unloaded successfully by user action.")
                        st.success("✅ Model unloaded!")
                        st.rerun()
                    else:
                        logger.error("Failed to unload image model by user action.")
                        st.error("❌ Failed to unload model")
            
            with col2:
                if st.button("🧹 Clear Memory", type="secondary"):
                    logger.info("User clicked 'Clear Memory' for image generator.")
                    image_generator.clear_memory() # clear_memory logs internally
                    st.success("GPU memory cleared!")
            
            # Image generation settings
            with st.expander("⚙️ Image Settings"):
                # Get device info
                device_info = image_generator.get_device_info()
                st.write(f"**Device:** {device_info['device']}")
                if device_info['device'] == 'cuda':
                    st.write(f"**GPU:** {device_info.get('gpu_name', 'N/A')}")
                    st.write(f"**VRAM:** {device_info.get('gpu_memory_total', 'N/A')}")
                
                st.write(f"**Model:** {image_generator.config.IMAGE_MODEL}")
                st.write(f"**Size:** {image_generator.config.IMAGE_WIDTH}x{image_generator.config.IMAGE_HEIGHT}")
                st.write(f"**Steps:** {image_generator.config.IMAGE_STEPS}")
        
        # Controls
        st.header("🎛️ Controls")
        if st.button("🗑️ Clear Conversation", type="secondary"):
            logger.info(f"User {st.session_state.user_id} clicked 'Clear Conversation'")
            chatbot.clear_conversation() # This logs internally
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🔄 Restart Chatbot", type="secondary"):
            logger.info(f"User {st.session_state.user_id} clicked 'Restart Chatbot'")
            st.cache_resource.clear()
            logger.info("Cleared all @st.cache_resource for chatbot restart.")
            st.session_state.messages = []
            # Also clear other relevant session state items if any were added that persist across chatbot instances
            # For example, if chatbot or image_generator instances were stored directly:
            if 'chatbot' in st.session_state:
                del st.session_state.chatbot
                logger.debug("Removed 'chatbot' from session_state.")
            if 'image_generator' in st.session_state: # Though image_generator is often independent of user_id
                del st.session_state.image_generator # This might be too aggressive if it's meant to persist globally
                logger.debug("Potentially removed 'image_generator' from session_state during chatbot restart.")
            st.rerun()

def render_chat_history() -> None:
    """Render the chat history"""
    # st.session_state.messages is List[Dict[str, Any]]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): # type: ignore # streamlit type hints might not be perfect for session_state structure
            st.markdown(message["content"]) # type: ignore
            
            # Display image if it exists in the message
            if "image_data" in message:
                display_chat_image(message)

def display_chat_image(message: Dict[str, Any]) -> None:
    """Consolidated image display logic for chat history"""
    try:
        import base64
        from PIL import Image
        import io
        
        # Decode base64 image data
        image_data = base64.b64decode(message["image_data"])
        image = Image.open(io.BytesIO(image_data))
        
        # Display image with proper caption at natural size (max 512px width)
        st.image(image, caption=f"Generated: {message.get('image_prompt', 'Image')}", width=512)
        
        # Add download button for historical images
        if "image_filepath" in message and os.path.exists(message["image_filepath"]):
            try:
                with open(message["image_filepath"], "rb") as file:
                    st.download_button(
                        label="📥 Download Image",
                        data=file.read(),
                        file_name=f"generated_image_{message.get('image_prompt', 'image').replace(' ', '_').replace('/', '_')}.png",
                        mime="image/png",
                        key=f"download_{hash(message['image_filepath'])}"  # Unique key for each download button
                    )
            except (FileNotFoundError, OSError) as e:
                logger.warning(f"Could not offer download for {message.get('image_filepath', 'N/A')}: {e}", exc_info=True)
                st.caption("💾 Image file moved or deleted")
        else:
            logger.debug(f"Image file not available or path not set for message: {message.get('image_prompt', 'N/A')}")
            st.caption("💾 Image file not available")
    except Exception as e:
        logger.error(f"Error displaying chat image for prompt {message.get('image_prompt', 'N/A')}: {str(e)}", exc_info=True)
        st.error(f"Error displaying image: {str(e)}")

# Add session cleanup function
def cleanup_old_images_from_session(max_images: int = None):
    """Clean up old base64 images from session state to prevent memory leaks"""
    if max_images is None:
        # Check if chatbot exists and is not None
        if "chatbot" in st.session_state and st.session_state.chatbot is not None:
            max_images = st.session_state.chatbot.config.MAX_STORED_IMAGES
        else:
            # Fall back to Config directly
            from app.config import Config
            config = Config()
            max_images = config.MAX_STORED_IMAGES
    
    if "messages" in st.session_state:
        image_messages = [msg for msg in st.session_state.messages if "image_data" in msg]
        
        # If we have too many images, remove base64 data from oldest ones
        if len(image_messages) > max_images:
            for msg in image_messages[:-max_images]:  # Keep only the last max_images
                if "image_data" in msg:
                    del msg["image_data"]  # Remove base64 data but keep metadata
                    msg["_image_cleaned"] = True  # Mark as cleaned for UI

def detect_image_request(prompt: str) -> bool:
    """Detect if the user is requesting image generation"""
    image_keywords = [
        "generate image", "create image", "make image", "draw", "paint", 
        "generate picture", "create picture", "make picture", "visualize",
        "show me", "illustrate", "sketch", "render", "design", "generate image of",
        "create image of", "make image of", "draw image", "paint image", "visualize image",
        "prepare image", "prepare picture", "generate an image", "generate a picture",
        "create an image", "create a picture"
    ]
    
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in image_keywords)

def extract_image_prompt(prompt: str) -> str:
    """Extract the actual image prompt from user input"""
    # Remove common prefixes
    prefixes_to_remove = [
        "generate image of", "create image of", "make image of", "draw",
        "generate picture of", "create picture of", "make picture of",
        "show me", "illustrate", "sketch", "render", "design", "paint"
    ]
    
    cleaned_prompt = prompt.lower()
    for prefix in prefixes_to_remove:
        if cleaned_prompt.startswith(prefix):
            cleaned_prompt = cleaned_prompt[len(prefix):].strip()
            break
    
    # Remove common words at the beginning
    cleaned_prompt = re.sub(r'^(a|an|the|some)\s+', '', cleaned_prompt)
    
    return cleaned_prompt if cleaned_prompt else prompt

def handle_chat_input(chatbot, image_generator):
    """Handle user chat input and generate response"""
    if prompt := st.chat_input("Type your message here... (Use 'generate image of...' for image creation)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Check if this is an image generation request
        if detect_image_request(prompt):
            if not image_generator.is_model_loaded():
                with st.chat_message("assistant"):
                    st.error("🚫 Image generation model not loaded. Please load it from the sidebar first.")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Image generation model not loaded. Please load it from the sidebar first."
                    })
                return
            
            # Generate image
            with st.chat_message("assistant"):
                with st.spinner("🎨 Generating image..."):
                    image_prompt = extract_image_prompt(prompt)
                    image, filepath = image_generator.generate_image(image_prompt)
                    
                    if image:
                        # Display the generated image using consolidated logic
                        st.image(image, caption=f"Generated: {image_prompt}", width=512)
                        
                        # Add download button with improved filename handling
                        safe_filename = image_prompt.replace(' ', '_').replace('/', '_')[:50]  # Limit filename length
                        with open(filepath, "rb") as file:
                            st.download_button(
                                label="📥 Download Image",
                                data=file.read(),
                                file_name=f"generated_{safe_filename}_{int(time.time())}.png",
                                mime="image/png"
                            )
                        
                        response_text = f"✅ Image generated successfully! Prompt: '{image_prompt}'"
                        st.markdown(response_text)
                        
                        # Store image data in session state (with cleanup to prevent memory leaks)
                        import base64
                        import io
                        
                        # Convert image to base64 for embedding in chat history (smaller size)
                        img_buffer = io.BytesIO()
                        # Resize image for storage to reduce memory usage
                        stored_image = image.copy()
                        if stored_image.size[0] > 512 or stored_image.size[1] > 512:
                            stored_image.thumbnail((512, 512), Image.Resampling.LANCZOS)
                        stored_image.save(img_buffer, format='PNG', optimize=True)
                        img_str = base64.b64encode(img_buffer.getvalue()).decode()
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text,
                            "image_data": img_str,
                            "image_prompt": image_prompt,
                            "image_filepath": filepath
                        })
                        
                        # Clean up old images to prevent memory bloat
                        cleanup_old_images_from_session()
                        
                    else:
                        error_msg = f"❌ Failed to generate image: {filepath}"  # filepath contains error message
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            # Handle normal chat
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    # Use asyncio.run with nest_asyncio support
                    async def stream_response():
                        nonlocal full_response
                        async for chunk in chatbot.chat(prompt):
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        return full_response
                    
                    # Run the async function
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Use nest_asyncio to handle nested loops
                            import nest_asyncio
                            nest_asyncio.apply()
                            full_response = asyncio.run(stream_response())
                        else:
                            full_response = asyncio.run(stream_response())
                    except RuntimeError:
                        # Fallback: create new event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        full_response = loop.run_until_complete(stream_response())
                        loop.close()
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# --- Main Application ---
def main():
    """Main Streamlit application"""
    st.markdown('<h1 class="main-header">🤖 AI Chatbot with Ollama & LangChain + Image Generation</h1>', unsafe_allow_html=True)
    
    # Get chatbot with user ID and role
    chatbot = get_chatbot(st.session_state.user_id, st.session_state.selected_role)
    
    # Get image generator (with auto-load)
    with st.spinner("🚀 Initializing AI services..."):
        image_generator = get_image_generator()
    
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = chatbot.get_chat_history()

    # Show welcome message if no chat history
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            welcome_msg = """
            👋 **Welcome to AI Chat with Image Generation!**
            
            🤖 **Chat Features:**
            - Ask questions and get AI-powered responses
            - Choose response complexity in the sidebar (Beginner/Expert/PhD)
            
            🎨 **Image Generation:**
            - Type commands like: `generate image of a sunset`
            - `create picture of a cat wearing a hat`
            - `draw a futuristic city`
            
            ⚙️ **Settings:** Customize everything in the sidebar
            
            *How can I help you today?*
            """
            st.markdown(welcome_msg)

    render_sidebar(chatbot, image_generator)
    render_chat_history()
    
    # Handle chat input with image generation support
    handle_chat_input(chatbot, image_generator)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>" 
        "Powered by LangChain 🦜🔗 + Ollama 🦙 + Streamlit ⚡ + SQLite 🗄️" 
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()