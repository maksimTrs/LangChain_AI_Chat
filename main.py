import streamlit as st
from app.chatbot import OllamaChatbot
from app.config import Config
import time

# Page configuration
st.set_page_config(
    page_title="AI Chatbot with Ollama",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    color: #000000 !important;
}
.user-message {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
    color: #000000 !important;
}
.assistant-message {
    background-color: #f3e5f5;
    border-left: 4px solid #9c27b0;
    color: #000000 !important;
}
.sidebar-info {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
/* Hide unwanted Streamlit elements */
.stSelectbox > div > div {
    background-color: transparent;
}
.stSelectbox > div > div > div {
    background-color: transparent !important;
}
/* Hide selectbox helper text and extra elements */
.stSelectbox > div[data-testid="stSelectbox"] > div:last-child {
    display: none;
}
/* Improve sidebar spacing */
.css-1d391kg {
    padding-top: 1rem;
}
/* Remove extra white space */
.stMarkdown {
    margin-bottom: 0.5rem;
}
/* Hide any white rows/fields */
.stSelectbox + div {
    display: none;
}
/* Target specific white elements */
[data-testid="stSelectbox"] + div[style*="background"] {
    display: none !important;
}
/* Hide empty sidebar-info divs */
.sidebar-info:empty {
    display: none !important;
}
/* Hide stMarkdown containers with empty sidebar-info */
.stMarkdown:has(.sidebar-info:empty) {
    display: none !important;
}
/* Alternative approach for browsers that don't support :has() */
div[data-testid="stMarkdownContainer"]:has(.sidebar-info:empty) {
    display: none !important;
}
/* Direct targeting of the problematic element */
.st-emotion-cache-1racx89:has(.sidebar-info:empty) {
    display: none !important;
}
/* Dark theme support */
@media (prefers-color-scheme: dark) {
    .user-message {
        background-color: #1e3a8a;
        color: #ffffff !important;
    }
    .assistant-message {
        background-color: #581c87;
        color: #ffffff !important;
    }
    .chat-message {
        color: #ffffff !important;
    }
}
/* Force text color for better visibility */
.chat-message strong {
    color: inherit !important;
}
.chat-message * {
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    """Initialize chatbot with error handling"""
    try:
        if 'chatbot' not in st.session_state:
            with st.spinner('🔄 Initializing AI Chatbot...'):
                st.session_state.chatbot = OllamaChatbot(session_id="streamlit_session")
                st.success("✅ Chatbot initialized successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize chatbot: {str(e)}")
        st.info("Please make sure Ollama is running and the model is available.")
        return False

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Chatbot with Ollama & LangChain</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Configuration")
        
        # Initialize chatbot
        if not initialize_chatbot():
            st.stop()
        
        chatbot = st.session_state.chatbot
        
        # Model selection
        st.subheader("🤖 Model Selection")
        available_models = chatbot.get_available_models()
        
        if available_models:
            current_model = Config.OLLAMA_MODEL
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
            
            # Switch model if selection changed
            if selected_model != current_model:
                with st.spinner(f'🔄 Switching to {selected_model}...'):
                    if chatbot.switch_model(selected_model):
                        st.success(f"✅ Switched to {selected_model}")
                        Config.OLLAMA_MODEL = selected_model
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to switch to {selected_model}")
        else:
            st.warning("⚠️ No models available")
        
        st.markdown("---")  # Add separator
        
        # Model information
        st.write(f"**Current Model:** {Config.OLLAMA_MODEL}")
        st.write(f"**Memory Size:** {Config.CHAT_MEMORY_SIZE} messages")
        
        # Conversation summary
        with st.expander("📊 Conversation Summary"):
            summary = chatbot.get_conversation_summary()
            st.json(summary)
        
        # Controls
        st.header("🎛️ Controls")
        
        if st.button("🗑️ Clear Conversation", type="secondary"):
            chatbot.clear_conversation()
            st.session_state.messages = []
            st.success("Conversation cleared!")
            st.rerun()
        
        if st.button("🔄 Restart Chatbot", type="secondary"):
            if 'chatbot' in st.session_state:
                del st.session_state.chatbot
            st.success("Chatbot will restart on next interaction")
            st.rerun()
    
    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Load existing chat history
        history = chatbot.get_chat_history()
        st.session_state.messages = history
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {content}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {content}</div>', 
                       unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {prompt}</div>', 
                   unsafe_allow_html=True)
        
        # Generate and display assistant response
        with st.spinner('🤔 Thinking...'):
            try:
                response = chatbot.chat(prompt)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display assistant response
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {response}</div>', 
                           unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Rerun to update the display
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>" 
        "Powered by LangChain 🦜🔗 + Ollama 🦙 + Streamlit ⚡" 
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()