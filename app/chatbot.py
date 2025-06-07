from langchain_ollama.llms import OllamaLLM
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from app.memory_manager import ChatMemoryManager
from app.config import Config
import requests
import time
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator

class OllamaChatbot:
    """Main chatbot class with LangChain and Ollama integration"""
    
    def __init__(self, session_id: str = None):
        self.config = Config()
        self.session_id = session_id or "default_session"
        self.memory_manager = ChatMemoryManager(
            session_id=self.session_id,
            memory_size=self.config.CHAT_MEMORY_SIZE
        )
        
        # Initialize system prompt and role
        self.current_role = "Beginner"
        self.system_prompts = {
            "Beginner": "You are a helpful AI assistant. Provide clear, simple explanations suitable for beginners. Use easy-to-understand language and avoid technical jargon. Break down complex concepts into digestible parts.",
            "Expert": "You are an expert AI assistant. Provide detailed, technical responses with in-depth analysis. Use professional terminology and include relevant technical details, best practices, and advanced concepts.",
            "PhD": "You are a highly specialized AI assistant with PhD-level expertise. Provide comprehensive, research-oriented responses with theoretical depth, citations when relevant, cutting-edge insights, and advanced analytical perspectives."
        }
        
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
            
            # Create conversation prompt template with dynamic system prompt
            system_message = f"{self.system_prompts[self.current_role]} You have access to the conversation history. Provide helpful, accurate, and contextual responses based on the conversation context."
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Create the conversation chain
            self.chain = (
                RunnablePassthrough.assign(
                    chat_history=lambda x: x.get("chat_history", [])
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
        
        try:
            # Add user message to memory (async)
            await self.memory_manager.add_message_async("user", message)
            
            # Get chat history asynchronously
            chat_history = await self.memory_manager.sql_history.aget_messages()
            
            # Get response from chain with chat history
            response = ""
            async for chunk in self.chain.astream({"input": message, "chat_history": chat_history}):
                if isinstance(chunk, str):
                    response += chunk
                    yield chunk
                elif isinstance(chunk, dict) and "answer" in chunk:
                    response += chunk["answer"]
                    yield chunk["answer"]
            
            # Add AI response to memory (async)
            await self.memory_manager.add_message_async("ai", response)
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            yield error_msg
            raise Exception(error_msg)
    
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
    
    def update_system_prompt(self, role: str) -> bool:
        """Update the system prompt based on the selected role"""
        try:
            if role in self.system_prompts:
                self.current_role = role
                self._initialize_llm()  # Reinitialize with new prompt
                print(f"✅ Updated system prompt for {role} level responses")
                return True
            else:
                print(f"❌ Invalid role: {role}")
                return False
        except Exception as e:
            print(f"Error updating system prompt: {e}")
            return False
    
    async def clear_conversation_async(self):
        """Clear conversation history (async)"""
        await self.memory_manager.clear_conversation_async()
        print("🧹 Conversation history cleared")
        
    def clear_conversation(self):
        """Clear conversation history (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a task instead of using run_until_complete
                asyncio.create_task(self.clear_conversation_async())
            else:
                asyncio.run(self.clear_conversation_async())
        except Exception as e:
            print(f"Error clearing conversation: {e}")
            # Fallback to sync method
            self.memory_manager.clear_memory()
        print("🧹 Conversation history cleared")
        
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        return self.memory_manager.get_memory_summary()
        
    async def get_chat_history_async(self) -> list:
        """Get formatted chat history for Streamlit (async)"""
        return await self.memory_manager.get_chat_history_async()
        
    def get_chat_history(self) -> list:
        """Get formatted chat history for Streamlit (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Use nest_asyncio to handle nested loops
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(self.get_chat_history_async())
            else:
                return asyncio.run(self.get_chat_history_async())
        except RuntimeError:
            # Fallback to sync method
            return self.memory_manager.get_chat_history()