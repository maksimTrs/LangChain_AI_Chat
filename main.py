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

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

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
        st.warning(f"CSS file not found at {file_path}")

load_css("static/style.css")

# --- Session State Initialization ---
def init_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = "User"
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = "Beginner"
    if "image_generator" not in st.session_state:
        st.session_state.image_generator = None

init_session_state()

# --- Chatbot Initialization ---
@st.cache_resource
def get_chatbot(_user_id, _role):
    """Initialize and cache the chatbot instance"""
    try:
        chatbot = OllamaChatbot(session_id=_user_id)
        chatbot.update_system_prompt(_role)
        return chatbot
    except Exception as e:
        st.error(f"❌ Failed to initialize chatbot: {str(e)}")
        st.info("Please make sure Ollama is running and the model is available.")
        st.stop()

# --- Image Generator Initialization ---
@st.cache_resource
def get_image_generator():
    """Initialize and cache the image generator instance"""
    generator = ImageGenerator()
    
    # Auto-load model if enabled in config
    if generator.config.IMAGE_AUTO_LOAD and not generator.is_model_loaded():
        print("🚀 Auto-loading image generation model...")
        # Show user-friendly message
        st.info("🚀 Loading Stable Diffusion model for image generation...")
        success = generator.load_model()
        if success:
            st.success("✅ Image generation ready!")
        else:
            st.error("❌ Failed to load image model")
    
    return generator

# --- UI Components ---
def render_sidebar(chatbot, image_generator):
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
                with st.spinner(f'🔄 Switching to {selected_model}...'):
                    if chatbot.switch_model(selected_model):
                        st.success(f"✅ Switched to {selected_model}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to switch to {selected_model}")
        else:
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
                with st.spinner("Loading image generation model..."):
                    if image_generator.load_model():
                        st.success("✅ Image model loaded!")
                        st.rerun()
                    else:
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
                    if image_generator.unload_model():
                        st.success("✅ Model unloaded!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to unload model")
            
            with col2:
                if st.button("🧹 Clear Memory", type="secondary"):
                    image_generator.clear_memory()
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
            chatbot.clear_conversation()
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🔄 Restart Chatbot", type="secondary"):
            st.cache_resource.clear()
            st.session_state.messages = []
            st.rerun()

def render_chat_history():
    """Render the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display image if it exists in the message
            if "image_data" in message:
                display_chat_image(message)

def display_chat_image(message: dict):
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
            except (FileNotFoundError, OSError):
                st.caption("💾 Image file moved or deleted")
        else:
            st.caption("💾 Image file not available")
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")

# Add session cleanup function
def cleanup_old_images_from_session(max_images: int = 10):
    """Clean up old base64 images from session state to prevent memory leaks"""
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
        "show me", "illustrate", "sketch", "render", "design"
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
                        cleanup_old_images_from_session(max_images=5)
                        
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