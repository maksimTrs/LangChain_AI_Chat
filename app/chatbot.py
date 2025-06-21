from langchain_ollama.llms import OllamaLLM
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from app.memory_manager import ChatMemoryManager
from app.config import Config
import requests
import time
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, List # Added List
import logging

from langchain_core.runnables import Runnable  # Import Runnable

logger = logging.getLogger(__name__)

class OllamaChatbot:
    """Main chatbot class with LangChain and Ollama integration"""

    config: Config
    session_id: str
    memory_manager: ChatMemoryManager
    current_role: str
    system_prompts: Dict[str, str]
    llm: Optional[OllamaLLM]
    chain: Optional[Runnable]

    def __init__(self, session_id: Optional[str] = None): # session_id can be None initially
        self.config = Config()
        self.session_id = session_id or "default_session" # Assign default if None
        self.memory_manager = ChatMemoryManager(
            session_id=self.session_id,
            memory_size=self.config.CHAT_MEMORY_SIZE
        )
        
        # Initialize system prompt and role
        self.current_role = "Beginner"  # Default role
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
            self.llm = OllamaLLM( # OllamaLLM is a Runnable itself
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
            
            logger.info(f"✅ Chatbot initialized successfully with model: {self.config.OLLAMA_MODEL} for session: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot for session {self.session_id}: {e}", exc_info=True)
            raise
    
    def _wait_for_ollama(self, max_retries: int = 30, delay: int = 2) -> None:
        """Wait for Ollama service to be ready"""
        logger.info("🔄 Waiting for Ollama service...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama service is ready!")
                    return
            except requests.exceptions.RequestException as e:
                logger.debug(f"Ollama readiness check failed on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Attempt {attempt + 1}/{max_retries} - Retrying Ollama connection in {delay} seconds...")
                time.sleep(delay)
        
        logger.error("❌ Could not connect to Ollama service after multiple retries.")
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
            try:
                async for chunk in self.chain.astream({"input": message, "chat_history": chat_history}):
                    if isinstance(chunk, str):
                        response += chunk
                        yield chunk
                    elif isinstance(chunk, dict) and "answer" in chunk:
                        response += chunk["answer"]
                        yield chunk["answer"]
            except ConnectionError as e:
                error_msg = f"Connection error - check if Ollama is running: {str(e)}"
                yield error_msg
                raise ConnectionError(error_msg)
            except TimeoutError as e:
                error_msg = f"Request timeout - try again or use a smaller model: {str(e)}"
                yield error_msg
                raise TimeoutError(error_msg)
            except ValueError as e:
                error_msg = f"Invalid input or model configuration: {str(e)}"
                yield error_msg
                raise ValueError(error_msg)
            
            # Add AI response to memory (async)
            if response:  # Only add if we got a response
                await self.memory_manager.add_message_async("ai", response)
            
        except (ConnectionError, TimeoutError, ValueError):
            # Re-raise specific exceptions we've already handled
            raise
        except Exception as e:
            # Catch any remaining unexpected errors
            error_msg = f"Unexpected error generating response for session {self.session_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            yield error_msg # Yield the error to be displayed in chat
            # No need to raise RuntimeError(error_msg) if we yield it, Streamlit will show it
            # However, if we want to signal a hard failure, we might still raise.
            # For now, yielding is enough for the UI.
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status() # Raise an exception for HTTP error codes
            models_data = response.json().get('models', [])
            return [model['name'] for model in models_data if 'name' in model]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching models from Ollama: {e}", exc_info=True)
            return []
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error fetching models: {e}", exc_info=True)
            return []
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different Ollama model"""
        try:
            logger.info(f"Attempting to switch model to: {model_name} for session {self.session_id}")
            self.config.OLLAMA_MODEL = model_name
            self._initialize_llm() # This already logs success/failure
            return True
        except Exception as e:
            logger.error(f"Error switching model to {model_name} for session {self.session_id}: {e}", exc_info=True)
            return False
    
    def update_system_prompt(self, role: str) -> bool:
        """Update the system prompt based on the selected role"""
        try:
            if role in self.system_prompts:
                logger.info(f"Updating system prompt to role: {role} for session {self.session_id}")
                self.current_role = role
                self._initialize_llm()  # Reinitialize with new prompt, this logs success/failure
                logger.info(f"✅ Updated system prompt for {role} level responses for session {self.session_id}")
                return True
            else:
                logger.warning(f"❌ Invalid role for system prompt update: {role} for session {self.session_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating system prompt to {role} for session {self.session_id}: {e}", exc_info=True)
            return False
    
    async def clear_conversation_async(self):
        """Clear conversation history (async)"""
        await self.memory_manager.clear_conversation_async() # Memory manager logs this
        logger.info(f"🧹 Conversation history cleared successfully via async call for session {self.session_id}")
        
    def clear_conversation(self):
        """Clear conversation history (sync wrapper)"""
        logger.info(f"Attempting to clear conversation for session {self.session_id}")
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                logger.debug(f"Event loop is running, creating task for clear_conversation_async for session {self.session_id}")
                # Create a task instead of using run_until_complete
                asyncio.create_task(self.clear_conversation_async())
            else:
                logger.debug(f"No event loop running, calling asyncio.run for clear_conversation_async for session {self.session_id}")
                asyncio.run(self.clear_conversation_async())
            logger.info(f"🧹 Conversation history clear initiated for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error in clear_conversation wrapper for session {self.session_id}: {e}", exc_info=True)
            # Fallback to sync method
            logger.info(f"Falling back to memory_manager.clear_memory() for session {self.session_id}")
            self.memory_manager.clear_memory()
        # The actual clearing is logged by the async method or memory_manager's sync method.
        
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return self.memory_manager.get_memory_summary()
        
    async def get_chat_history_async(self) -> List[Dict[str, str]]:
        """Get formatted chat history for Streamlit (async)"""
        return await self.memory_manager.get_chat_history_async()
        
    def get_chat_history(self) -> List[Dict[str, str]]:
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
            logger.info(f"Falling back to memory_manager.get_chat_history() for session {self.session_id}")
            return self.memory_manager.get_chat_history()