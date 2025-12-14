"""
Premium Sidebar Module
Enhanced sidebar with glassmorphism and smooth interactions.
"""

import streamlit as st
from typing import List, Dict, Callable
from datetime import datetime


def render_sidebar(
    on_new_chat: Callable = None,
    on_clear_chat: Callable = None,
    on_load_chat: Callable = None,
    chat_history: List[Dict] = None,
    settings: Dict = None
):
    """
    Render the premium sidebar.
    
    Args:
        on_new_chat: Callback for new chat button
        on_clear_chat: Callback for clear chat button
        on_load_chat: Callback for loading a chat (receives chat_id)
        chat_history: List of previous chats
        settings: Current settings dict
    """
    with st.sidebar:
        # Apply sidebar-specific styles
        st.markdown("""
        <style>
        /* Premium Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d0d0f 0%, #131416 100%) !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem !important;
        }
        
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(99, 102, 241, 0.1) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            color: #a5b4fc !important;
            border-radius: 12px !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(99, 102, 241, 0.2) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            transform: translateX(4px);
        }
        
        /* Selectbox styling */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.03) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        render_header()
        render_menu(on_new_chat, on_clear_chat)
        
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("✨ New Chat", use_container_width=True, key="sb_new"):
            if on_new_chat:
                on_new_chat()
        
        # Mode Selector - REMOVED (now automatic based on prompts)
        # st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
        # render_mode_selector()
        
        # Chat History
        if chat_history:
            st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
            render_chat_history(chat_history, on_load_chat)
        
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        # Settings
        render_settings(settings)
        
        # File Manager (show uploaded files with remove option)
        render_file_manager()
        
        # Export Section
        render_export_section()
        
        # Admin Panel (metrics & analytics)
        render_admin_panel()
        
        # Footer
        render_footer()


def render_header():
    """Render premium sidebar header with animated logo."""
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 4px 16px 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 16px;
    ">
        <div style="
            font-size: 2rem;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 3s ease infinite;
            filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.4));
        ">✦</div>
        <div>
            <div style="
                font-size: 1.25rem; 
                font-weight: 600; 
                color: #f0f0f0;
                letter-spacing: -0.02em;
            ">NexusAI</div>
            <div style="
                font-size: 0.7rem; 
                color: #6366f1;
                font-weight: 500;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            ">Production v4.0</div>
        </div>
    </div>
    
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_menu(on_new_chat: Callable = None, on_clear_chat: Callable = None):
    """Render hamburger menu with premium styling."""
    col1, col2 = st.columns([4, 1])
    
    with col2:
        # Use expander instead of popover for HF Spaces compatibility
        with st.expander("⋮", expanded=False):
            st.markdown("""
            <div style="
                color: #f0f0f0; 
                font-weight: 600; 
                font-size: 14px;
                margin-bottom: 8px;
            ">Menu</div>
            """, unsafe_allow_html=True)
            
            if st.button("➕ New Chat", key="menu_new", use_container_width=True):
                if on_new_chat:
                    on_new_chat()
            
            if st.button("🗑️ Clear Chat", key="menu_clear", use_container_width=True):
                if on_clear_chat:
                    on_clear_chat()
            
            st.markdown("""
            <div style="
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            ">
                <div style="color: #6b7280; font-size: 11px; font-weight: 500; margin-bottom: 6px;">
                    SHORTCUTS
                </div>
                <div style="color: #8b8d93; font-size: 12px; line-height: 1.8;">
                    <kbd style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">Ctrl+N</kbd> New Chat<br>
                    <kbd style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">Ctrl+Enter</kbd> Send<br>
                    <kbd style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">Ctrl+M</kbd> Voice
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_mode_selector():
    """Render AI Mode Selector with visual cards."""
    from config.constants import AI_MODES
    
    # Get current mode
    current_mode = st.session_state.get("ai_mode", "assistant")
    current_config = AI_MODES.get(current_mode, AI_MODES["assistant"])
    
    # Header
    st.markdown(f"""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">🎭 AI Mode</div>
    """, unsafe_allow_html=True)
    
    # Current mode display
    st.markdown(f"""
    <div style="
        background: {current_config['gradient']};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    ">
        <span style="font-size: 24px;">{current_config['icon']}</span>
        <div>
            <div style="color: white; font-weight: 600; font-size: 14px;">{current_config['name']}</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 11px;">{current_config['description']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mode selector grid
    cols = st.columns(5)
    for i, (mode_key, mode_config) in enumerate(AI_MODES.items()):
        with cols[i]:
            is_selected = mode_key == current_mode
            btn_style = f"""
            <div style="
                text-align: center;
                padding: 8px 4px;
                border-radius: 10px;
                cursor: pointer;
                background: {'rgba(99, 102, 241, 0.2)' if is_selected else 'rgba(255,255,255,0.03)'};
                border: 1px solid {mode_config['color'] if is_selected else 'rgba(255,255,255,0.05)'};
                transition: all 0.2s;
            ">
                <div style="font-size: 20px;">{mode_config['icon']}</div>
                <div style="font-size: 9px; color: {'#e0e0e0' if is_selected else '#6b7280'}; margin-top: 4px;">{mode_config['name'].split()[0]}</div>
            </div>
            """
            st.markdown(btn_style, unsafe_allow_html=True)
            
            if st.button("", key=f"mode_{mode_key}", use_container_width=True, help=mode_config['description']):
                st.session_state.ai_mode = mode_key
                st.toast(f"Mode: {mode_config['icon']} {mode_config['name']}", icon="🎭")
                st.rerun()


def render_chat_history(history: List[Dict], on_load: Callable = None):
    """Render premium chat history list."""
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">Recent Chats</div>
    """, unsafe_allow_html=True)
    
    for chat in reversed(history[-5:]):
        title = chat.get("title", "Untitled")[:28]
        if len(chat.get("title", "")) > 28:
            title += "..."
        
        if st.button(f"💬 {title}", key=f"h_{chat['id']}", use_container_width=True):
            if on_load:
                on_load(chat["id"])


def render_settings(current_settings: Dict = None):
    """Render premium settings panel with glassmorphism."""
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    ">Settings</div>
    """, unsafe_allow_html=True)
    
    settings = current_settings or {}
    
    # Provider Selection
    providers = ["⚡ Groq (Fast)", "🧠 Gemini (Smart)"]
    current_idx = 0 if settings.get("provider") == "groq" else 1
    
    provider = st.selectbox(
        "AI Provider",
        providers,
        index=current_idx,
        key="setting_provider",
        label_visibility="collapsed"
    )
    
    st.session_state.provider = "groq" if "Groq" in provider else "gemini"
    
    # Model Selection
    if st.session_state.provider == "groq":
        models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    else:
        # Use only models that are confirmed working
        models = ["gemini-2.0-flash-exp", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"]
    
    current_model = settings.get("model", models[0])
    if current_model not in models:
        current_model = models[0]
    
    st.session_state.model = st.selectbox(
        "Model",
        models,
        index=models.index(current_model) if current_model in models else 0,
        key="setting_model",
        label_visibility="collapsed"
    )
    
    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    
    # Feature Toggles - Vertical layout for better readability
    st.session_state.use_rag = st.toggle(
        "🧠 RAG Mode",
        value=settings.get("use_rag", False),
        help="Enable Knowledge Base retrieval",
        key="setting_rag"
    )
    
    st.session_state.tts_enabled = st.toggle(
        "🔊 Text-to-Speech",
        value=settings.get("tts_enabled", True),
        help="Read responses aloud",
        key="setting_tts"
    )
    
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # ========== USER PREFERENCES (ChatGPT 5.2 Feature #6) ==========
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    ">💡 Response Preferences</div>
    """, unsafe_allow_html=True)
    
    # Verbosity preference
    verbosity = st.select_slider(
        "Response Length",
        options=["short", "normal", "detailed"],
        value=settings.get("verbosity", "normal"),
        key="setting_verbosity",
        help="How detailed should responses be?"
    )
    st.session_state.verbosity = verbosity
    
    # Language preference
    language = st.selectbox(
        "Language Style",
        options=["english", "hinglish", "formal"],
        index=["english", "hinglish", "formal"].index(settings.get("language", "english")),
        key="setting_language",
        label_visibility="collapsed"
    )
    st.session_state.language = language
    
    # Update memory service with preferences
    try:
        from services.memory_service import get_memory_service
        memory = get_memory_service()
        memory.update_preference("verbosity", verbosity)
        memory.update_preference("language", language)
        if verbosity == "short":
            memory.preferences.prefer_bullet_points = True
    except Exception:
        pass
    
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # ==================== AVATAR CUSTOMIZATION ====================
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">👤 Your Avatar</div>
    """, unsafe_allow_html=True)
    
    avatar_options = {
        "👤": "Default User",
        "😊": "Smiling",
        "🧑‍💻": "Developer",
        "🎨": "Creative",
        "🚀": "Explorer",
        "💼": "Professional",
        "🦸": "Hero",
        "🤖": "Robot",
    }
    
    current_avatar = settings.get("user_avatar", "👤")
    avatar_labels = [f"{k} {v}" for k, v in avatar_options.items()]
    avatar_keys = list(avatar_options.keys())
    
    if current_avatar not in avatar_keys:
        current_avatar = "👤"
    
    selected_avatar = st.selectbox(
        "Avatar",
        avatar_labels,
        index=avatar_keys.index(current_avatar),
        key="setting_avatar",
        label_visibility="collapsed"
    )
    
    # Extract emoji from selection
    st.session_state.user_avatar = selected_avatar.split()[0]
    
    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    
    # AI Avatar
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">✨ AI Avatar</div>
    """, unsafe_allow_html=True)
    
    ai_avatar_options = {
        "✨": "Sparkle",
        "🤖": "Robot",
        "🧠": "Brain",
        "💡": "Idea",
        "🌟": "Star",
        "🔮": "Crystal Ball",
        "🦾": "Strong AI",
        "👾": "Alien",
    }
    
    current_ai_avatar = settings.get("ai_avatar", "✨")
    ai_avatar_labels = [f"{k} {v}" for k, v in ai_avatar_options.items()]
    ai_avatar_keys = list(ai_avatar_options.keys())
    
    if current_ai_avatar not in ai_avatar_keys:
        current_ai_avatar = "✨"
    
    selected_ai_avatar = st.selectbox(
        "AI Avatar",
        ai_avatar_labels,
        index=ai_avatar_keys.index(current_ai_avatar),
        key="setting_ai_avatar",
        label_visibility="collapsed"
    )
    
    st.session_state.ai_avatar = selected_ai_avatar.split()[0]
    
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # ==================== SYSTEM PROMPT EDITOR ====================
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">🎭 AI Personality</div>
    """, unsafe_allow_html=True)
    
    personality_presets = {
        "default": "🤖 Default Assistant",
        "friendly": "😊 Friendly Helper", 
        "professional": "💼 Professional",
        "creative": "🎨 Creative Writer",
        "teacher": "👨‍🏫 Patient Teacher",
        "coder": "💻 Code Expert",
        "custom": "✏️ Custom..."
    }
    
    current_personality = settings.get("personality", "default")
    if current_personality not in personality_presets:
        current_personality = "default"
    
    selected_personality = st.selectbox(
        "Personality",
        list(personality_presets.values()),
        index=list(personality_presets.keys()).index(current_personality),
        key="setting_personality",
        label_visibility="collapsed"
    )
    
    # Get key from value
    personality_key = list(personality_presets.keys())[list(personality_presets.values()).index(selected_personality)]
    st.session_state.personality = personality_key
    
    # Show custom prompt editor if "Custom" is selected
    if personality_key == "custom":
        st.session_state.custom_system_prompt = st.text_area(
            "Custom System Prompt",
            value=settings.get("custom_system_prompt", "You are a helpful AI assistant."),
            height=100,
            key="setting_custom_prompt",
            placeholder="Describe how the AI should behave..."
        )
    
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # Image Generation Style Selector
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    ">🎨 Image Style</div>
    """, unsafe_allow_html=True)
    
    image_styles = {
        "flux": "✨ Default (Balanced)",
        "flux-realism": "📷 Realistic (Photo-like)",
        "flux-anime": "🎌 Anime Style",
        "flux-3d": "🎮 3D Rendered",
        "turbo": "⚡ Turbo (Fast)"
    }
    
    current_style = settings.get("image_style", "flux")
    if current_style not in image_styles:
        current_style = "flux"
    
    style_names = list(image_styles.values())
    style_keys = list(image_styles.keys())
    
    selected_style = st.selectbox(
        "Image Style",
        style_names,
        index=style_keys.index(current_style) if current_style in style_keys else 0,
        key="setting_image_style",
        label_visibility="collapsed"
    )
    
    # Store the style key (not the display name)
    st.session_state.image_style = style_keys[style_names.index(selected_style)]


