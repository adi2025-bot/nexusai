"""
Spell Correction Service
Automatic typo correction for user input while preserving technical terms.
"""

import re
import logging
from typing import Set, Optional
from functools import lru_cache

logger = logging.getLogger("NexusAI.SpellService")


# Technical terms to NEVER correct (programming, tech, etc.)
PROTECTED_TERMS: Set[str] = {
    # Programming languages
    'python', 'javascript', 'typescript', 'java', 'kotlin', 'swift', 'rust',
    'golang', 'ruby', 'php', 'perl', 'scala', 'haskell', 'lua', 'dart',
    'csharp', 'cpp', 'sql', 'html', 'css', 'sass', 'scss', 'jsx', 'tsx',
    
    # Frameworks & tools
    'react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt', 'django', 'flask',
    'fastapi', 'express', 'nodejs', 'npm', 'yarn', 'pip', 'conda', 'docker',
    'kubernetes', 'k8s', 'aws', 'gcp', 'azure', 'terraform', 'ansible',
    
    # Tech terms
    'api', 'rest', 'graphql', 'json', 'xml', 'yaml', 'http', 'https', 'tcp',
    'udp', 'ssh', 'ssl', 'tls', 'jwt', 'oauth', 'saml', 'ldap', 'dns', 'cdn',
    'gpu', 'cpu', 'ram', 'ssd', 'nvme', 'pcie', 'usb', 'hdmi', 'wifi', 'lan',
    
    # AI/ML terms
    'ai', 'ml', 'llm', 'gpt', 'bert', 'transformers', 'pytorch', 'tensorflow',
    'keras', 'numpy', 'pandas', 'sklearn', 'matplotlib', 'opencv', 'cuda',
    'rag', 'nlp', 'cnn', 'rnn', 'lstm', 'gan', 'vae', 'rlhf', 'embeddings',
    
    # Databases
    'mysql', 'postgres', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
    'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'supabase', 'firebase',
    
    # Abbreviations
    'ui', 'ux', 'cli', 'gui', 'ide', 'vm', 'os', 'devops', 'cicd', 'saas',
    'paas', 'iaas', 'sdk', 'mvp', 'poc', 'eta', 'faq', 'btw', 'imo', 'tbh',
    
    # Special terms
    'nexusai', 'chatgpt', 'gemini', 'claude', 'groq', 'openai', 'anthropic',
    'streamlit', 'gradio', 'huggingface', 'github', 'gitlab', 'bitbucket',
}


class SpellCorrector:
    """Smart spell correction that preserves technical terms."""
    
    def __init__(self):
        self._spell = None
        self._loaded = False
    
    @property
    def spell(self):
        """Lazy load spell checker."""
        if not self._loaded:
            try:
                from spellchecker import SpellChecker
                self._spell = SpellChecker()
                # Add protected terms to the dictionary so they're not corrected
                self._spell.word_frequency.load_words(PROTECTED_TERMS)
                self._loaded = True
                logger.info("SpellChecker loaded successfully")
            except ImportError:
                logger.warning("pyspellchecker not installed, spell correction disabled")
                self._spell = None
                self._loaded = True
        return self._spell
    
    def is_protected(self, word: str) -> bool:
        """Check if word should not be corrected."""
        word_lower = word.lower()
        
        # Check protected terms
        if word_lower in PROTECTED_TERMS:
            return True
        
        # Protect URLs, emails, file paths
        if any(c in word for c in ['@', '/', '\\', '.com', '.org', '.py', '.js']):
            return True
        
        # Protect words starting with special chars
        if word.startswith(('#', '@', '/', '\\')):
            return True
        
        # Protect words with numbers
        if any(c.isdigit() for c in word):
            return True
        
        # Protect all-caps acronyms (3+ chars)
        if word.isupper() and len(word) >= 2:
            return True
        
        return False
    
    @lru_cache(maxsize=1000)
    def correct_word(self, word: str) -> str:
        """Correct a single word, preserving case and protected terms."""
        if not self.spell or not word:
            return word
        
        # Skip protected terms
        if self.is_protected(word):
            return word
        
        # Skip very short words (likely abbreviations)
        if len(word) <= 2:
            return word
        
        # Skip words that are already correct
        word_lower = word.lower()
        if word_lower in self.spell:
            return word
        
        # Get correction
        correction = self.spell.correction(word_lower)
        
        if correction and correction != word_lower:
            # Preserve original case pattern
            if word.isupper():
                return correction.upper()
            elif word[0].isupper():
                return correction.capitalize()
            return correction
        
        return word
    
    def correct_text(self, text: str) -> tuple[str, bool]:
        """
        Correct typos in text while preserving structure.
        
        Returns:
            tuple: (corrected_text, was_corrected)
        """
        if not self.spell or not text:
            return text, False
        
        # Split into words while preserving structure
        words = re.findall(r'\S+|\s+', text)
        corrected_words = []
        was_corrected = False
        
        for word in words:
            if word.isspace():
                corrected_words.append(word)
            else:
                # Separate punctuation
                prefix = ''
                suffix = ''
                core = word
                
                # Extract leading punctuation
                while core and not core[0].isalnum():
                    prefix += core[0]
                    core = core[1:]
                
                # Extract trailing punctuation
                while core and not core[-1].isalnum():
                    suffix = core[-1] + suffix
                    core = core[:-1]
                
                if core:
                    corrected = self.correct_word(core)
                    if corrected != core:
                        was_corrected = True
                    corrected_words.append(prefix + corrected + suffix)
                else:
                    corrected_words.append(word)
        
        return ''.join(corrected_words), was_corrected


# Singleton instance
_spell_corrector: Optional[SpellCorrector] = None


def get_spell_corrector() -> SpellCorrector:
    """Get the singleton spell corrector instance."""
    global _spell_corrector
    if _spell_corrector is None:
        _spell_corrector = SpellCorrector()
    return _spell_corrector


def correct_user_input(text: str) -> tuple[str, bool]:
    """
    Convenience function to correct user input.
    
    Args:
        text: User's input text
        
    Returns:
        tuple: (corrected_text, was_corrected)
    """
    corrector = get_spell_corrector()
    return corrector.correct_text(text)
