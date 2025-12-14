"""
NexusAI - Production AI Chat Application
=========================================

A professional AI chat interface with:
- Multi-provider support (Groq, Gemini)
- Real-time web search
- Voice input/output
- File analysis
- Image generation (Pollinations AI - Free)
- User authentication (Supabase)
- Premium UI/UX

Version: 4.0.0 (Refactored Architecture)
"""

import streamlit as st
from datetime import datetime
import re

# Import modular components
from config import settings
from config.constants import QUICK_ACTIONS, DEFAULT_SYSTEM_PROMPT, get_personality_prompt
from services import create_ai_service, get_search_service, create_image_service
from services import get_executor, format_execution_result, extract_code_blocks
from services import get_document_analyzer
from services import create_auth_service, create_database_service
from services import get_rag_service
from ui import (
    apply_styles,
    render_welcome,
    render_quick_actions,
    render_chat_messages,
    render_file_badge,
    render_floating_toolbar,
    render_tts,
    render_sidebar,
)
from ui.auth_ui import render_login_page, render_user_menu, require_auth
from utils.file_processing import extract_text_from_file


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title=settings.app.app_name,
    page_icon=settings.app.app_icon,
    layout=settings.app.layout,
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        # Chat state
        "messages": [],
        "chat_history": [],
        
        # Provider settings
        "provider": settings.ai.default_provider,
        "model": "llama-3.3-70b-versatile",
        "temperature": settings.ai.default_temperature,
        
        # File handling
        "uploaded_files": [],
        "uploaded_images": [],
        
        # Features
        "use_rag": False,
        "tts_enabled": True,
        "speak_response": "",
        
        # Conversation tracking
        "conversation_id": None,
        "db_conversation_id": None,  # Database conversation ID
        
        # Token tracking
        "session_tokens": 0,
        "last_tokens": 0,
        
        # Authentication
        "authenticated": False,
        "user": None,
        "access_token": None,
        "guest_mode": False,
        
        # UI Theme
        "color_theme": "default",
        
        # Avatar Customization
        "user_avatar": "👤",
        "ai_avatar": "✨",
        
        # AI Personality
        "personality": "default",
        "custom_system_prompt": "You are a helpful AI assistant.",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Generate conversation ID if needed
    if not st.session_state.conversation_id:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# CHAT HANDLERS
# =============================================================================
def get_db_service():
    """Get database service if user is logged in."""
    if st.session_state.get("user") and not st.session_state.get("guest_mode"):
        try:
            db = create_database_service()
            if db.is_configured():
                return db
        except:
            pass
    return None


def handle_new_chat():
    """Start a new chat conversation."""
    db = get_db_service()
    user = st.session_state.get("user")
    
    # Save current chat to history (local and/or database)
    if st.session_state.messages:
        title = st.session_state.messages[0]["content"][:30] + "..."
        
        # Save to database if logged in
        if db and user:
            try:
                conv_id = st.session_state.get("db_conversation_id")
                if conv_id:
                    db.update_conversation_title(conv_id, title)
            except:
                pass
        
        # Also save to local history
        st.session_state.chat_history.append({
            "id": st.session_state.conversation_id,
            "title": title,
            "messages": st.session_state.messages.copy()
        })
    
    # Create new conversation in database
    new_conv_id = None
    if db and user:
        try:
            new_conv_id = db.create_conversation(user.id, "New Chat")
        except:
            pass
    
    # Reset state (keep uploaded files for use in new conversation)
    st.session_state.messages = []
    # Note: uploaded_files intentionally NOT cleared to persist across chats
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.db_conversation_id = new_conv_id
    st.rerun()


def handle_clear_chat():
    """Clear current chat (keeps uploaded files)."""
    st.session_state.messages = []
    # Note: uploaded_files intentionally NOT cleared
    st.rerun()


def handle_load_chat(chat_id: str):
    """Load a chat from history or database."""
    db = get_db_service()
    
    # Try database first (for logged-in users)
    if db:
        try:
            messages = db.get_messages_as_dicts(chat_id)
            if messages:
                st.session_state.messages = messages
                st.session_state.db_conversation_id = chat_id
                st.session_state.conversation_id = chat_id
                st.rerun()
                return
        except:
            pass
    
    # Fallback to local history
    for chat in st.session_state.chat_history:
        if chat["id"] == chat_id:
            st.session_state.messages = chat["messages"].copy()
            st.session_state.conversation_id = chat_id
            st.rerun()
            break


def save_message_to_db(role: str, content: str):
    """Save a message to database if user is logged in."""
    db = get_db_service()
    user = st.session_state.get("user")
    
    if not db or not user:
        return
    
    try:
        conv_id = st.session_state.get("db_conversation_id")
        
        # Create conversation if doesn't exist
        if not conv_id:
            title = content[:30] + "..." if len(content) > 30 else content
            conv_id = db.create_conversation(user.id, title)
            st.session_state.db_conversation_id = conv_id
        
        # Save message
        if conv_id:
            db.save_message(conv_id, role, content)
    except Exception as e:
        pass  # Silently fail - don't break chat flow


