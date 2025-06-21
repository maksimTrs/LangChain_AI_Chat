from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import Config
from typing import List, Dict, Any
import asyncio
import concurrent.futures

class ChatMemoryManager:
    """Manages conversation memory with database persistence"""
    
    def __init__(self, session_id: str, memory_size: int = 10):
        self.memory_size = memory_size
        self.session_id = session_id
        self.config = Config()
        
        # Create async engine for database
        self.async_engine = create_async_engine(self.config.DATABASE_URL)
        
        # Initialize SQL chat message history
        self.sql_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=self.async_engine,
            table_name=self.config.DATABASE_TABLE_NAME,
            async_mode=True
        )
        
        # Initialize LangChain memory with SQL history
        self.memory = ConversationBufferWindowMemory(
            k=memory_size,
            return_messages=True,
            memory_key="chat_history",
            chat_memory=self.sql_history
        )
        
        # Create thread pool for handling sync-to-async bridges
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    async def add_message_async(self, message_type: str, content: str):
        """Add a message to the chat history asynchronously."""
        try:
            from langchain_core.messages import HumanMessage, AIMessage
            if message_type == "user":
                await self.sql_history.aadd_message(HumanMessage(content=content))
            elif message_type == "ai":
                await self.sql_history.aadd_message(AIMessage(content=content))
        except Exception as e:
            print(f"Error adding message to memory: {e}")
    
    def add_message(self, message_type: str, content: str) -> None:
        """Add a message to memory (sync version with proper async handling)"""
        try:
            # Use nest_asyncio for better async compatibility
            import nest_asyncio
            nest_asyncio.apply()
            
            # Run the async method properly
            asyncio.run(self.add_message_async(message_type, content))
        except RuntimeError as e:
            # If there's already a running event loop, handle it differently
            if "another loop is running" in str(e).lower():
                # Create a future and let it complete in background
                loop = asyncio.get_event_loop()
                future = asyncio.ensure_future(self.add_message_async(message_type, content))
                # Add a callback to handle any errors
                future.add_done_callback(lambda f: print(f"Error in background task: {f.exception()}") if f.exception() else None)
            else:
                print(f"Error adding message: {e}")
        except Exception as e:
            print(f"Error adding message: {e}")
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for LangChain"""
        return self.memory.load_memory_variables({})
    
    async def get_chat_history_async(self):
        """Get the chat history asynchronously formatted for Streamlit."""
        try:
            messages = await self.sql_history.aget_messages()
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'type'):
                    role = "user" if msg.type == "human" else "assistant"
                else:
                    role = "user" if isinstance(msg, HumanMessage) else "assistant"
                formatted_messages.append({
                    "role": role,
                    "content": msg.content
                })
            return formatted_messages
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def get_chat_history(self) -> List[dict]:
        """Get formatted chat history for Streamlit with proper async handling"""
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, run in executor to avoid blocking
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(self.get_chat_history_async())
            except RuntimeError:
                # No running loop, we can safely run async code
                return asyncio.run(self.get_chat_history_async())
        except Exception as e:
            print(f"Error getting chat history, returning empty list: {e}")
            return []
    
    async def clear_conversation_async(self):
        """Clear the conversation history asynchronously."""
        try:
            await self.sql_history.aclear()
        except Exception as e:
            print(f"Error clearing conversation: {e}")
    
    def clear_memory(self) -> None:
        """Clear all conversation memory with proper async handling"""
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, schedule the task
                asyncio.create_task(self.clear_conversation_async())
            except RuntimeError:
                # No running loop, we can safely run async code
                asyncio.run(self.clear_conversation_async())
        except Exception as e:
            print(f"Error clearing memory: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        messages = self.get_chat_history()
        return {
            "total_messages": len(messages),
            "memory_size_limit": self.memory_size,
            "has_conversation": len(messages) > 0,
            "session_id": self.session_id
        }
    
    def __del__(self):
        """Cleanup thread pool on destruction"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)