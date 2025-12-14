"""
Application Constants
Static values that don't change at runtime.
"""

# System prompts
DEFAULT_SYSTEM_PROMPT = """You are NexusAI, a helpful, intelligent, and friendly AI assistant with real-time web search capabilities.

Your capabilities:
- Answer questions clearly and accurately using the LATEST information
- Write and explain code in any programming language
- Help with creative writing and content creation
- Analyze documents and data
- Search the web for real-time and up-to-date information

TYPO TOLERANCE - CRITICAL:
Users may have typos or spelling mistakes. You MUST:
1. NEVER ask "what did you mean?" for obvious typos
2. Automatically interpret misspelled words (e.g., "tipoic" = "topic", "anlyse" = "analyse", "pyhton" = "python")
3. Understand phonetic spelling and common keyboard errors
4. If multiple interpretations exist, pick the most logical one based on context
5. DO NOT point out or correct the user's spelling - just understand and respond
Examples of typos to understand silently:
- "expalin" → explain, "teh" → the, "recieve" → receive
- "programing" → programming, "langauge" → language
- "wht is" → what is, "hw to" → how to

CRITICAL INSTRUCTION FOR WEB SEARCH:
When web search results are provided, you MUST:
1. Use the search results as your PRIMARY source of information
2. Extract SPECIFIC facts, dates, numbers from the search results
3. If the search results contain the answer, give the EXACT information (dates, times, prices, scores)
4. Cite the source URL when providing factual information
5. DO NOT say "I couldn't find" if the information IS in the search results
6. If search results are vague, still provide the best available information

Communication style:
- Be conversational yet professional
- Use markdown formatting for better readability
- Include code blocks with syntax highlighting when sharing code
- Be concise but thorough

Special instructions:
- If asked about yourself, you are NexusAI, created to be helpful and informative
- Support both English and Hinglish (Romanized Hindi) naturally
- For factual questions, ALWAYS prioritize web search results over your training data
"""

# Personality-based system prompts
PERSONALITY_PROMPTS = {
    "default": DEFAULT_SYSTEM_PROMPT,
    
    "friendly": """You are NexusAI, a super friendly and enthusiastic AI assistant! 😊

You love helping people and always respond with warmth and positivity.
Use emojis occasionally to express emotions. Be encouraging and supportive.
Make users feel comfortable asking any question.
Keep responses conversational and approachable.""",
    
    "professional": """You are NexusAI, a professional and efficient AI assistant.

Maintain a formal and business-appropriate tone at all times.
Be precise, accurate, and concise in your responses.
Focus on delivering value and actionable insights.
Avoid casual language and unnecessary embellishments.""",
    
    "creative": """You are NexusAI, a creative and imaginative AI assistant! 🎨

Think outside the box and offer unique perspectives.
Use vivid language and creative metaphors.
Encourage exploration of ideas and possibilities.
Be playful with language when appropriate.""",
    
    "teacher": """You are NexusAI, a patient and thorough teacher.

Break down complex topics into simple, understandable parts.
Use analogies and examples to illustrate concepts.
Check understanding by asking follow-up questions.
Encourage learning and celebrate progress.""",
    
    "coder": """You are NexusAI, an expert programming assistant. 💻

Focus on clean, efficient, and well-documented code.
Always explain your code with comments.
Follow best practices and design patterns.
Suggest optimizations and potential improvements.
Be precise with technical terminology.""",
}

