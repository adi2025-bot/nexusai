"""
Database Service using Supabase PostgreSQL.
Handles chat history persistence, conversations, and usage tracking.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Conversation:
    """Conversation data class."""
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


@dataclass
class Message:
    """Message data class."""
    id: str
    conversation_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    created_at: str


class DatabaseService:
    """
    Supabase Database Service.
    Handles all database operations for chat persistence.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self._client = None
    
    @property
    def client(self):
        """Lazy-load Supabase client."""
        if self._client is None:
            try:
                from supabase import create_client
                self._client = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {e}")
                raise
        return self._client
    
    def is_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.supabase_url and self.supabase_key)
    
    # ==================== Profile Methods ====================
    
    def create_profile(self, user_id: str, email: str, display_name: str = None) -> bool:
        """Create a user profile after signup."""
        try:
            self.client.table("profiles").insert({
                "id": user_id,
                "email": email,
                "display_name": display_name or email.split("@")[0]
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            return False
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile."""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return None
    
    def update_profile(self, user_id: str, data: Dict) -> bool:
        """Update user profile."""
        try:
            self.client.table("profiles").update(data).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return False
    
    # ==================== Conversation Methods ====================
    
    def create_conversation(self, user_id: str, title: str = "New Chat") -> Optional[str]:
        """
        Create a new conversation.
        
        Returns:
            Conversation ID if successful, None otherwise
        """
        try:
            response = self.client.table("conversations").insert({
                "user_id": user_id,
                "title": title
            }).execute()
            
            if response.data:
                return response.data[0]["id"]
            return None
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None
    
    def get_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """
        Get all conversations for a user.
        
        Returns:
            List of Conversation objects
        """
        try:
            response = self.client.table("conversations")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("updated_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return [
                Conversation(
                    id=conv["id"],
                    user_id=conv["user_id"],
                    title=conv["title"],
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"]
                )
                for conv in response.data
            ]
            
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title."""
        try:
            self.client.table("conversations").update({
                "title": title,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", conversation_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        try:
            self.client.table("conversations").delete().eq("id", conversation_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False
    
    # ==================== Message Methods ====================
    
    def save_message(self, conversation_id: str, role: str, content: str) -> Optional[str]:
        """
        Save a message to a conversation.
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            response = self.client.table("messages").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content
            }).execute()
            
            # Update conversation's updated_at
            self.client.table("conversations").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", conversation_id).execute()
            
            if response.data:
                return response.data[0]["id"]
            return None
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return None
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        """
        Get all messages for a conversation.
        
        Returns:
            List of Message objects in chronological order
        """
        try:
            response = self.client.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at", desc=False)\
                .execute()
            
            return [
                Message(
                    id=msg["id"],
                    conversation_id=msg["conversation_id"],
                    role=msg["role"],
                    content=msg["content"],
                    created_at=msg["created_at"]
                )
                for msg in response.data
            ]
            
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def get_messages_as_dicts(self, conversation_id: str) -> List[Dict]:
        """Get messages formatted for chat display."""
        messages = self.get_messages(conversation_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    # ==================== Usage Tracking ====================
    
    def log_usage(self, user_id: str, action: str, tokens: int = 0, 
                  provider: str = None, model: str = None) -> bool:
        """
        Log usage for analytics and quotas.
        
        Args:
            user_id: User's ID
            action: Action type (chat, image_gen, search, etc.)
            tokens: Number of tokens used
            provider: AI provider used
            model: Model used
        """
        try:
            self.client.table("usage_logs").insert({
                "user_id": user_id,
                "action": action,
                "tokens_used": tokens,
                "provider": provider,
                "model": model
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
            return False
    
    def get_usage_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get usage statistics for a user."""
        try:
            # This is a simplified version - in production you'd use SQL functions
            response = self.client.table("usage_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            total_tokens = sum(log.get("tokens_used", 0) for log in response.data)
            action_counts = {}
            for log in response.data:
                action = log.get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                "total_tokens": total_tokens,
                "total_actions": len(response.data),
                "action_counts": action_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {"total_tokens": 0, "total_actions": 0, "action_counts": {}}


# Factory function
def create_database_service() -> DatabaseService:
    """Create a database service with settings from environment."""
    from config.settings import settings
    
    return DatabaseService(
        supabase_url=settings.ai.supabase_url,
        supabase_key=settings.ai.supabase_key
    )