def is_image_request(text: str) -> tuple[bool, str]:
    """Check if the input is an image generation request."""
    text_lower = text.lower().strip()
    
    # Check for /image command
    if text_lower.startswith("/image "):
        return True, text[7:].strip()
    
    # Check for common image generation phrases (with typo tolerance)
    patterns = [
        # Generate/genrate (common typo)
        r"^gen[e]?rate?\s+(?:an?\s+)?image\s+(?:of\s+)?(.+)",
        r"^gen[e]?rate?\s+(?:an?\s+)?(?:picture|photo|pic)\s+(?:of\s+)?(.+)",
        # Create
        r"^create\s+(?:an?\s+)?image\s+(?:of\s+)?(.+)",
        r"^create\s+(?:an?\s+)?(?:picture|photo|pic)\s+(?:of\s+)?(.+)",
        # Draw
        r"^draw\s+(?:an?\s+)?(?:image\s+(?:of\s+)?)?(.+)",
        # Make
        r"^make\s+(?:an?\s+)?image\s+(?:of\s+)?(.+)",
        r"^make\s+(?:an?\s+)?(?:picture|photo|pic)\s+(?:of\s+)?(.+)",
        # Imagine
        r"^imagine\s+(.+)",
        # "image of" at the start
        r"^image\s+of\s+(.+)",
        r"^picture\s+of\s+(.+)",
        r"^photo\s+of\s+(.+)",
        # Show me
        r"^show\s+(?:me\s+)?(?:an?\s+)?image\s+(?:of\s+)?(.+)",
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text_lower)
        if match:
            return True, match.group(1).strip()
    
    return False, ""


def is_code_request(text: str) -> tuple[bool, str]:
    """Check if the input is a code execution request."""
    text_lower = text.lower().strip()
    
    # Check for /run command
    if text_lower.startswith("/run"):
        # Get code after /run
        code = text[4:].strip()
        if code:
            return True, code
        return False, ""
    
    # Check for ```python code blocks
    code_blocks = extract_code_blocks(text)
    if code_blocks and text_lower.startswith("run"):
        return True, code_blocks[0]
    
    return False, ""


def handle_code_execution(code: str):
    """Execute Python code and display results."""
    # Add user message
    st.session_state.messages.append({
        "role": "user", 
        "content": f"▶️ Run code:\n```python\n{code}\n```"
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"▶️ **Run code:**\n```python\n{code}\n```")
    
    # Execute code
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("⚡ Executing code..."):
            executor = get_executor()
            result = executor.execute(code)
        
        # Format and display result
        formatted = format_execution_result(result)
        st.markdown(formatted)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": formatted
        })