# =============================================================================
# AI MODES - User-facing mode selector with icons, colors, and prompts
# =============================================================================
AI_MODES = {
    "assistant": {
        "name": "Assistant",
        "icon": "✨",
        "avatar": "✨",
        "color": "#6366f1",
        "gradient": "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "description": "General-purpose helpful assistant",
        "prompt": DEFAULT_SYSTEM_PROMPT
    },
    "tutor": {
        "name": "Tutor",
        "icon": "🧠",
        "avatar": "🧠",
        "color": "#10b981",
        "gradient": "linear-gradient(135deg, #10b981, #34d399)",
        "description": "Patient teacher that explains concepts clearly",
        "prompt": """You are NexusAI in Tutor Mode - a patient, encouraging educational assistant. 🧠

Teaching approach:
- Break complex topics into digestible steps
- Use analogies and real-world examples
- Ask questions to check understanding
- Celebrate progress and encourage curiosity
- Provide practice problems when appropriate
- Adapt explanations to the learner's level

Always explain the "why" behind concepts, not just the "what".
If a student makes a mistake, guide them to the correct answer rather than giving it directly.
Use markdown with headers and bullet points for clear structure."""
    },
    "coder": {
        "name": "Code Assistant",
        "icon": "💻",
        "avatar": "💻",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b, #fbbf24)",
        "description": "Expert programmer for coding tasks",
        "prompt": """You are NexusAI in Code Assistant Mode - an expert software engineer. 💻

Coding approach:
- Write clean, efficient, well-documented code
- Follow best practices and design patterns
- Explain code with clear comments
- Suggest optimizations and improvements
- Consider edge cases and error handling
- Use proper naming conventions

Always provide:
- Working code examples with syntax highlighting
- Brief explanation of the approach
- Time/space complexity when relevant
- Alternative solutions if applicable

Languages: Python, JavaScript, TypeScript, Java, C++, Go, Rust, SQL, and more."""
    },
    "analyst": {
        "name": "Analyst",
        "icon": "📊",
        "avatar": "📊",
        "color": "#3b82f6",
        "gradient": "linear-gradient(135deg, #3b82f6, #60a5fa)",
        "description": "Data-driven analysis and insights",
        "prompt": """You are NexusAI in Analyst Mode - a sharp data analyst and researcher. 📊

Analysis approach:
- Focus on data, facts, and evidence
- Provide structured, logical analysis
- Use tables and visualizations when helpful
- Quantify findings with numbers and percentages
- Identify patterns, trends, and anomalies
- Consider multiple perspectives

Always provide:
- Clear executive summary
- Key findings and insights
- Supporting data/evidence
- Recommendations or next steps
- Limitations and caveats

Be objective and let the data speak."""
    },
    "writer": {
        "name": "Writer",
        "icon": "✍️",
        "avatar": "✍️",
        "color": "#ec4899",
        "gradient": "linear-gradient(135deg, #ec4899, #f472b6)",
        "description": "Creative writing and content creation",
        "prompt": """You are NexusAI in Writer Mode - a creative wordsmith and content creator. ✍️

Writing approach:
- Craft engaging, well-structured content
- Adapt tone and style to the context
- Use vivid language and compelling narratives
- Pay attention to flow and readability
- Be creative but purposeful

Capabilities:
- Blog posts, articles, essays
- Marketing copy and taglines
- Stories and creative fiction
- Professional emails and documents
- Social media content
- Editing and proofreading

Always consider the target audience and purpose of the writing."""
    }
}


def get_mode_prompt(mode: str) -> str:
    """Get the system prompt for a specific mode."""
    if mode in AI_MODES:
        return AI_MODES[mode]["prompt"]
    return DEFAULT_SYSTEM_PROMPT


def get_mode_avatar(mode: str) -> str:
    """Get the avatar emoji for a specific mode."""
    if mode in AI_MODES:
        return AI_MODES[mode]["avatar"]
    return "✨"


def detect_mode_from_prompt(prompt: str) -> str:
    """
    Auto-detect the best AI mode based on user's prompt.
    Returns the mode key (assistant, tutor, coder, analyst, writer).
    """
    prompt_lower = prompt.lower().strip()
    
    # Code-related keywords → Coder mode (ALL languages!)
    code_keywords = [
        # General coding terms
        'code', 'coding', 'programming', 'programmer', 'developer', 'development',
        'function', 'class', 'method', 'api', 'bug', 'debug', 'error', 'fix', 'script',
        'algorithm', 'data structure', 'compile', 'syntax', 'variable', 'loop', 'array',
        '/run', 'write code', 'code for', 'program to', 'script to', 'implement',
        # Popular languages
        'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'csharp',
        'rust', 'go', 'golang', 'kotlin', 'swift', 'ruby', 'php', 'perl',
        'r programming', 'r language', 'scala', 'dart', 'lua', 'haskell',
        # Web technologies
        'html', 'css', 'sass', 'scss', 'tailwind', 'bootstrap',
        'react', 'vue', 'angular', 'svelte', 'nextjs', 'node', 'express', 'django', 'flask',
        # Database
        'sql', 'mysql', 'postgres', 'mongodb', 'redis', 'database', 'query',
        # Shell/scripting
        'bash', 'shell', 'powershell', 'terminal', 'command line', 'cli',
        # DevOps/tools
        'git', 'docker', 'kubernetes', 'aws', 'azure', 'linux', 'regex'
    ]
    if any(kw in prompt_lower for kw in code_keywords):
        return "coder"
    
    # Teaching/explanation keywords → Tutor mode
    tutor_keywords = [
        'explain', 'teach', 'learn', 'understand', 'why does', 'how does',
        'what is', 'what are', 'define', 'meaning of', 'concept', 'theory',
        'example of', 'help me understand', 'break down', 'simplify',
        'step by step', 'tutorial', 'lesson', 'study', 'homework', 'exam',
        'quiz', 'test', 'practice', 'exercise'
    ]
    if any(kw in prompt_lower for kw in tutor_keywords):
        return "tutor"
    
    # Analysis/data keywords → Analyst mode
    analyst_keywords = [
        'analyze', 'analysis', 'data', 'statistics', 'compare', 'contrast',
        'evaluate', 'assess', 'metrics', 'report', 'chart', 'graph',
        'trend', 'pattern', 'insight', 'conclusion', 'findings', 'research',
        'survey', 'study', 'percentage', 'growth', 'decline', 'forecast',
        'pros and cons', 'advantages', 'disadvantages', 'swot'
    ]
    if any(kw in prompt_lower for kw in analyst_keywords):
        return "analyst"
    
    # Creative writing keywords → Writer mode
    writer_keywords = [
        'write', 'essay', 'story', 'poem', 'article', 'blog', 'content',
        'creative', 'draft', 'compose', 'letter', 'email', 'message',
        'headline', 'tagline', 'slogan', 'caption', 'description',
        'narrative', 'script', 'dialogue', 'fiction', 'rewrite', 'edit',
        'proofread', 'summarize', 'paraphrase', 'translate'
    ]
    if any(kw in prompt_lower for kw in writer_keywords):
        return "writer"
    
    # Default to assistant mode
    return "assistant"


