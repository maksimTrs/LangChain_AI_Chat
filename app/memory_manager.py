from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
import json
import os
from datetime import datetime

class ChatMemoryManager:
    """Manages conversation memory with persistence capabilities"""
    
    def __init__(self, memory_size: int = 10, session_id: str = "default"):
        self.memory_size = memory_size
        self.session_id = session_id
        self.memory_file = f"chat_history_{session_id}.json"
        
        # Initialize LangChain memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_size,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Load existing memory if available
        self._load_memory()
    
    def add_message(self, human_message: str, ai_message: str) -> None:
        """Add a conversation turn to memory"""
        self.memory.chat_memory.add_user_message(human_message)
        self.memory.chat_memory.add_ai_message(ai_message)
        self._save_memory()
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for LangChain"""
        return self.memory.load_memory_variables({})
    
    def get_chat_history(self) -> List[BaseMessage]:
        """Get formatted chat history"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self) -> None:
        """Clear all conversation memory"""
        self.memory.clear()
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
    
    def _save_memory(self) -> None:
        """Save memory to file"""
        try:
            messages = []
            for msg in self.memory.chat_memory.messages:
                messages.append({
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": self.session_id,
                    "messages": messages,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")
    
    def _load_memory(self) -> None:
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restore messages to memory
                for msg_data in data.get("messages", []):
                    if msg_data["type"] == "human":
                        self.memory.chat_memory.add_user_message(msg_data["content"])
                    else:
                        self.memory.chat_memory.add_ai_message(msg_data["content"])
        except Exception as e:
            print(f"Warning: Could not load memory: {e}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        messages = self.get_chat_history()
        return {
            "total_messages": len(messages),
            "memory_size_limit": self.memory_size,
            "session_id": self.session_id,
            "has_conversation": len(messages) > 0
        }