def render_file_manager():
    """Render file manager section for viewing and removing uploaded files."""
    uploaded_files = st.session_state.get("uploaded_files", [])
    uploaded_images = st.session_state.get("uploaded_images", [])
    
    total_files = len(uploaded_files) + len(uploaded_images)
    
    if total_files == 0:
        return  # Don't show if no files
    
    # Get RAG service for indexing info
    try:
        from services import get_rag_service
        rag_service = get_rag_service()
        indexed_sources = rag_service.indexed_sources
        total_chunks = rag_service.total_chunks
    except:
        indexed_sources = {}
        total_chunks = 0
    
    # Header with stats
    st.markdown(f"""
    <div style="
        color: #a5b4fc; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 16px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span>📚 Knowledge Base</span>
        <span style="
            background: rgba(99, 102, 241, 0.2);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            color: #c4b5fd;
        ">{total_chunks} chunks</span>
    </div>
    """, unsafe_allow_html=True)
    
    # List uploaded text files with enhanced info
    for i, file in enumerate(uploaded_files):
        file_name = file.get("name", f"File {i+1}")
        content = file.get("content", "")
        content_len = len(content)
        
        # Calculate stats
        tokens_est = content_len // 4
        chunks_count = indexed_sources.get(file_name, 0)
        
        # Determine indexing status
        if chunks_count > 0:
            status = "✅"
            status_text = "Indexed"
            status_color = "#10b981"
        elif total_chunks > 0:
            status = "⏳"
            status_text = "Processing"
            status_color = "#f59e0b"
        else:
            status = "⏳"
            status_text = "Pending"
            status_color = "#6b7280"
        
        # File card
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.04));
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 10px;
            padding: 10px 12px;
            margin: 6px 0;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">📄</span>
                <div style="flex: 1; min-width: 0;">
                    <div style="
                        color: #e0e0e0; 
                        font-size: 12px; 
                        font-weight: 500;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    ">{file_name}</div>
                    <div style="
                        display: flex;
                        gap: 12px;
                        margin-top: 4px;
                        font-size: 10px;
                        color: #6b7280;
                    ">
                        <span>🧩 {chunks_count} chunks</span>
                        <span>📊 ~{tokens_est:,} tokens</span>
                    </div>
                </div>
                <span style="
                    color: {status_color};
                    font-size: 11px;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                ">{status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ View", key=f"view_file_{i}", use_container_width=True):
                st.session_state[f"show_file_{i}"] = not st.session_state.get(f"show_file_{i}", False)
        with col2:
            if st.button("❌ Remove", key=f"remove_file_{i}", use_container_width=True):
                st.session_state.uploaded_files.pop(i)
                # Clear from RAG if possible
                try:
                    from services import reset_rag_service
                    reset_rag_service()
                except:
                    pass
                st.rerun()
        
        # Show file content if expanded
        if st.session_state.get(f"show_file_{i}", False):
            st.markdown(f"""
            <div style="
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 10px;
                margin: 4px 0 8px;
                max-height: 150px;
                overflow-y: auto;
                font-size: 11px;
                color: #9ca3af;
                white-space: pre-wrap;
                font-family: monospace;
            ">{content[:1000]}{'...' if len(content) > 1000 else ''}</div>
            """, unsafe_allow_html=True)
    
    # List uploaded images (simplified)
    for i, img in enumerate(uploaded_images):
        img_name = img.get("name", f"Image {i+1}")
        size_kb = len(img.get("data", b"")) / 1024
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div style="
                font-size: 12px; 
                color: #e0e0e0;
                padding: 6px 10px;
                background: rgba(139, 92, 246, 0.1);
                border-radius: 8px;
                margin: 4px 0;
            ">🖼️ {img_name[:20]}{'...' if len(img_name) > 20 else ''} <span style="color: #6b7280;">({size_kb:.0f}KB)</span></div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑️", key=f"remove_img_{i}", help=f"Remove {img_name}"):
                st.session_state.uploaded_images.pop(i)
                st.rerun()
    
    # Clear all button
    if total_files > 1:
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True, key="clear_all_files"):
            st.session_state.uploaded_files = []
            st.session_state.uploaded_images = []
            try:
                from services import reset_rag_service
                reset_rag_service()
            except:
                pass
            st.rerun()


