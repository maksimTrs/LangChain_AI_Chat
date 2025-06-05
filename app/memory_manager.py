from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any

class ChatMemoryManager:
    """Manages conversation memory"""
    
    def __init__(self, memory_size: int = 10):
        self.memory_size = memory_size
        
        # Initialize LangChain memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_size,
            return_messages=True,
            memory_key="chat_history"
        )
    
    def add_message(self, human_message: str, ai_message: str) -> None:
        """Add a conversation turn to memory"""
        self.memory.chat_memory.add_user_message(human_message)
        self.memory.chat_memory.add_ai_message(ai_message)
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for LangChain"""
        return self.memory.load_memory_variables({})
    
    def get_chat_history(self) -> List[BaseMessage]:
        """Get formatted chat history"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self) -> None:
        """Clear all conversation memory"""
        self.memory.clear()
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        messages = self.get_chat_history()
        return {
            "total_messages": len(messages),
            "memory_size_limit": self.memory_size,
            "has_conversation": len(messages) > 0
        }