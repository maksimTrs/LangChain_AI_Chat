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
}
.user-message {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}
.assistant-message {
    background-color: #f3e5f5;
    border-left: 4px solid #9c27b0;
}
.sidebar-info {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
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
        
        # Model information
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.write(f"**Current Model:** {Config.OLLAMA_MODEL}")
        st.write(f"**Memory Size:** {Config.CHAT_MEMORY_SIZE} messages")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Available models
        with st.expander("📋 Available Models"):
            models = chatbot.get_available_models()
            if models:
                for model in models:
                    st.write(f"• {model}")
            else:
                st.write("No models found")
        
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