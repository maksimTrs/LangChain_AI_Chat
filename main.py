import streamlit as st
from app.chatbot import OllamaChatbot
from app.config import Config
import asyncio
import uuid
import nest_asyncio

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

# --- UI Components ---
def render_sidebar(chatbot):
    """Render the sidebar UI components"""
    with st.sidebar:
        st.header("🛠️ Configuration")
        
        # User identification
        st.subheader("👤 User Settings")
        if "user_id" not in st.session_state:
            st.session_state.user_id = "User"
        
        user_id = st.text_input(
            "Enter your name:",
            value=st.session_state.user_id,
            key="user_id_input",
            help="Your name for session identification"
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

def handle_chat_input(chatbot):
    """Handle user chat input and generate response"""
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
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
    st.markdown('<h1 class="main-header">🤖 AI Chatbot with Ollama & LangChain</h1>', unsafe_allow_html=True)
    
    # Get chatbot with user ID and role
    chatbot = get_chatbot(st.session_state.user_id, st.session_state.selected_role)
    
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = chatbot.get_chat_history()

    render_sidebar(chatbot)
    render_chat_history()
    
    # Handle chat input (now synchronous)
    handle_chat_input(chatbot)
    
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