def render_export_section():
    """Render chat export options with premium styling."""
    messages = st.session_state.get("messages", [])
    
    if not messages:
        return
    
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # Section header
    st.markdown("""
    <div style="
        color: #6b7280; 
        font-size: 11px; 
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    ">📥 Export Chat</div>
    """, unsafe_allow_html=True)
    
    # Import exporter
    try:
        from services.export_service import get_exporter
        exporter = get_exporter()
        
        # Custom styled export buttons container
        st.markdown("""
        <style>
            .export-container {
                display: flex;
                gap: 8px;
                margin-top: 8px;
            }
            .export-btn {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 10px 16px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
            }
            .export-btn-md {
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.2);
                color: #a5b4fc;
            }
            .export-btn-md:hover {
                background: rgba(99, 102, 241, 0.2);
                border-color: rgba(99, 102, 241, 0.4);
            }
            .export-btn-html {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                color: #34d399;
            }
            .export-btn-html:hover {
                background: rgba(16, 185, 129, 0.2);
                border-color: rgba(16, 185, 129, 0.4);
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Markdown export
            md_content = exporter.to_markdown(messages)
            st.download_button(
                "📄 Export",
                data=md_content,
                file_name=f"chat_{st.session_state.get('conversation_id', 'export')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="export_md"
            )
        
        with col2:
            # HTML export
            html_content = exporter.to_html(messages)
            st.download_button(
                "🌐 HTML",
                data=html_content,
                file_name=f"chat_{st.session_state.get('conversation_id', 'export')}.html",
                mime="text/html",
                use_container_width=True,
                key="export_html"
            )
            
    except ImportError:
        st.caption("Export unavailable")


def render_admin_panel():
    """Render admin panel with metrics and export options."""
    try:
        from services.metrics_service import get_metrics_service
        metrics = get_metrics_service()
        summary = metrics.get_session_summary()
        
        # Only show if there are some requests
        if summary.get("total_requests", 0) == 0:
            return
        
        st.markdown("""
        <div style="
            color: #6b7280; 
            font-size: 11px; 
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 16px;
            margin-bottom: 8px;
        ">📊 Session Metrics</div>
        """, unsafe_allow_html=True)
        
        # Compact metrics display
        st.markdown(f"""
        <div style="
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 10px;
            padding: 12px;
            font-size: 12px;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #9ca3af;">Requests</span>
                <span style="color: #e0e0e0; font-weight: 600;">{summary['successful_requests']}/{summary['total_requests']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #9ca3af;">Tokens Used</span>
                <span style="color: #e0e0e0; font-weight: 600;">{summary['total_tokens']:,}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #9ca3af;">Cost</span>
                <span style="color: #10b981; font-weight: 600;">{summary['total_cost_usd']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: #9ca3af;">Error Rate</span>
                <span style="color: {'#f87171' if float(summary['error_rate'].strip('%')) > 10 else '#e0e0e0'}; font-weight: 600;">{summary['error_rate']}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #9ca3af;">RAG Hit Rate</span>
                <span style="color: #e0e0e0; font-weight: 600;">{summary['rag_hit_rate']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Export buttons
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            json_data = metrics.export_json()
            st.download_button(
                "📄 JSON",
                data=json_data,
                file_name=f"metrics_{summary['session_id']}.json",
                mime="application/json",
                use_container_width=True,
                key="export_metrics_json"
            )
        
        with col2:
            csv_data = metrics.export_csv()
            st.download_button(
                "📊 CSV",
                data=csv_data,
                file_name=f"metrics_{summary['session_id']}.csv",
                mime="text/csv",
                use_container_width=True,
                key="export_metrics_csv"
            )
            
    except Exception as e:
        pass  # Silently fail if metrics not available


def render_footer():
    """Render premium sidebar footer."""
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # Token counter
    if st.session_state.get("session_tokens", 0) > 0:
        st.markdown("""
        <div style="
            background: rgba(99, 102, 241, 0.08);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
        ">
            <div style="
                color: #6b7280; 
                font-size: 10px; 
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                margin-bottom: 8px;
            ">Token Usage</div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            last = st.session_state.get("last_tokens", 0)
            st.metric("Last", f"{last:,}", label_visibility="collapsed")
        with col2:
            total = st.session_state.get("session_tokens", 0)
            st.metric("Total", f"{total:,}", label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Version info
    st.markdown("""
    <div style="
        text-align: center;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    ">
        <div style="
            color: #4b5563;
            font-size: 11px;
        ">NexusAI v4.0 • Production</div>
    </div>
    """, unsafe_allow_html=True)
