"""
UI Components for NexusAI chatbot.
Extracted from main app.py for better organization.
"""

import streamlit as st
from typing import Optional, List, Dict
from utils.sanitize import sanitize_filename


def render_token_counter(prompt_tokens: int = 0, completion_tokens: int = 0, total_session_tokens: int = 0):
    """
    Render token usage display in sidebar.
    
    Args:
        prompt_tokens: Tokens used in prompt
        completion_tokens: Tokens in response
        total_session_tokens: Running total for session
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Token Usage")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Last Request", f"{prompt_tokens + completion_tokens:,}")
    with col2:
        st.metric("Session Total", f"{total_session_tokens:,}")
    
    # Cost estimate (approximate)
    # Groq: Free tier, Gemini: ~$0.075 per 1M tokens
    estimated_cost = total_session_tokens * 0.000000075
    if estimated_cost > 0.001:
        st.sidebar.caption(f"Est. cost: ${estimated_cost:.4f}")


def render_file_badge(uploaded_files: List[Dict]):
    """
    Render the uploaded file badge above chat input.
    
    Args:
        uploaded_files: List of {name, content} dicts
    """
    if not uploaded_files:
        return
    
    file_count = len(uploaded_files)
    
    if file_count == 1:
        badge_text = sanitize_filename(uploaded_files[0]["name"])
    else:
        names = [sanitize_filename(f["name"]) for f in uploaded_files[:3]]
        if file_count > 3:
            badge_text = f"{', '.join(names)} +{file_count - 3} more"
        else:
            badge_text = ', '.join(names)
    
    st.markdown(f"""
    <div style="position: fixed; bottom: 75px; left: 50%; transform: translateX(-50%); 
                background: linear-gradient(135deg, #2d2e30, #1f2021); 
                border: 1px solid #4285f4; border-radius: 16px; 
                padding: 5px 12px; z-index: 1001; display: flex; align-items: center; gap: 6px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.3);">
        <span style="color: #4285f4;">📎</span>
        <span style="color: #e3e3e3; font-size: 12px;">{badge_text}</span>
        <span style="color: #9aa0a6; font-size: 11px;">({file_count} file{'s' if file_count > 1 else ''})</span>
    </div>
    """, unsafe_allow_html=True)


def render_image_preview(image_data: bytes, filename: str):
    """
    Render image thumbnail preview.
    
    Args:
        image_data: Raw image bytes
        filename: Name of the image file
    """
    import base64
    
    b64_image = base64.b64encode(image_data).decode()
    
    st.markdown(f"""
    <div style="position: fixed; bottom: 120px; left: 50%; transform: translateX(-50%);
                background: #1e1f20; border: 1px solid #4285f4; border-radius: 12px;
                padding: 8px; z-index: 1002; display: flex; align-items: center; gap: 10px;">
        <img src="data:image/png;base64,{b64_image}" 
             style="max-width: 80px; max-height: 60px; border-radius: 8px; object-fit: cover;">
        <div>
            <div style="color: #e3e3e3; font-size: 12px; font-weight: 500;">{filename}</div>
            <div style="color: #9aa0a6; font-size: 10px;">Image attached</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_conversation_history_sidebar(conversations: List[Dict]):
    """
    Render conversation history in sidebar.
    
    Args:
        conversations: List of conversation dicts from chat_db
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Recent Chats")
    
    if not conversations:
        st.sidebar.caption("No saved conversations")
        return
    
    for conv in conversations[:10]:
        title = conv.get('title', 'Untitled')[:30]
        if len(conv.get('title', '')) > 30:
            title += '...'
        
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.button(f"📝 {title}", key=f"conv_{conv['id']}", use_container_width=True):
                st.session_state.current_conversation_id = conv['id']
                st.session_state.load_conversation = True
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv['id']}"):
                st.session_state.delete_conversation_id = conv['id']
                st.rerun()


def get_floating_toolbar_html() -> str:
    """
    Get the HTML/CSS/JS for the floating toolbar.
    Consolidated from multiple inline components.
    
    Returns:
        Complete HTML string for toolbar
    """
    return """
    <script>
    (function() {
        var doc = window.parent.document;
        
        // Only add if not already present
        if (doc.getElementById('nexus-toolbar')) return;
        
        // Add styles
        var style = doc.createElement('style');
        style.textContent = `
            :root {
                --ui-bg: #1a1a1b;
                --ui-contrast: rgba(255,255,255,0.04);
                --ui-contrast-strong: rgba(255,255,255,0.08);
                --fg: #e8eaed;
                --muted: #9aa0a6;
                --shadow: 0 8px 32px rgba(0,0,0,0.4);
            }
            
            .nexus-toolbar {
                position: fixed;
                bottom: 90px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(145deg, var(--ui-bg), #151516);
                border-radius: 40px;
                padding: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: var(--shadow);
                z-index: 99999;
                min-width: 200px;
                max-width: 92%;
                justify-content: center;
                border: 1px solid rgba(255,255,255,0.06);
            }
            
            .nexus-btn {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: var(--ui-contrast);
                color: var(--muted);
                cursor: pointer;
                transition: transform 0.14s ease, background 0.12s ease;
                outline: none;
            }
            
            .nexus-btn:hover {
                background: var(--ui-contrast-strong);
                color: var(--fg);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.45);
            }
            
            .nexus-mic-btn.recording {
                background: linear-gradient(135deg, #ea4335, #d33426) !important;
                color: white !important;
                animation: mic-pulse 1.2s infinite;
            }
            
            @keyframes mic-pulse {
                0% { box-shadow: 0 0 0 0 rgba(234,67,53,0.4); }
                50% { box-shadow: 0 0 0 10px transparent; }
                100% { box-shadow: 0 0 0 0 transparent; }
            }
            
            #nexus-status {
                position: fixed;
                bottom: 145px;
                left: 50%;
                transform: translateX(-50%);
                background: #1e1f20;
                border: 1px solid #4285f4;
                border-radius: 8px;
                padding: 8px 16px;
                color: white;
                font-size: 13px;
                display: none;
                z-index: 99999;
            }
        `;
        doc.head.appendChild(style);
        
        // Create status element
        var status = doc.createElement('div');
        status.id = 'nexus-status';
        doc.body.appendChild(status);
        
        // Create toolbar
        var toolbar = doc.createElement('div');
        toolbar.id = 'nexus-toolbar';
        toolbar.className = 'nexus-toolbar';
        toolbar.innerHTML = `
            <button type="button" class="nexus-btn" id="nexus-upload-btn" title="Upload file">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 5 17 10"/>
                    <line x1="12" y1="5" x2="12" y2="19"/>
                </svg>
            </button>
            <button type="button" class="nexus-btn nexus-mic-btn" id="nexus-mic-btn" title="Voice input">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
            </button>
        `;
        doc.body.appendChild(toolbar);
        
        // Event handlers
        doc.getElementById('nexus-upload-btn').onclick = function() {
            var inputs = doc.querySelectorAll('input[type="file"]');
            if (inputs.length > 0) inputs[0].click();
        };
        
        // Keyboard shortcuts
        doc.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                var textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
                if (textarea && textarea.value.trim()) {
                    var sendBtn = doc.querySelector('[data-testid="stChatInput"] button[kind="primary"]');
                    if (sendBtn) sendBtn.click();
                }
                e.preventDefault();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                window.parent.location.href = window.parent.location.pathname + '?action=new_chat&t=' + Date.now();
                e.preventDefault();
            }
        });
        
        // Voice recognition
        var rec = null, listening = false;
        doc.getElementById('nexus-mic-btn').onclick = function() {
            var btn = this;
            var stat = doc.getElementById('nexus-status');
            var SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
            
            if (!SR) { 
                stat.textContent = '❌ Voice input requires Chrome or Edge browser';
                stat.style.display = 'block';
                setTimeout(function() { stat.style.display = 'none'; }, 3000);
                return; 
            }
            
            if (!rec) {
                rec = new SR();
                rec.continuous = false;
                rec.interimResults = true;
                rec.lang = 'en-US';  // Set language for better recognition
                rec.maxAlternatives = 1;
                
                rec.onstart = function() {
                    listening = true;
                    btn.classList.add('recording');
                    stat.textContent = '🎤 Listening...';
                    stat.style.display = 'block';
                };
                
                rec.onresult = function(e) {
                    var text = '';
                    for (var i = e.resultIndex; i < e.results.length; i++) {
                        text += e.results[i][0].transcript;
                    }
                    stat.textContent = '✓ ' + text;
                    
                    // Find and update the Streamlit chat input textarea
                    var textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
                    if (textarea) {
                        // Set value using native setter to trigger React state update
                        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(textarea, text);
                        
                        // Dispatch input event to notify React
                        var inputEvent = new Event('input', { bubbles: true, cancelable: true });
                        textarea.dispatchEvent(inputEvent);
                        
                        // Also trigger change event
                        var changeEvent = new Event('change', { bubbles: true });
                        textarea.dispatchEvent(changeEvent);
                        
                        textarea.focus();
                    }
                };
                
                rec.onend = function() {
                    listening = false;
                    btn.classList.remove('recording');
                    setTimeout(function() { stat.style.display = 'none'; }, 1500);
                };
                
                rec.onerror = function(e) {
                    listening = false;
                    btn.classList.remove('recording');
                    var errorMsg = e.error;
                    if (e.error === 'not-allowed') {
                        errorMsg = 'Microphone access denied. Please allow microphone access.';
                    } else if (e.error === 'no-speech') {
                        errorMsg = 'No speech detected. Try again.';
                    } else if (e.error === 'network') {
                        errorMsg = 'Network error. Check your connection.';
                    }
                    stat.textContent = '❌ ' + errorMsg;
                    setTimeout(function() { stat.style.display = 'none'; }, 3000);
                };
            }
            
            if (listening) rec.stop();
            else rec.start();
        };
    })();
    </script>
    """


def get_tts_script(text: str) -> str:
    """
    Generate text-to-speech JavaScript.
    
    Args:
        text: Text to speak (will be cleaned)
        
    Returns:
        JavaScript code for TTS
    """
    import re
    
    # Clean markdown formatting
    clean_text = re.sub(r'\*\*|__|\\*|_|`|#|>|-|\|', '', text)
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)  # Links
    clean_text = re.sub(r'```[\s\S]*?```', 'code block', clean_text)  # Code blocks
    clean_text = clean_text[:1500]  # Limit
    
    # Escape for JavaScript
    clean_text = clean_text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').replace('\r', '')
    
    return f"""
    <script>
    (function() {{
        var text = '{clean_text}';
        if (window.parent.speechSynthesis) {{
            window.parent.speechSynthesis.cancel();
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            var voices = window.parent.speechSynthesis.getVoices();
            var voice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft') || v.lang.startsWith('en'));
            if (voice) utterance.voice = voice;
            window.parent.speechSynthesis.speak(utterance);
        }}
    }})();
    </script>
    """