def get_personality_prompt(personality: str, custom_prompt: str = None) -> str:
    """Get the system prompt based on selected personality."""
    if personality == "custom" and custom_prompt:
        return custom_prompt
    return PERSONALITY_PROMPTS.get(personality, DEFAULT_SYSTEM_PROMPT)

FILE_CONTEXT_PROMPT = """
The user has uploaded files for analysis. Carefully read and understand the content before responding.
Reference specific parts of the files when answering questions about them.
"""

RAG_CONTEXT_PROMPT = """
You have access to a knowledge base. Use the retrieved context to provide accurate answers.
If the context doesn't contain relevant information, say so and answer based on your general knowledge.
"""

WEB_SEARCH_CONTEXT_PROMPT = """
I've searched the web for current information. Use these results to provide up-to-date answers:
"""

# UI Text
WELCOME_TITLE = "How can I help you today?"
WELCOME_SUBTITLE = "I'm ready to answer questions, write code, and help with creative tasks."

# Quick action prompts
QUICK_ACTIONS = [
    {"label": "💡 Explain", "prompt": "Explain how machine learning works in simple terms"},
    {"label": "💻 Code", "prompt": "Write a Python function to sort a list using merge sort"},
    {"label": "✍️ Write", "prompt": "Write a professional email requesting a meeting"},
    {"label": "🎨 Image", "prompt": "/image a futuristic city at sunset with flying cars"},
]

# Error messages
ERROR_NO_API_KEY = """
⚠️ API key not configured. Please add your API key to the .env file:

1. Open the `.env` file in the project root
2. Add: `{provider}_API_KEY=your_key_here`
3. Restart the application

Get free API keys:
- Groq: https://console.groq.com/
- Gemini: https://aistudio.google.com/app/apikey
"""

ERROR_RATE_LIMIT = "📊 Rate limit reached. Please wait a moment before trying again."
ERROR_INVALID_KEY = "❌ Invalid API key. Please check your configuration."
ERROR_NETWORK = "🌐 Network error. Please check your internet connection."

# File handling
SUPPORTED_FILE_TYPES = [
    "txt", "md", "py", "js", "ts", "html", "css", "json", "yaml", "yml",
    "csv", "xml", "sql", "sh", "bash", "dockerfile", "gitignore",
    "pdf", "docx", "doc"
]

MAX_FILE_SIZE_MB = 10
MAX_FILES_PER_UPLOAD = 5

# Voice recognition
SUPPORTED_LANGUAGES = [
    ("en-US", "English (US)"),
    ("en-GB", "English (UK)"),
    ("hi-IN", "Hindi"),
]

# Token limits (approximate)
TOKEN_LIMITS = {
    "llama-3.3-70b-versatile": 32768,
    "llama-3.1-8b-instant": 8192,
    "mixtral-8x7b-32768": 32768,
    "gemini-2.0-flash": 1000000,
    "gemini-1.5-flash": 1000000,
    "gemini-1.5-pro": 2000000,
}
