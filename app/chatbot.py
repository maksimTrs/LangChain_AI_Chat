from langchain_ollama.llms import OllamaLLM
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from app.memory_manager import ChatMemoryManager
from app.config import Config
import requests
import time
from typing import Optional, Dict, Any, AsyncGenerator

class OllamaChatbot:
    """Main chatbot class with LangChain and Ollama integration"""
    
    def __init__(self):
        self.config = Config()
        self.memory_manager = ChatMemoryManager(
            memory_size=self.config.CHAT_MEMORY_SIZE
        )
        
        # Initialize Ollama LLM
        self.llm = None
        self.chain = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize Ollama LLM and conversation chain"""
        try:
            # Wait for Ollama to be ready
            self._wait_for_ollama()
            
            # Initialize LLM
            self.llm = OllamaLLM(
                base_url=self.config.OLLAMA_BASE_URL,
                model=self.config.OLLAMA_MODEL,
                temperature=self.config.OLLAMA_TEMPERATURE,
                top_p=self.config.OLLAMA_TOP_P,
                num_predict=self.config.OLLAMA_NUM_PREDICT
            )
            
            # Create conversation prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant. You have access to the conversation history. "
                          "Provide helpful, accurate, and contextual responses based on the conversation context."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create the conversation chain
            self.chain = (
                RunnablePassthrough.assign(
                    chat_history=lambda x: self.memory_manager.get_memory_variables()["chat_history"]
                )
                | prompt
                | self.llm
                | StrOutputParser()
            )
            
            print(f"✅ Chatbot initialized successfully with model: {self.config.OLLAMA_MODEL}")
            
        except Exception as e:
            print(f"❌ Failed to initialize chatbot: {e}")
            raise
    
    def _wait_for_ollama(self, max_retries: int = 30, delay: int = 2) -> None:
        """Wait for Ollama service to be ready"""
        print("🔄 Waiting for Ollama service...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama service is ready!")
                    return
            except requests.exceptions.RequestException:
                pass
            
            if attempt < max_retries - 1:
                print(f"⏳ Attempt {attempt + 1}/{max_retries} - Retrying in {delay} seconds...")
                time.sleep(delay)
        
        raise ConnectionError("Could not connect to Ollama service")
    
    async def chat(self, message: str) -> AsyncGenerator[str, None]:
        """Send a message and stream the response"""
        if not self.chain:
            raise RuntimeError("Chatbot not properly initialized")
        
        full_response = ""
        try:
            async for chunk in self.chain.astream({"input": message}):
                yield chunk
                full_response += chunk
            
            # Add to memory after streaming is complete
            self.memory_manager.add_message(message, full_response)
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(f"❌ {error_msg}")
            yield f"I apologize, but I encountered an error: {error_msg}"
    
    def get_available_models(self) -> list:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different Ollama model"""
        try:
            self.config.OLLAMA_MODEL = model_name
            self._initialize_llm()
            return True
        except Exception as e:
            print(f"Error switching model: {e}")
            return False
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.memory_manager.clear_memory()
        print("🗑️ Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return self.memory_manager.get_memory_summary()
    
    def get_chat_history(self) -> list:
        """Get formatted chat history for display"""
        messages = self.memory_manager.get_chat_history()
        formatted_history = []
        
        for msg in messages:
            role = "user" if msg.type == "human" else "assistant"
            formatted_history.append({"role": role, "content": msg.content})
        
        return formatted_history