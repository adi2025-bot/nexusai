"""
Memory Service
Context compression, conversation summarization, and user preference memory.
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger("NexusAI.MemoryService")


@dataclass
class UserPreferences:
    """User preferences for personalized responses."""
    verbosity: str = "normal"  # short, normal, detailed
    language: str = "english"  # english, hinglish, hindi
    style: str = "friendly"    # friendly, professional, casual
    expertise_level: str = "intermediate"  # beginner, intermediate, expert
    prefer_code_examples: bool = True
    prefer_bullet_points: bool = True
    
    def to_prompt(self) -> str:
        """Convert preferences to system prompt instructions."""
        instructions = []
        
        # Verbosity
        if self.verbosity == "short":
            instructions.append("Keep responses brief and concise. Use bullet points.")
        elif self.verbosity == "detailed":
            instructions.append("Provide thorough, detailed explanations with examples.")
        
        # Language
        if self.language == "hinglish":
            instructions.append("Mix English with Hindi naturally (Hinglish style).")
        elif self.language == "hindi":
            instructions.append("Respond in Hindi when appropriate.")
        
        # Style
        if self.style == "professional":
            instructions.append("Maintain a formal, professional tone.")
        elif self.style == "casual":
            instructions.append("Be casual and relaxed in tone. Use informal language.")
        
        # Expertise
        if self.expertise_level == "beginner":
            instructions.append("Explain concepts simply. Avoid jargon. Use analogies.")
        elif self.expertise_level == "expert":
            instructions.append("Assume technical knowledge. Be concise on basics.")
        
        # Format preferences
        if self.prefer_code_examples:
            instructions.append("Include code examples when relevant.")
        if self.prefer_bullet_points:
            instructions.append("Use bullet points for clarity.")
        
        return "\n".join(f"- {i}" for i in instructions) if instructions else ""


@dataclass
class ConversationMemory:
    """Compressed conversation memory."""
    summary: str = ""
    topics: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    user_goals: List[str] = field(default_factory=list)
    last_updated: str = ""
    message_count: int = 0
    
    def to_prompt(self) -> str:
        """Convert memory to context for system prompt."""
        if not self.summary and not self.topics:
            return ""
        
        parts = []
        
        if self.summary:
            parts.append(f"Previous conversation context: {self.summary}")
        
        if self.topics:
            parts.append(f"Topics discussed: {', '.join(self.topics[:5])}")
        
        if self.user_goals:
            parts.append(f"User's goals: {', '.join(self.user_goals[:3])}")
        
        if self.key_facts:
            parts.append(f"Key information: {'; '.join(self.key_facts[:3])}")
        
        return "\n".join(parts)


class MemoryService:
    """
    Manages conversation memory and user preferences.
    Compresses old context while keeping recent messages raw.
    """
    
    # How many recent messages to keep verbatim
    KEEP_RAW_COUNT = 6
    
    # Max summary length
    MAX_SUMMARY_LENGTH = 300
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.preferences = UserPreferences()
        self._topic_keywords = set()
    
    def summarize_messages(self, messages: List[Dict], keep_raw: int = None) -> tuple[str, List[Dict]]:
        """
        Compress old messages into a summary, keep recent ones raw.
        
        Args:
            messages: Full message history
            keep_raw: How many recent messages to keep raw (default: KEEP_RAW_COUNT)
            
        Returns:
            tuple: (summary_string, recent_messages_to_keep)
        """
        keep_raw = keep_raw or self.KEEP_RAW_COUNT
        
        if len(messages) <= keep_raw:
            # Not enough messages to compress
            return "", messages
        
        # Split into old (to summarize) and recent (to keep)
        old_messages = messages[:-keep_raw]
        recent_messages = messages[-keep_raw:]
        
        # Generate summary from old messages
        summary = self._generate_summary(old_messages)
        
        # Update memory
        self.memory.summary = summary
        self.memory.message_count = len(messages)
        self.memory.last_updated = datetime.now().isoformat()
        
        # Extract topics
        self._extract_topics(old_messages)
        
        return summary, recent_messages
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """Generate a concise summary of messages."""
        if not messages:
            return ""
        
        # Extract key content from messages
        user_points = []
        ai_responses = []
        
        for msg in messages:
            content = msg.get("content", "")[:200]  # Limit per message
            role = msg.get("role", "")
            
            if role == "user":
                user_points.append(content)
            elif role == "assistant":
                # Get first sentence or key point
                first_sentence = content.split('.')[0][:100] if content else ""
                ai_responses.append(first_sentence)
        
        # Build summary
        parts = []
        
        if user_points:
            # Summarize user questions
            topics = set()
            for point in user_points[-5:]:  # Last 5 user messages
                words = point.lower().split()
                # Extract key topics (nouns, verbs)
                for word in words:
                    if len(word) > 4 and word.isalpha():
                        topics.add(word)
            
            self.memory.topics = list(topics)[:8]
            parts.append(f"User asked about: {', '.join(list(topics)[:5])}")
        
        if ai_responses:
            # Note key AI responses
            parts.append(f"AI covered: {'; '.join(ai_responses[-3:])}")
        
        summary = ". ".join(parts)
        
        # Truncate if too long
        if len(summary) > self.MAX_SUMMARY_LENGTH:
            summary = summary[:self.MAX_SUMMARY_LENGTH] + "..."
        
        return summary
    
    def _extract_topics(self, messages: List[Dict]):
        """Extract topics from messages."""
        keywords = set()
        
        for msg in messages:
            content = msg.get("content", "").lower()
            words = content.split()
            
            for word in words:
                # Simple extraction: longer words that appear in multiple messages
                if len(word) > 5 and word.isalpha():
                    keywords.add(word)
        
        self.memory.topics = list(keywords)[:10]
    
    def add_key_fact(self, fact: str):
        """Add a key fact to remember."""
        if fact and fact not in self.memory.key_facts:
            self.memory.key_facts.append(fact)
            # Keep only recent facts
            self.memory.key_facts = self.memory.key_facts[-5:]
    
    def add_user_goal(self, goal: str):
        """Add a user goal to track."""
        if goal and goal not in self.memory.user_goals:
            self.memory.user_goals.append(goal)
            self.memory.user_goals = self.memory.user_goals[-3:]
    
    def update_preference(self, key: str, value):
        """Update a user preference."""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            logger.info(f"Updated preference: {key} = {value}")
    
    def get_context_prompt(self) -> str:
        """Get the combined context prompt from memory and preferences."""
        parts = []
        
        # Add memory context
        memory_prompt = self.memory.to_prompt()
        if memory_prompt:
            parts.append("=== CONVERSATION CONTEXT ===")
            parts.append(memory_prompt)
        
        # Add preference instructions
        pref_prompt = self.preferences.to_prompt()
        if pref_prompt:
            parts.append("\n=== USER PREFERENCES ===")
            parts.append(pref_prompt)
        
        return "\n".join(parts) if parts else ""
    
    def prepare_messages_for_api(self, messages: List[Dict]) -> List[Dict]:
        """
        Prepare messages for API call with context compression.
        
        Returns messages with old context compressed into a system message.
        """
        summary, recent = self.summarize_messages(messages)
        
        if summary:
            # Prepend summary as a system-level context note
            context_note = {
                "role": "system",
                "content": f"[Previous conversation summary: {summary}]"
            }
            return [context_note] + recent
        
        return recent
    
    def to_dict(self) -> Dict:
        """Serialize memory state for persistence."""
        return {
            "memory": asdict(self.memory),
            "preferences": asdict(self.preferences)
        }
    
    def from_dict(self, data: Dict):
        """Load memory state from dict."""
        if "memory" in data:
            for key, value in data["memory"].items():
                if hasattr(self.memory, key):
                    setattr(self.memory, key, value)
        
        if "preferences" in data:
            for key, value in data["preferences"].items():
                if hasattr(self.preferences, key):
                    setattr(self.preferences, key, value)


# Singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get singleton memory service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service


def compress_context(messages: List[Dict]) -> List[Dict]:
    """Convenience function to compress message context."""
    service = get_memory_service()
    return service.prepare_messages_for_api(messages)
