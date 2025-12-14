"""
Premium UI Components Module
Animated and enhanced Streamlit UI components.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, List, Dict
import base64


def render_welcome():
    """Render the premium animated welcome screen with floating orbs."""
    st.markdown("""
    <style>
        .welcome-container {
            min-height: 400px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            pointer-events: none;
            z-index: 0;
        }
        
        .orb-1 {
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation: orbFloat 8s ease-in-out infinite;
        }
        
        .orb-2 {
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
            top: 20%;
            left: 70%;
            animation: orbFloat2 10s ease-in-out infinite;
        }
        
        @keyframes orbFloat {
            0%, 100% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-30%, -60%) scale(1.2); }
        }
        
        @keyframes orbFloat2 {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(-30px, 30px) scale(1.3); }
        }
        
        .welcome-icon {
            font-size: 5rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7, #6366f1);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 4s ease infinite, iconPulse 2s ease-in-out infinite;
            filter: drop-shadow(0 0 40px rgba(99, 102, 241, 0.6));
            z-index: 1;
            position: relative;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes iconPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
        }
        
        .welcome-title {
            font-size: 2.5rem;
            font-weight: 600;
            color: #f0f0f0;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
            z-index: 1;
            position: relative;
            animation: fadeSlideUp 0.6s ease-out;
        }
        
        .welcome-subtitle {
            font-size: 1.1rem;
            color: #9aa0a6;
            max-width: 500px;
            line-height: 1.7;
            z-index: 1;
            position: relative;
            animation: fadeSlideUp 0.6s ease-out 0.15s backwards;
        }
        
        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    
    <div class="welcome-container">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="welcome-icon">✦</div>
        <h1 class="welcome-title">How can I help you today?</h1>
        <p class="welcome-subtitle">
            I can write code, answer questions, analyze files, and help with creative tasks.
            Just type below or try a quick action.
        </p>
    </div>
    """, unsafe_allow_html=True)



def render_quick_actions(actions: List[Dict] = None) -> Optional[str]:
    """
    Render animated quick action buttons.
    
    Args:
        actions: List of {"label": str, "prompt": str} dicts
        
    Returns:
        Selected prompt or None
    """
    if actions is None:
        actions = [
            {"label": "💡 Explain a concept", "prompt": "Explain how machine learning works in simple terms"},
            {"label": "💻 Write code", "prompt": "Write a Python function to sort a list using merge sort with comments"},
            {"label": "✍️ Help me write", "prompt": "Write a professional email requesting a meeting with a potential client"},
            {"label": "📊 Compare options", "prompt": "Compare Python vs JavaScript - when to use each?"},
        ]
    
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    
    cols = st.columns(len(actions))
    selected = None
    
    for idx, action in enumerate(actions):
        with cols[idx]:
            if st.button(action["label"], use_container_width=True, key=f"quick_{idx}"):
                selected = action["prompt"]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected


def render_chat_messages(messages: List[Dict]):
    """
    Render chat message history with premium styling.
    
    Args:
        messages: List of {"role": str, "content": str} dicts
    """
    # Get custom avatars from session state
    user_avatar = st.session_state.get("user_avatar", "👤")
    ai_avatar = st.session_state.get("ai_avatar", "✨")
    
    for idx, message in enumerate(messages):
        avatar = user_avatar if message["role"] == "user" else ai_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


def render_file_badge(files: List[Dict]):
    """
    Render premium uploaded file badge with glow effect.
    
    Args:
        files: List of {"name": str, "content": str} dicts
    """
    if not files:
        return
    
    count = len(files)
    names = [f["name"] for f in files[:3]]
    display = ", ".join(names)
    if count > 3:
        display += f" +{count - 3} more"
    
    st.markdown(f"""
    <div style="
        position: fixed;
        bottom: 85px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 24px;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1001;
        box-shadow: 
            0 4px 24px rgba(99, 102, 241, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    ">
        <span style="font-size: 1.2rem;">📎</span>
        <span style="color: #f0f0f0; font-size: 14px; font-weight: 500;">{display}</span>
        <span style="
            background: rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 500;
        ">{count} file{"s" if count > 1 else ""}</span>
    </div>
    
    <style>
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateX(-50%) translateY(10px); }}
        to {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_image_preview(image_data: bytes, filename: str):
    """Render premium image thumbnail preview with glass effect."""
    b64 = base64.b64encode(image_data).decode()
    
    st.markdown(f"""
    <div style="
        position: fixed;
        bottom: 130px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(26, 27, 30, 0.95);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 12px;
        z-index: 1002;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease-out;
    ">
        <img src="data:image/png;base64,{b64}" 
             style="
                max-width: 90px; 
                max-height: 70px; 
                border-radius: 10px; 
                object-fit: cover;
                border: 1px solid rgba(255, 255, 255, 0.1);
             ">
        <div>
            <div style="color: #f0f0f0; font-size: 13px; font-weight: 600;">{filename}</div>
            <div style="color: #8b8d93; font-size: 11px; margin-top: 2px;">Image ready to analyze</div>
        </div>
        <div style="
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 500;
        ">✓ Attached</div>
    </div>
    """, unsafe_allow_html=True)


def render_token_counter(session_tokens: int = 0, last_tokens: int = 0):
    """Render premium token usage display."""
    if session_tokens > 0:
        st.sidebar.markdown("""
        <div style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 12px;
            padding: 12px;
            margin-top: 8px;
        ">
            <div style="color: #8b8d93; font-size: 12px; font-weight: 500; margin-bottom: 8px;">
                📊 Token Usage
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Last", f"{last_tokens:,}")
        with col2:
            st.metric("Total", f"{session_tokens:,}")


def render_loading_skeleton():
    """Render a premium loading skeleton for streaming responses."""
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 16px 0;
    ">
        <div class="skeleton" style="height: 16px; width: 80%; border-radius: 8px;"></div>
        <div class="skeleton" style="height: 16px; width: 65%; border-radius: 8px;"></div>
        <div class="skeleton" style="height: 16px; width: 75%; border-radius: 8px;"></div>
    </div>
    
    <style>
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(99, 102, 241, 0.1) 25%,
            rgba(99, 102, 241, 0.2) 50%,
            rgba(99, 102, 241, 0.1) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_typing_indicator():
    """Render animated typing indicator."""
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
    ">
        <div style="display: flex; gap: 4px;">
            <div class="typing-dot" style="animation-delay: 0s;"></div>
            <div class="typing-dot" style="animation-delay: 0.15s;"></div>
            <div class="typing-dot" style="animation-delay: 0.3s;"></div>
        </div>
        <span style="color: #8b8d93; font-size: 14px;">Thinking...</span>
    </div>
    
    <style>
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        animation: typingBounce 1.4s infinite ease-in-out;
    }
    
    @keyframes typingBounce {
        0%, 80%, 100% { 
            transform: scale(0.6);
            opacity: 0.5;
        }
        40% { 
            transform: scale(1);
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def get_floating_toolbar_js() -> str:
    """Get premium JavaScript for floating toolbar with voice and upload."""
    return """
    <script>
    (function() {
        var doc = window.parent.document;
        if (doc.getElementById('nexus-toolbar')) return;
        
        // Premium styles
        var style = doc.createElement('style');
        style.textContent = `
            .nexus-toolbar {
                position: fixed;
                bottom: 90px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(145deg, rgba(26, 27, 30, 0.95), rgba(19, 20, 22, 0.98));
                backdrop-filter: blur(24px) saturate(180%);
                -webkit-backdrop-filter: blur(24px) saturate(180%);
                border-radius: 24px;
                padding: 8px;
                display: flex;
                align-items: center;
                gap: 6px;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
                z-index: 99999;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            
            .nexus-btn {
                width: 42px;
                height: 42px;
                border-radius: 14px;
                border: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(255, 255, 255, 0.05);
                color: #8b8d93;
                cursor: pointer;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                outline: none;
            }
            
            .nexus-btn:hover {
                background: rgba(99, 102, 241, 0.15);
                color: #a5b4fc;
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
            }
            
            .nexus-btn.recording {
                background: linear-gradient(135deg, #ef4444, #dc2626) !important;
                color: white !important;
                animation: recordPulse 1.5s infinite;
            }
            
            @keyframes recordPulse {
                0%, 100% { 
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
                }
                50% { 
                    box-shadow: 0 0 0 12px transparent;
                }
            }
            
            #nexus-status {
                position: fixed;
                bottom: 145px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(26, 27, 30, 0.95), rgba(19, 20, 22, 0.98));
                backdrop-filter: blur(16px);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 10px 18px;
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 500;
                display: none;
                z-index: 99999;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
        `;
        doc.head.appendChild(style);
        
        // Status element
        var status = doc.createElement('div');
        status.id = 'nexus-status';
        doc.body.appendChild(status);
        
        // Toolbar
        var toolbar = doc.createElement('div');
        toolbar.id = 'nexus-toolbar';
        toolbar.className = 'nexus-toolbar';
        toolbar.innerHTML = `
            <button type="button" class="nexus-btn" id="nexus-upload" title="Upload file (Ctrl+U)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
            </button>
            <button type="button" class="nexus-btn" id="nexus-mic" title="Voice input (Ctrl+M)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
            </button>
        `;
        doc.body.appendChild(toolbar);
        
        // ROBUST Upload handler with retry and visual feedback
        doc.getElementById('nexus-upload').onclick = function() {
            var btn = this;
            btn.style.opacity = '0.5';
            btn.style.pointerEvents = 'none';
            
            // Try multiple selectors to find the file input
            function findAndClickFileInput(attempts) {
                if (attempts <= 0) {
                    btn.style.opacity = '1';
                    btn.style.pointerEvents = 'auto';
                    console.warn('File input not found after retries');
                    return;
                }
                
                // Try multiple selectors
                var input = doc.querySelector('input[type="file"]') ||
                           doc.querySelector('[data-testid="stFileUploader"] input') ||
                           doc.querySelector('.stFileUploader input');
                
                if (input) {
                    input.click();
                    setTimeout(function() {
                        btn.style.opacity = '1';
                        btn.style.pointerEvents = 'auto';
                    }, 500);
                } else {
                    // Retry after a short delay
                    setTimeout(function() {
                        findAndClickFileInput(attempts - 1);
                    }, 100);
                }
            }
            
            findAndClickFileInput(10); // Try up to 10 times (1 second total)
        };
        
        // Keyboard shortcuts
        doc.addEventListener('keydown', function(e) {
            // Ctrl+Enter to send
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                var textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
                if (textarea && textarea.value.trim()) {
                    var btn = doc.querySelector('[data-testid="stChatInput"] button');
                    if (btn) btn.click();
                }
                e.preventDefault();
            }
            // Ctrl+N for new chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                window.parent.location.href = window.parent.location.pathname + '?action=new_chat';
                e.preventDefault();
            }
            // Ctrl+M for mic
            if ((e.ctrlKey || e.metaKey) && e.key === 'm') {
                doc.getElementById('nexus-mic').click();
                e.preventDefault();
            }
            // Ctrl+U for upload
            if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
                doc.getElementById('nexus-upload').click();
                e.preventDefault();
            }
        });
        
        // ========================================
        // ROBUST UNLIMITED VOICE RECOGNITION
        // ========================================
        // State management - use closure for isolation
        (function() {
            var voiceState = {
                isListening: false,
                sessionCount: 0,
                currentRecognition: null
            };
            
            // Cleanup function to properly dispose of recognition
            function cleanupRecognition() {
                if (voiceState.currentRecognition) {
                    try {
                        voiceState.currentRecognition.onstart = null;
                        voiceState.currentRecognition.onend = null;
                        voiceState.currentRecognition.onresult = null;
                        voiceState.currentRecognition.onerror = null;
                        voiceState.currentRecognition.onspeechend = null;
                        voiceState.currentRecognition.abort();
                    } catch(e) { /* ignore cleanup errors */ }
                    voiceState.currentRecognition = null;
                }
                voiceState.isListening = false;
            }
            
            // Create brand new recognition instance
            function createRecognition() {
                var SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
                if (!SR) return null;
                
                var rec = new SR();
                rec.continuous = true;  // Allow longer speech
                rec.interimResults = true;  // Show live transcription
                rec.maxAlternatives = 3;  // Get top 3 alternatives for better accuracy
                rec.lang = 'en-US';  // Primary language
                
                return rec;
            }
            
            // Update UI state
            function updateUI(btn, stat, state, message) {
                switch(state) {
                    case 'listening':
                        btn.classList.add('recording');
                        stat.innerHTML = '<span style="color: #f87171; animation: pulse 1s infinite;">●</span> Listening... (click again to stop)';
                        stat.style.display = 'block';
                        break;
                    case 'processing':
                        stat.innerHTML = '<span style="color: #60a5fa;">⟳</span> Processing...';
                        break;
                    case 'success':
                        btn.classList.remove('recording');
                        stat.innerHTML = '<span style="color: #34d399;">✓</span> ' + (message || 'Done');
                        setTimeout(function() { stat.style.display = 'none'; }, 2000);
                        break;
                    case 'error':
                        btn.classList.remove('recording');
                        stat.innerHTML = '<span style="color: #f87171;">✕</span> ' + (message || 'Error');
                        setTimeout(function() { stat.style.display = 'none'; }, 3000);
                        break;
                    case 'idle':
                        btn.classList.remove('recording');
                        stat.style.display = 'none';
                        break;
                }
            }
            
            // Set text to input field
            function setInputText(text) {
                var textarea = doc.querySelector('[data-testid="stChatInput"] textarea');
                if (textarea && text) {
                    try {
                        var setter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLTextAreaElement.prototype, 'value'
                        ).set;
                        setter.call(textarea, text);
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.focus();
                    } catch(e) {
                        textarea.value = text;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            }
            
            // Main click handler
            doc.getElementById('nexus-mic').onclick = function() {
                var btn = this;
                var stat = doc.getElementById('nexus-status');
                
                // Check browser support
                var SR = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
                if (!SR) {
                    updateUI(btn, stat, 'error', 'Voice not supported. Use Chrome, Edge, or Safari.');
                    return;
                }
                
                // Toggle off if already listening
                if (voiceState.isListening) {
                    cleanupRecognition();
                    updateUI(btn, stat, 'idle');
                    return;
                }
                
                // Cleanup any previous instance completely
                cleanupRecognition();
                
                // Increment session counter (helps with debugging)
                voiceState.sessionCount++;
                var thisSession = voiceState.sessionCount;
                
                // Create fresh recognition
                var rec = createRecognition();
                if (!rec) {
                    updateUI(btn, stat, 'error', 'Could not initialize voice recognition');
                    return;
                }
                
                voiceState.currentRecognition = rec;
                var finalTranscript = '';
                var interimTranscript = '';
                
                rec.onstart = function() {
                    if (thisSession !== voiceState.sessionCount) return;
                    voiceState.isListening = true;
                    updateUI(btn, stat, 'listening');
                };
                
                rec.onresult = function(e) {
                    if (thisSession !== voiceState.sessionCount) return;
                    
                    interimTranscript = '';
                    for (var i = e.resultIndex; i < e.results.length; i++) {
                        var result = e.results[i];
                        // Pick the best alternative (highest confidence)
                        var bestAlt = result[0];
                        for (var j = 1; j < result.length; j++) {
                            if (result[j].confidence > bestAlt.confidence) {
                                bestAlt = result[j];
                            }
                        }
                        
                        if (result.isFinal) {
                            finalTranscript += bestAlt.transcript;
                        } else {
                            interimTranscript += bestAlt.transcript;
                        }
                    }
                    
                    // Show combined transcript
                    var displayText = finalTranscript + interimTranscript;
                    if (displayText) {
                        stat.innerHTML = '<span style="color: #34d399;">✓</span> ' + displayText.substring(0, 100) + (displayText.length > 100 ? '...' : '');
                        setInputText(displayText);
                    }
                };
                
                rec.onspeechend = function() {
                    if (thisSession !== voiceState.sessionCount) return;
                    // User stopped speaking, stop recognition after a brief pause
                    setTimeout(function() {
                        if (voiceState.currentRecognition === rec && voiceState.isListening) {
                            rec.stop();
                        }
                    }, 500);
                };
                
                rec.onend = function() {
                    if (thisSession !== voiceState.sessionCount) return;
                    
                    var hadContent = finalTranscript || interimTranscript;
                    cleanupRecognition();
                    
                    if (hadContent) {
                        updateUI(btn, stat, 'success', (finalTranscript + interimTranscript).substring(0, 50) + '...');
                    } else {
                        updateUI(btn, stat, 'idle');
                    }
                };
                
                rec.onerror = function(e) {
                    if (thisSession !== voiceState.sessionCount) return;
                    
                    cleanupRecognition();
                    
                    var msg = 'Error: ' + e.error;
                    switch(e.error) {
                        case 'not-allowed':
                            msg = 'Microphone access denied. Please allow microphone access.';
                            break;
                        case 'no-speech':
                            msg = 'No speech detected. Please try again.';
                            break;
                        case 'aborted':
                            msg = 'Voice input cancelled';
                            break;
                        case 'network':
                            msg = 'Network error. Check your connection.';
                            break;
                        case 'audio-capture':
                            msg = 'No microphone found. Please connect a microphone.';
                            break;
                    }
                    
                    // For 'no-speech', just go idle instead of showing error
                    if (e.error === 'no-speech' || e.error === 'aborted') {
                        updateUI(btn, stat, 'idle');
                    } else {
                        updateUI(btn, stat, 'error', msg);
                    }
                };
                
                // Start recognition
                try {
                    rec.start();
                } catch(e) {
                    cleanupRecognition();
                    updateUI(btn, stat, 'error', 'Failed to start: ' + e.message);
                }
            };
        })();
    })();
    </script>
    """


def render_floating_toolbar():
    """Inject the premium floating toolbar into the page."""
    components.html(get_floating_toolbar_js(), height=0)


def get_tts_script(text: str) -> str:
    """Generate text-to-speech JavaScript."""
    import re
    
    # Clean markdown
    clean = re.sub(r'\*\*|__|\\*|_|`|#|>|-|\|', '', text)
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
    clean = re.sub(r'```[\s\S]*?```', 'code block', clean)
    clean = clean[:1500]
    clean = clean.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    
    return f"""
    <script>
    (function() {{
        var text = '{clean}';
        if (window.parent.speechSynthesis) {{
            window.parent.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance(text);
            u.rate = 1.0;
            u.pitch = 1.0;
            var voices = window.parent.speechSynthesis.getVoices();
            var v = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft') || v.lang.startsWith('en'));
            if (v) u.voice = v;
            window.parent.speechSynthesis.speak(u);
        }}
    }})();
    </script>
    """


def render_tts(text: str):
    """Render text-to-speech for response."""
    components.html(get_tts_script(text), height=0)


def render_typing_indicator():
    """Render animated typing indicator (AI is thinking...)."""
    st.markdown("""
    <style>
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin: 8px 0;
        width: fit-content;
    }
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-primary, #6366f1);
        animation: typingBounce 1.4s infinite ease-in-out both;
    }
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typingBounce {
        0%, 80%, 100% { 
            transform: scale(0.6);
            opacity: 0.5;
        }
        40% { 
            transform: scale(1);
            opacity: 1;
        }
    }
    .typing-text {
        color: var(--text-secondary, #8b8d93);
        font-size: 13px;
        font-weight: 500;
    }
    </style>
    <div class="typing-indicator">
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        <span class="typing-text">AI is thinking...</span>
    </div>
    """, unsafe_allow_html=True)


def render_message_reactions(message_id: str):
    """Render emoji reaction buttons for a message."""
    reactions = ["👍", "❤️", "😂", "🎉", "🤔"]
    
    # Get current reactions from session state
    reactions_key = f"reactions_{message_id}"
    if reactions_key not in st.session_state:
        st.session_state[reactions_key] = {}
    
    # Create reaction buttons
    cols = st.columns(len(reactions) + 1)
    
    for i, emoji in enumerate(reactions):
        count = st.session_state[reactions_key].get(emoji, 0)
        label = f"{emoji} {count}" if count > 0 else emoji
        
        with cols[i]:
            if st.button(label, key=f"react_{message_id}_{i}", help=f"React with {emoji}"):
                st.session_state[reactions_key][emoji] = count + 1
                st.rerun()


def get_reactions_css():
    """Get CSS for message reactions overlay."""
    return """
    <style>
    .reaction-bar {
        display: flex;
        gap: 4px;
        margin-top: 8px;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .message-container:hover .reaction-bar {
        opacity: 1;
    }
    
    .reaction-btn {
        padding: 4px 8px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .reaction-btn:hover {
        background: rgba(99, 102, 241, 0.2);
        transform: scale(1.1);
    }
    
    .reaction-btn.active {
        background: rgba(99, 102, 241, 0.3);
        border-color: rgba(99, 102, 241, 0.5);
    }
    </style>
    """

