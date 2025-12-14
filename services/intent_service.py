"""
Intent Detection Service
Detects user intent from prompts for smarter responses.
"""

import re
import logging
from typing import Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("NexusAI.IntentService")


class Intent(Enum):
    """Types of user intents."""
    EXPLAIN = "explain"      # User wants something explained
    DEBUG = "debug"          # User wants help fixing/debugging
    SUMMARIZE = "summarize"  # User wants a summary
    COMPARE = "compare"      # User wants comparison
    CREATE = "create"        # User wants something created/written
    ANALYZE = "analyze"      # User wants analysis
    QUESTION = "question"    # Simple question/info request
    FOLLOWUP = "followup"    # Continuing previous topic
    GREETING = "greeting"    # Social greeting
    UNKNOWN = "unknown"      # Cannot determine


class Confidence(Enum):
    """Confidence level in intent detection."""
    HIGH = "high"       # >80% confident
    MEDIUM = "medium"   # 50-80% confident
    LOW = "low"         # <50% confident


@dataclass
class IntentResult:
    """Result of intent detection."""
    intent: Intent
    confidence: Confidence
    sub_intent: str = ""  # More specific intent (e.g., "explain_concept", "debug_code")
    requires_clarification: bool = False
    clarification_question: str = ""


class IntentDetector:
    """Detects user intent from prompts using rule-based matching."""
    
    # Intent patterns (keyword → intent mapping)
    INTENT_PATTERNS: Dict[Intent, List[str]] = {
        Intent.EXPLAIN: [
            'explain', 'what is', 'what are', 'how does', 'how do', 'why does',
            'why do', 'describe', 'tell me about', 'help me understand',
            'meaning of', 'define', 'definition', 'concept', 'break down',
            'walk me through', 'teach', 'learn about', 'understand'
        ],
        Intent.DEBUG: [
            'fix', 'debug', 'error', 'bug', 'not working', 'broken', 'issue',
            'problem', 'wrong', 'fail', 'crash', 'exception', 'doesnt work',
            "doesn't work", 'help me fix', 'troubleshoot', 'solve'
        ],
        Intent.SUMMARIZE: [
            'summarize', 'summary', 'tldr', 'tl;dr', 'brief', 'short version',
            'in short', 'key points', 'main points', 'overview', 'recap',
            'gist', 'essence', 'nutshell'
        ],
        Intent.COMPARE: [
            'compare', 'vs', 'versus', 'difference between', 'differences',
            'which is better', 'pros and cons', 'advantages', 'disadvantages',
            'or', 'compared to', 'better than', 'worse than', 'prefer'
        ],
        Intent.CREATE: [
            'write', 'create', 'generate', 'make', 'build', 'draft', 'compose',
            'design', 'code for', 'script for', 'program to', 'implement',
            'develop', 'produce', 'construct', 'craft', 'give me'
        ],
        Intent.ANALYZE: [
            'analyze', 'analysis', 'evaluate', 'assess', 'review', 'examine',
            'study', 'investigate', 'look at', 'check', 'inspect', 'critique',
            'feedback', 'opinion on', 'thoughts on', 'what do you think'
        ],
        Intent.GREETING: [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'howdy', 'greetings', 'sup', 'yo', 'hola', 'namaste', 'hii'
        ],
        Intent.FOLLOWUP: [
            'continue', 'go on', 'more', 'elaborate', 'expand', 'and then',
            'what next', 'ok', 'okay', 'yes', 'yeah', 'sure', 'got it',
            'thanks', 'thank you', 'cool', 'great', 'nice', 'interesting',
            'tell me more', 'keep going', 'what else'
        ]
    }
    
    # Ambiguous patterns that need clarification
    AMBIGUOUS_PATTERNS = [
        'it', 'this', 'that', 'these', 'those', 'the thing', 'stuff',
        'some', 'something', 'anything', 'whatever'
    ]
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for faster matching."""
        self._compiled_patterns = {}
        for intent, keywords in self.INTENT_PATTERNS.items():
            # Create regex pattern that matches any keyword
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self._compiled_patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def detect(self, prompt: str, history: List[Dict] = None) -> IntentResult:
        """
        Detect intent from user prompt.
        
        Args:
            prompt: User's input text
            history: Previous messages for context
            
        Returns:
            IntentResult with detected intent and confidence
        """
        prompt_lower = prompt.lower().strip()
        history = history or []
        
        # Check for empty/very short prompts
        if len(prompt_lower) < 2:
            return IntentResult(
                intent=Intent.UNKNOWN,
                confidence=Confidence.LOW,
                requires_clarification=True,
                clarification_question="Could you please provide more details about what you'd like help with?"
            )
        
        # Score each intent based on pattern matches
        scores: Dict[Intent, int] = {}
        for intent, pattern in self._compiled_patterns.items():
            matches = pattern.findall(prompt_lower)
            scores[intent] = len(matches)
        
        # Get highest scoring intent
        best_intent = max(scores, key=scores.get) if scores else Intent.UNKNOWN
        best_score = scores.get(best_intent, 0)
        
        # Determine confidence based on score and prompt length
        word_count = len(prompt_lower.split())
        
        if best_score >= 2:
            confidence = Confidence.HIGH
        elif best_score == 1:
            confidence = Confidence.MEDIUM if word_count >= 5 else Confidence.LOW
        else:
            confidence = Confidence.LOW
            best_intent = Intent.QUESTION  # Default to question for unmatched
        
        # Check if this is a follow-up (short response after AI message)
        if history and len(history) >= 1:
            if word_count <= 3 and history[-1].get('role') == 'assistant':
                # Likely a follow-up to previous response
                if scores.get(Intent.FOLLOWUP, 0) > 0 or word_count <= 2:
                    best_intent = Intent.FOLLOWUP
                    confidence = Confidence.MEDIUM
        
        # Check for ambiguity
        requires_clarification = False
        clarification_question = ""
        
        if confidence == Confidence.LOW:
            # Check for ambiguous pronouns without context
            has_ambiguous = any(
                re.search(r'\b' + re.escape(amb) + r'\b', prompt_lower)
                for amb in self.AMBIGUOUS_PATTERNS
            )
            
            if has_ambiguous and len(history) == 0:
                requires_clarification = True
                clarification_question = self._generate_clarification(prompt, best_intent)
        
        # Determine sub-intent
        sub_intent = self._get_sub_intent(prompt_lower, best_intent)
        
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            sub_intent=sub_intent,
            requires_clarification=requires_clarification,
            clarification_question=clarification_question
        )
    
    def _get_sub_intent(self, prompt: str, intent: Intent) -> str:
        """Get more specific sub-intent."""
        if intent == Intent.EXPLAIN:
            if any(w in prompt for w in ['code', 'function', 'class', 'method']):
                return "explain_code"
            elif any(w in prompt for w in ['concept', 'theory', 'idea']):
                return "explain_concept"
            return "explain_general"
        
        elif intent == Intent.CREATE:
            if any(w in prompt for w in ['code', 'function', 'script', 'program']):
                return "create_code"
            elif any(w in prompt for w in ['email', 'letter', 'message']):
                return "create_email"
            elif any(w in prompt for w in ['essay', 'article', 'blog', 'story']):
                return "create_writing"
            return "create_general"
        
        elif intent == Intent.DEBUG:
            if 'error' in prompt:
                return "debug_error"
            elif 'performance' in prompt:
                return "debug_performance"
            return "debug_general"
        
        return ""
    
    def _generate_clarification(self, prompt: str, intent: Intent) -> str:
        """Generate a clarification question."""
        if intent == Intent.EXPLAIN:
            return "Could you specify what topic or concept you'd like me to explain?"
        elif intent == Intent.DEBUG:
            return "Could you share the error message or describe what's not working?"
        elif intent == Intent.CREATE:
            return "What would you like me to create? (code, document, etc.)"
        elif intent == Intent.ANALYZE:
            return "What would you like me to analyze? Please share the content or describe it."
        else:
            return "Could you provide more details about what you need help with?"
    
    def get_prompt_enhancement(self, result: IntentResult) -> str:
        """
        Get system prompt enhancement based on detected intent.
        """
        enhancements = {
            Intent.EXPLAIN: "Provide a clear, educational explanation. Use analogies and examples. Structure your response with headings if complex.",
            Intent.DEBUG: "Focus on identifying the root cause. Provide step-by-step debugging guidance. Suggest specific fixes with code examples.",
            Intent.SUMMARIZE: "Be concise and focused. Use bullet points. Highlight the most important information. Keep it brief.",
            Intent.COMPARE: "Create a structured comparison. Use tables if helpful. Highlight key differences and similarities. Give a recommendation if appropriate.",
            Intent.CREATE: "Be creative and thorough. Provide complete, working examples. Explain your choices briefly.",
            Intent.ANALYZE: "Be objective and thorough. Identify patterns and insights. Support conclusions with evidence.",
            Intent.FOLLOWUP: "Continue from the previous context naturally. Don't repeat what was already said.",
            Intent.GREETING: "Be friendly and welcoming. Ask how you can help.",
        }
        
        return enhancements.get(result.intent, "")


# Singleton instance
_intent_detector = None


def get_intent_detector() -> IntentDetector:
    """Get singleton intent detector instance."""
    global _intent_detector
    if _intent_detector is None:
        _intent_detector = IntentDetector()
    return _intent_detector


def detect_intent(prompt: str, history: List[Dict] = None) -> IntentResult:
    """Convenience function to detect intent."""
    detector = get_intent_detector()
    return detector.detect(prompt, history)