def handle_image_generation(prompt: str):
    """Generate an image and display it in chat."""
    # Get selected style from sidebar (default to 'flux')
    selected_style = st.session_state.get("image_style", "flux")
    style_names = {
        "flux": "Default",
        "flux-realism": "Realistic",
        "flux-anime": "Anime",
        "flux-3d": "3D",
        "turbo": "Turbo"
    }
    style_display = style_names.get(selected_style, "Default")
    
    # Add user message
    st.session_state.messages.append({
        "role": "user", 
        "content": f"🎨 Generate image ({style_display}): {prompt}"
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"🎨 Generate image ({style_display}): **{prompt}**")
    
    # Generate image
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner(f"🎨 Creating your {style_display.lower()} image..."):
            try:
                image_service = create_image_service()
                result = image_service.generate(
                    prompt, 
                    model=selected_style  # Pass the selected style as the model
                )
                
                # Get image bytes for display and download
                import requests
                import base64
                from datetime import datetime
                
                image_bytes = None
                try:
                    if result.url.startswith("data:image"):
                        # Base64 image from Clipdrop
                        image_data = result.url.split(",")[1]
                        image_bytes = base64.b64decode(image_data)
                    else:
                        # URL image from Pollinations
                        response = requests.get(result.url, timeout=30)
                        if response.status_code == 200:
                            image_bytes = response.content
                except Exception as e:
                    pass  # Will use URL fallback
                
                # Display image with constrained size using HTML container
                if image_bytes:
                    import base64
                    img_b64 = base64.b64encode(image_bytes).decode()
                    st.markdown(f'''
                    <div style="max-width: 256px; padding: 8px; background: #1e1e2e; border-radius: 12px; margin: 8px 0;">
                        <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 8px; display: block;">
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    filename = f"nexusai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    st.download_button(
                        label="📥 Download",
                        data=image_bytes,
                        file_name=filename,
                        mime="image/png"
                    )
                else:
                    # Fallback for URL-based images (Pollinations)
                    st.markdown(f'''
                    <div style="max-width: 256px; padding: 8px; background: #1e1e2e; border-radius: 12px; margin: 8px 0;">
                        <img src="{result.url}" style="width: 100%; border-radius: 8px; display: block;">
                    </div>
                    ''', unsafe_allow_html=True)
                    st.markdown(f"[📥 Download]({result.url})")
                
                st.caption(f"✨ {prompt[:40]}... | {result.provider}")
                
                # Store SHORT response (avoid token limit errors)
                response_content = f"[Image: {prompt[:30]}] Generated with {result.provider}"
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
            except Exception as e:
                error_msg = f"❌ Image generation failed: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


def is_image_edit_request(text: str) -> tuple[bool, str]:
    """Check if the input is an image editing request."""
    text_lower = text.lower().strip()
    
    # Check for /edit command
    if text_lower.startswith("/edit "):
        return True, text[6:].strip()
    
    # Check for natural language edit commands
    edit_patterns = [
        r"^edit\s+(?:the\s+)?(?:image|photo|picture)\s+(?:to\s+)?(.+)",
        r"^transform\s+(?:the\s+)?(?:image|photo|picture)\s+(?:to\s+)?(.+)",
        r"^convert\s+(?:the\s+)?(?:image|photo|picture)\s+(?:to\s+)?(.+)",
        r"^change\s+(?:the\s+)?(?:image|photo|picture)\s+(?:to\s+)?(.+)",
        r"^make\s+(?:the\s+)?(?:image|photo|picture)\s+(.+)",
        r"^turn\s+(?:the\s+)?(?:image|photo|picture)\s+into\s+(.+)",
        r"^style\s+(?:the\s+)?(?:image|photo|picture)\s+(?:as\s+)?(.+)",
    ]
    
    for pattern in edit_patterns:
        match = re.match(pattern, text_lower, re.IGNORECASE)
        if match:
            return True, match.group(1)
    
    return False, ""


def handle_image_edit(edit_prompt: str):
    """Edit an uploaded image using Pollinations AI."""
    # Check if there's an uploaded image to edit
    images = st.session_state.get("uploaded_images", [])
    
    if not images:
        st.warning("⚠️ Please upload an image first, then request edits.")
        return
    
    # Get the first uploaded image
    image_data = images[0]
    
    # Get selected style
    selected_style = st.session_state.get("image_style", "flux")
    style_names = {
        "flux": "Default",
        "flux-realism": "Realistic", 
        "flux-anime": "Anime",
        "flux-3d": "3D",
        "turbo": "Turbo"
    }
    style_display = style_names.get(selected_style, "Default")
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": f"✏️ Edit image ({style_display}): {edit_prompt}"
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"✏️ Edit image ({style_display}): **{edit_prompt}**")
    
    # Generate edited image
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner(f"✏️ Applying {style_display.lower()} edits..."):
            try:
                image_service = create_image_service()
                
                # For local uploaded images, we need to describe the edit
                # Since Pollinations works best with prompts, we'll use the 
                # edit prompt as a style transfer description
                enhanced_prompt = f"{edit_prompt}, high quality, detailed"
                
                result = image_service.generate(
                    prompt=enhanced_prompt,
                    model=selected_style
                )
                
                # Display edited image
                st.image(
                    result.url,
                    caption=f"✨ {edit_prompt}",
                    use_container_width=True
                )
                
                response_content = f"Here's your edited image!\\n\\n![{edit_prompt}]({result.url})\\n\\n*Style: {style_display}*"
                st.markdown(f"*Applied **{style_display}** style*")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Clear the uploaded images after processing
                st.session_state.uploaded_images = []
                
            except Exception as e:
                error_msg = f"❌ Image editing failed: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


def handle_image_analysis(user_input: str):
    """Analyze uploaded images using Gemini Vision (only Gemini supports vision currently)."""
    images = st.session_state.uploaded_images
    
    if not images:
        return
    
    # Get AI service - only Gemini has working vision API
    ai_service = create_ai_service()
    gemini_provider = ai_service.providers.get("gemini")
    
    if not gemini_provider or not gemini_provider.is_available():
        st.error("""⚠️ **Image analysis requires Gemini API.**
        
Please add `GEMINI_API_KEY` to your `.env` file.

Note: Groq no longer supports vision models (deprecated).
        """)
        st.session_state.uploaded_images = []
        return
    
    # Display user message with image thumbnails
    image_names = ", ".join([img["name"] for img in images])
    display_message = f"🖼️ *Analyzing {len(images)} image(s): {image_names}*\n\n{user_input}"
    
    st.session_state.messages.append({
        "role": "user",
        "content": display_message
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(display_message)
        # Show image thumbnails
        cols = st.columns(min(len(images), 3))
        for i, img in enumerate(images[:3]):
            with cols[i]:
                st.image(img["data"], caption=img["name"], width=150)
    
    # Analyze with Gemini Vision
    with st.chat_message("assistant", avatar="✨"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Analyze first image
            prompt = user_input if user_input else "Describe this image in detail. What do you see?"
            
            st.caption("🔍 Using Gemini Vision...")
            
            for chunk in gemini_provider.analyze_image(
                image_data=images[0]["data"],
                prompt=prompt,
                model="gemini-2.0-flash-exp"
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str:
                error_msg = "📊 **Gemini quota exceeded.** Please wait a minute and try again."
            else:
                error_msg = f"❌ Image analysis failed: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
        
        finally:
            # Clear uploaded images after analysis
            st.session_state.uploaded_images = []


def render_sources_panel(sources: list, chunks: list = None):
    """
    Render expandable Sources Used panel under AI responses.
    Shows source files, chunk info, and relevance scores.
    """
    if not sources:
        return
    
    # Use chunks list directly
    chunks = chunks or []
    
    # Build sources HTML
    sources_html = []
    for i, source in enumerate(sources):
        # Get relevance score if available
        score = ""
        if i < len(chunks):
            chunk_score = chunks[i].score if hasattr(chunks[i], 'score') else 0
            score_pct = int(chunk_score * 100)
            score_color = "#10b981" if score_pct >= 70 else "#f59e0b" if score_pct >= 50 else "#6b7280"
            score = f'<span style="color: {score_color}; font-size: 10px; margin-left: 8px;">{score_pct}% match</span>'
        
        sources_html.append(f'''
        <div style="
            display: flex;
            align-items: center;
            padding: 6px 10px;
            background: rgba(99, 102, 241, 0.05);
            border-radius: 6px;
            margin: 4px 0;
        ">
            <span style="color: #a5b4fc; margin-right: 8px;">📄</span>
            <span style="color: #e0e0e0; font-size: 12px; flex: 1;">{source}</span>
            {score}
        </div>
        ''')
    
    sources_list = "".join(sources_html)
    
    # Inline citation chips (hover for details)
    chips_html = []
    for i, source in enumerate(sources):
        score_pct = 0
        if i < len(chunks):
            chunk_score = chunks[i].score if hasattr(chunks[i], 'score') else 0
            score_pct = int(chunk_score * 100)
        
        chips_html.append(f'''
        <span class="citation-chip" style="
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            font-size: 11px;
            color: #a5b4fc;
            cursor: pointer;
            transition: all 0.2s ease;
            margin: 2px;
            position: relative;
        " title="{source} ({score_pct}% match)">
            <span style="font-size: 10px;">📄</span>
            <span>{source[:20]}{'...' if len(source) > 20 else ''}</span>
            <span style="
                background: rgba(99, 102, 241, 0.3);
                padding: 1px 5px;
                border-radius: 8px;
                font-size: 9px;
            ">{score_pct}%</span>
        </span>
        ''')
    
    chips_list = "".join(chips_html)
    
    # Render inline chips row
    st.markdown(f'''
    <div style="
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 10px;
        padding: 8px 12px;
        background: rgba(99, 102, 241, 0.05);
        border-radius: 12px;
        align-items: center;
    ">
        <span style="color: #6b7280; font-size: 11px; margin-right: 6px;">📚 Sources:</span>
        {chips_list}
    </div>
    <style>
        .citation-chip:hover {{
            background: rgba(99, 102, 241, 0.25);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
        }}
    </style>
    ''', unsafe_allow_html=True)


def process_user_input(user_input: str):
    """Process user input and generate AI response."""
    # Auto-correct typos (silently, preserves technical terms)
    try:
        from utils.spell_service import correct_user_input
        corrected_input, was_corrected = correct_user_input(user_input)
        if was_corrected:
            user_input = corrected_input
            # Optional: show small toast that correction was applied
            # st.toast(f"Auto-corrected: {corrected_input[:30]}...", icon="✏️")
    except Exception:
        pass  # Spell correction is optional, continue without it
    
    # ========== INTENT DETECTION (ChatGPT 5.2 Feature #1) ==========
    try:
        from services.intent_service import detect_intent, Intent, Confidence
        intent_result = detect_intent(user_input, st.session_state.messages)
        
        # Show detected intent for transparency
        if intent_result.confidence == Confidence.HIGH:
            st.toast(f"Detected: {intent_result.intent.value}", icon="🎯")
        
        # If low confidence and needs clarification, ask first
        if intent_result.requires_clarification and intent_result.clarification_question:
            # Show clarification question instead of answering
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"🤔 {intent_result.clarification_question}"
            })
            return  # Don't process further until clarified
        
        # Store intent for prompt enhancement
        st.session_state.current_intent = intent_result
    except Exception as e:
        logger.debug(f"Intent detection skipped: {e}")
        st.session_state.current_intent = None
    
    # Check for code execution request (/run command)
    is_code, code = is_code_request(user_input)
    if is_code:
        handle_code_execution(code)
        return
    
    # Check for image generation request
    is_image, image_prompt = is_image_request(user_input)
    if is_image and settings.app.enable_image_generation:
        handle_image_generation(image_prompt)
        return
    
    # Check for image edit request (/edit command)
    is_edit, edit_prompt = is_image_edit_request(user_input)
    if is_edit and settings.app.enable_image_generation:
        handle_image_edit(edit_prompt)
        return
    
    # Check for uploaded images - use Gemini Vision
    if st.session_state.uploaded_images:
        handle_image_analysis(user_input)
        return
    
    # Initialize AI service
    ai_service = create_ai_service()
    ai_service.current_provider = st.session_state.provider
    ai_service.current_model = st.session_state.model
    ai_service.temperature = st.session_state.temperature
    
    if not ai_service.is_ready():
        st.error("⚠️ No AI provider configured. Please add API keys to your .env file.")
        return
    
    # Build prompt with file context
    full_prompt = user_input
    display_message = user_input
    rag_sources = []
    
    # Handle uploaded files - use RAG retrieval for better context
    if st.session_state.uploaded_files:
        files = st.session_state.uploaded_files
        
        try:
            rag_service = get_rag_service()
            
            # If RAG has indexed content, use semantic retrieval
            if rag_service.has_indexed_content():
                # Show document reading state indicator
                rag_placeholder = st.empty()
                rag_placeholder.markdown("""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 10px; 
                    padding: 12px 16px;
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.05));
                    border: 1px solid rgba(139, 92, 246, 0.2);
                    border-radius: 12px;
                    margin: 8px 0;
                ">
                    <div style="font-size: 20px; animation: bounce-book 1s infinite;">📚</div>
                    <div>
                        <div style="color: #a78bfa; font-weight: 600; font-size: 13px;">Reading documents</div>
                        <div style="color: #8b8d93; font-size: 11px;">Finding relevant information...</div>
                    </div>
                </div>
                <style>@keyframes bounce-book { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }</style>
                """, unsafe_allow_html=True)
                
                # Retrieve relevant chunks based on query
                rag_context = rag_service.retrieve(user_input, top_k=5, min_score=0.3)
                rag_placeholder.empty()  # Clear indicator
                
                if rag_context.chunks:
                    # Use RAG-enhanced prompt
                    full_prompt = rag_service.get_rag_prompt(user_input, rag_context)
                    rag_sources = rag_context.sources
                    # Save chunks for sources panel
                    st.session_state._rag_chunks = rag_context.chunks
                    display_message = f"📚 *Searching {len(files)} file(s) (RAG enabled)*\n\n{user_input}"
                else:
                    # No relevant chunks found, use direct file content
                    file_content = "\n\n".join([
                        f"--- FILE: {f['name']} ---\n{f['content'][:2000]}..." 
                        for f in files
                    ])
                    full_prompt = f"""I have uploaded files for analysis:

{file_content}

User's question: {user_input}

Please analyze the files and answer the question."""
                    display_message = f"📎 *Analyzing {len(files)} file(s)*\n\n{user_input}"
            else:
                # RAG not indexed, use direct file content (fallback)
                file_content = "\n\n".join([
                    f"--- FILE: {f['name']} ---\n{f['content'][:2000]}..." 
                    for f in files
                ])
                full_prompt = f"""I have uploaded files for analysis:

{file_content}

User's question: {user_input}

Please analyze the files and answer the question."""
                display_message = f"📎 *Analyzing {len(files)} file(s)*\n\n{user_input}"
                
        except Exception as e:
            # RAG error - fallback to direct file content
            file_content = "\n\n".join([
                f"--- FILE: {f['name']} ---\n{f['content'][:2000]}..." 
                for f in files
            ])
            full_prompt = f"""I have uploaded files for analysis:

{file_content}

User's question: {user_input}

Please analyze the files and answer the question."""
            display_message = f"📎 *Analyzing {len(files)} file(s)*\n\n{user_input}"
    
    # Check for web search with explicit state indicator
    search_service = get_search_service()
    search_context = ""
    
    if search_service.should_search(user_input):
        # Show web search state indicator
        search_placeholder = st.empty()
        search_placeholder.markdown("""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding: 12px 16px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.05));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            margin: 8px 0;
        ">
            <div style="font-size: 20px; animation: pulse 1.5s infinite;">🌐</div>
            <div>
                <div style="color: #60a5fa; font-weight: 600; font-size: 13px;">Searching the web</div>
                <div style="color: #8b8d93; font-size: 11px;">Finding latest information...</div>
            </div>
        </div>
        <style>@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.7; transform: scale(1.1); } }</style>
        """, unsafe_allow_html=True)
        
        results = search_service.search(user_input, max_results=8)
        if results:
            search_context = search_service.format_for_context(results)
            full_prompt = f"{search_context}\n\n{full_prompt}"
        
        search_placeholder.empty()  # Clear indicator when done
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": display_message})
    save_message_to_db("user", display_message)
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(display_message)
    
    # Generate and display response
    current_mode = st.session_state.get("ai_mode", "assistant")
    from config.constants import get_mode_avatar
    mode_avatar = get_mode_avatar(current_mode)
    
    with st.chat_message("assistant", avatar=mode_avatar):
        placeholder = st.empty()
        full_response = ""
        
        # Show enhanced thinking indicator
        placeholder.markdown("""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding: 12px 16px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            margin: 8px 0;
        ">
            <div style="font-size: 20px; animation: think 1.5s infinite;">🧠</div>
            <div>
                <div style="color: #a5b4fc; font-weight: 600; font-size: 13px;">Thinking</div>
                <div style="color: #8b8d93; font-size: 11px;">Generating response...</div>
            </div>
            <div style="margin-left: auto; display: flex; gap: 4px;">
                <div style="width: 6px; height: 6px; border-radius: 50%; background: #6366f1; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.32s;"></div>
                <div style="width: 6px; height: 6px; border-radius: 50%; background: #6366f1; animation: bounce 1.4s infinite ease-in-out both; animation-delay: -0.16s;"></div>
                <div style="width: 6px; height: 6px; border-radius: 50%; background: #6366f1; animation: bounce 1.4s infinite ease-in-out both;"></div>
            </div>
        </div>
        <style>
            @keyframes think { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
            @keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
        </style>
        """, unsafe_allow_html=True)
        
        try:
            # Auto-detect mode based on user's prompt
            from config.constants import get_mode_prompt, get_mode_avatar, detect_mode_from_prompt, AI_MODES
            detected_mode = detect_mode_from_prompt(user_input)
            current_mode = st.session_state.get("ai_mode", "assistant")
            
            # Auto-switch mode if different (and show notification)
            if detected_mode != current_mode:
                st.session_state.ai_mode = detected_mode
                mode_info = AI_MODES.get(detected_mode, {})
                mode_name = mode_info.get("name", detected_mode.title())
                mode_icon = mode_info.get("icon", "✨")
                st.toast(f"{mode_icon} Auto-switched to {mode_name} mode", icon="🎭")
            
            # Get mode-based system prompt
            system_prompt = get_mode_prompt(detected_mode)
            mode_avatar = get_mode_avatar(detected_mode)
            
            # ========== INTENT-ENHANCED PROMPT (ChatGPT 5.2 Feature #1) ==========
            intent_result = st.session_state.get("current_intent")
            if intent_result:
                from services.intent_service import get_intent_detector
                detector = get_intent_detector()
                intent_enhancement = detector.get_prompt_enhancement(intent_result)
                if intent_enhancement:
                    system_prompt += f"\n\n[Based on user's intent: {intent_enhancement}]"
            
            # ========== CONTEXT COMPRESSION (ChatGPT 5.2 Feature #2) ==========
            try:
                from services.memory_service import get_memory_service
                memory = get_memory_service()
                compressed_history = memory.prepare_messages_for_api(st.session_state.messages[:-1])
                
                # Add memory context to system prompt
                memory_context = memory.get_context_prompt()
                if memory_context:
                    system_prompt += f"\n\n{memory_context}"
            except Exception:
                compressed_history = st.session_state.messages[:-1]
            
            # Stream response
            for chunk in ai_service.stream(
                full_prompt, 
                history=compressed_history,
                system_prompt=system_prompt
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            
            # Final display
            placeholder.markdown(full_response)
            
            # Show RAG sources panel if we used RAG
            if rag_sources:
                rag_chunks = st.session_state.get('_rag_chunks', [])
                render_sources_panel(rag_sources, rag_chunks)
            
            # Save to history (include sources for later display)
            message_data = {
                "role": "assistant", 
                "content": full_response
            }
            if rag_sources:
                message_data["sources"] = rag_sources
            st.session_state.messages.append(message_data)
            save_message_to_db("assistant", full_response)
            
            # TTS if enabled
            if st.session_state.tts_enabled:
                st.session_state.speak_response = full_response
                
        except Exception as e:
            # Professional error handling - no raw exceptions!
            error_msg = str(e).lower()
            
            # Classify error for user-friendly message
            if "rate" in error_msg or "limit" in error_msg or "429" in str(e):
                error_title = "Rate limit reached"
                error_desc = "The AI service is temporarily busy."
                error_icon = "📊"
            elif "api_key" in error_msg or "invalid" in error_msg or "auth" in error_msg:
                error_title = "Authentication issue"
                error_desc = "There's a problem with the API configuration."
                error_icon = "🔑"
            elif "timeout" in error_msg or "timed out" in error_msg:
                error_title = "Request timed out"
                error_desc = "The AI service took too long to respond."
                error_icon = "⏱️"
            elif "network" in error_msg or "connect" in error_msg:
                error_title = "Connection issue"
                error_desc = "Couldn't reach the AI service."
                error_icon = "🌐"
            else:
                error_title = "Something went wrong"
                error_desc = "An unexpected error occurred."
                error_icon = "⚠️"
            
            # Friendly error card
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 12px;
                padding: 16px 20px;
                margin: 8px 0;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 28px;">{error_icon}</span>
                    <div>
                        <div style="color: #fca5a5; font-weight: 600; font-size: 15px;">{error_title}</div>
                        <div style="color: #9ca3af; font-size: 13px;">{error_desc}</div>
                    </div>
                </div>
                <div style="color: #d1d5db; font-size: 12px; margin-bottom: 12px;">
                    You can try:
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ========== CONVERSATIONAL ERROR SUGGESTIONS (ChatGPT 5.2 Feature #7) ==========
            # Offer context-aware alternatives
            has_files = bool(st.session_state.get("uploaded_files"))
            has_rag = st.session_state.get("use_rag", False)
            
            if "rate" in error_msg or "limit" in error_msg:
                st.info("💡 **Tip:** I'm being rate-limited. Would you like me to try a different AI provider, or should we wait a moment?")
            elif "network" in error_msg or "connect" in error_msg:
                if has_files:
                    st.info("💡 **Tip:** I can't reach the AI service, but you have uploaded files. Would you like me to search your documents offline instead?")
                else:
                    st.info("💡 **Tip:** Check your internet connection and try again.")
            elif has_files and has_rag:
                st.info("💡 **Tip:** The AI service isn't responding. Would you like me to try answering from your uploaded documents only?")
            
            # Recovery action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Retry", key="error_retry", use_container_width=True):
                    st.rerun()
            with col2:
                current_provider = st.session_state.get("provider", "groq")
                new_provider = "gemini" if current_provider == "groq" else "groq"
                if st.button(f"🔀 Switch to {new_provider.title()}", key="error_switch", use_container_width=True):
                    st.session_state.provider = new_provider
                    st.toast(f"Switched to {new_provider.title()}", icon="✅")
                    st.rerun()
            with col3:
                if st.button("💬 New Chat", key="error_new", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
            
            # Remove failed user message from history
            if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
                st.session_state.messages.pop()


# =============================================================================
# FILE UPLOAD HANDLER
# =============================================================================
def handle_file_upload():
    """Handle file uploads including images for vision analysis."""
    uploaded = st.file_uploader(
        "Upload files",
        type=["txt", "md", "py", "js", "json", "csv", "pdf", "png", "jpg", "jpeg", "gif", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader"
    )
    
    if uploaded:
        new_files = []
        new_images = []
        
        # File size limit (10MB)
        MAX_FILE_SIZE_MB = 10
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
        
        for file in uploaded:
            # Check file size
            file_size = file.size if hasattr(file, 'size') else len(file.read())
            if hasattr(file, 'seek'):
                file.seek(0)  # Reset after reading size
            
            if file_size > MAX_FILE_SIZE_BYTES:
                st.error(f"⚠️ File '{file.name}' is too large ({file_size / (1024*1024):.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB")
                continue
            
            file_ext = file.name.lower().split('.')[-1]
            
            # Check if it's an image
            if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                try:
                    image_bytes = file.read()
                    file.seek(0)  # Reset for potential re-read
                    new_images.append({
                        "name": file.name,
                        "data": image_bytes,
                        "type": file_ext
                    })
                except Exception as e:
                    st.error(f"Error reading image {file.name}: {e}")
            else:
                # Regular file
                try:
                    content = extract_text_from_file(file)
                    new_files.append({
                        "name": file.name,
                        "content": content
                    })
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")
        
        if new_files:
            st.session_state.uploaded_files = new_files
            
            # Async-style RAG indexing with progress UI
            try:
                # Show ingestion progress indicator
                ingestion_status = st.empty()
                ingestion_status.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin: 8px 0;
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="font-size: 18px; animation: spin 1s linear infinite;">⚙️</div>
                        <div style="flex: 1;">
                            <div style="color: #a5b4fc; font-weight: 600; font-size: 13px;">
                                Indexing {len(new_files)} file(s) for smart retrieval...
                            </div>
                            <div style="
                                height: 4px;
                                background: rgba(99, 102, 241, 0.2);
                                border-radius: 2px;
                                margin-top: 8px;
                                overflow: hidden;
                            ">
                                <div style="
                                    height: 100%;
                                    width: 100%;
                                    background: linear-gradient(90deg, #6366f1, #8b5cf6);
                                    animation: progressIndeterminate 1.5s ease-in-out infinite;
                                "></div>
                            </div>
                        </div>
                    </div>
                </div>
                <style>
                    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
                    @keyframes progressIndeterminate {{
                        0% {{ transform: translateX(-100%); }}
                        50% {{ transform: translateX(0%); }}
                        100% {{ transform: translateX(100%); }}
                    }}
                </style>
                """, unsafe_allow_html=True)
                
                # Index files
                rag_service = get_rag_service()
                chunks_indexed = rag_service.index_uploaded_files(new_files)
                
                # Clear progress and show success
                ingestion_status.empty()
                
                if chunks_indexed > 0:
                    st.toast(f"📚 Indexed {chunks_indexed} chunks from {len(new_files)} file(s)", icon="✨")
                    
            except Exception as e:
                # Non-blocking error - just log it
                ingestion_status.empty()
                st.toast("⚠️ Indexing skipped - files still available", icon="📁")
                
        if new_images:
            st.session_state.uploaded_images = new_images


# =============================================================================
# URL ACTION HANDLER
# =============================================================================
def handle_url_actions():
    """Process URL query parameters for actions."""
    if hasattr(st, 'query_params'):
        action = st.query_params.get("action")
        
        if action == "new_chat":
            st.session_state.messages = []
            st.session_state.uploaded_files = []
            st.query_params.clear()
            st.rerun()
        
        elif action == "clear_history":
            st.session_state.messages = []
            st.query_params.clear()
            st.rerun()


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point."""
    # Initialize state
    init_session_state()
    
    # Apply styling (default dark theme)
    apply_styles(theme="default")
    
    # ==================== AUTHENTICATION CHECK ====================
    # DISABLED: Skip login page for now - go directly to chat
    # if not require_auth(allow_guest=True):
    #     return  # Stop here - login page is shown
    st.session_state.guest_mode = True  # Always use guest mode
    
    # ==================== LOAD DATABASE CONVERSATIONS ====================
    # Load conversations from database for logged-in users
    if st.session_state.get("user") and not st.session_state.get("guest_mode"):
        if "db_chats_loaded" not in st.session_state:
            try:
                db = create_database_service()
                user = st.session_state.user
                if db.is_configured():
                    db_convos = db.get_conversations(user.id, limit=20)
                    # Add database conversations to chat_history
                    for conv in db_convos:
                        # Check if already in local history
                        if not any(c["id"] == conv.id for c in st.session_state.chat_history):
                            st.session_state.chat_history.append({
                                "id": conv.id,
                                "title": conv.title,
                                "messages": []  # Will load on-demand when selected
                            })
                    st.session_state.db_chats_loaded = True
            except Exception as e:
                pass  # Silently fail - don't block the UI
    
    # Handle URL actions
    handle_url_actions()
    
    # Render sidebar
    render_sidebar(
        on_new_chat=handle_new_chat,
        on_clear_chat=handle_clear_chat,
        on_load_chat=handle_load_chat,
        chat_history=st.session_state.chat_history,
        settings={
            "provider": st.session_state.provider,
            "model": st.session_state.model,
            "use_rag": st.session_state.use_rag,
            "tts_enabled": st.session_state.tts_enabled,
        }
    )
    
    # Show user menu in sidebar (logout button etc.)
    render_user_menu()
    
    # Main content area
    if not st.session_state.messages:
        # Welcome screen
        render_welcome()
        
        # Quick actions
        selected = render_quick_actions(QUICK_ACTIONS)
        if selected:
            ai_service = create_ai_service()
            if ai_service.is_ready():
                process_user_input(selected)
                st.rerun()
            else:
                st.error("⚠️ Please configure your API keys first.")
    else:
        # Chat history with bottom padding
        st.markdown('<div style="padding-bottom: 100px;">', unsafe_allow_html=True)
        render_chat_messages(st.session_state.messages)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload (hidden, triggered by toolbar)
    with st.container():
        handle_file_upload()
    
    # Show file badge if files are uploaded
    if st.session_state.uploaded_files:
        render_file_badge(st.session_state.uploaded_files)
    
    # Floating toolbar (upload + voice buttons)
    render_floating_toolbar()
    
    # Chat input
    if prompt := st.chat_input("Message NexusAI..."):
        process_user_input(prompt)
        # Note: st.rerun() removed - the response is already displayed during streaming
        # and saved to session state. Rerun was causing answers to "disappear" briefly.
    
    # Text-to-speech for response
    if st.session_state.speak_response and st.session_state.tts_enabled:
        render_tts(st.session_state.speak_response)
        st.session_state.speak_response = ""


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()
