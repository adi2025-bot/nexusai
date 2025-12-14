"""
Premium UI Styles Module
Enhanced CSS with glassmorphism, animations, and mobile responsiveness.
"""

import streamlit as st
from typing import Literal

ThemeType = Literal["dark", "light"]


class Theme:
    """Theme color definitions with gradient support."""
    
    DARK = {
        "bg_primary": "#0a0a0b",
        "bg_secondary": "#131416",
        "bg_tertiary": "#1a1b1e",
        "bg_card": "rgba(26, 27, 30, 0.8)",
        "glass_bg": "rgba(255, 255, 255, 0.03)",
        "glass_border": "rgba(255, 255, 255, 0.08)",
        "border": "#2a2b2e",
        "text_primary": "#f0f0f0",
        "text_secondary": "#8b8d93",
        "text_muted": "#5c5e66",
        "accent_primary": "#6366f1",  # Indigo
        "accent_secondary": "#8b5cf6",  # Purple
        "accent_tertiary": "#06b6d4",  # Cyan
        "accent_success": "#10b981",
        "accent_warning": "#f59e0b",
        "accent_error": "#ef4444",
        "gradient_primary": "linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7)",
        "gradient_user": "linear-gradient(135deg, #3b82f6, #1d4ed8)",
        "gradient_assistant": "linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.08))",
        "glow_primary": "0 0 40px rgba(99, 102, 241, 0.3)",
        "glow_accent": "0 0 60px rgba(139, 92, 246, 0.2)",
    }
    
    LIGHT = {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8fafc",
        "bg_tertiary": "#f1f5f9",
        "bg_card": "rgba(255, 255, 255, 0.9)",
        "glass_bg": "rgba(255, 255, 255, 0.7)",
        "glass_border": "rgba(0, 0, 0, 0.08)",
        "border": "#e2e8f0",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "text_muted": "#94a3b8",
        "accent_primary": "#6366f1",
        "accent_secondary": "#8b5cf6",
        "accent_tertiary": "#0891b2",
        "accent_success": "#059669",
        "accent_warning": "#d97706",
        "accent_error": "#dc2626",
        "gradient_primary": "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "gradient_user": "linear-gradient(135deg, #dbeafe, #bfdbfe)",
        "gradient_assistant": "linear-gradient(135deg, #f8fafc, #ffffff)",
        "glow_primary": "0 0 40px rgba(99, 102, 241, 0.15)",
        "glow_accent": "0 0 60px rgba(139, 92, 246, 0.1)",
    }
    
    # ==================== CUSTOM COLOR THEMES ====================
    
    OCEAN_BLUE = {
        **DARK,
        "accent_primary": "#0ea5e9",  # Sky blue
        "accent_secondary": "#0284c7",  # Darker blue
        "accent_tertiary": "#38bdf8",  # Light blue
        "gradient_primary": "linear-gradient(135deg, #0ea5e9, #0284c7, #0369a1)",
        "gradient_user": "linear-gradient(135deg, #0ea5e9, #0284c7)",
        "gradient_assistant": "linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(2, 132, 199, 0.08))",
        "glow_primary": "0 0 40px rgba(14, 165, 233, 0.3)",
        "glow_accent": "0 0 60px rgba(56, 189, 248, 0.2)",
    }
    
    FOREST_GREEN = {
        **DARK,
        "accent_primary": "#22c55e",  # Green
        "accent_secondary": "#16a34a",  # Darker green
        "accent_tertiary": "#4ade80",  # Light green
        "gradient_primary": "linear-gradient(135deg, #22c55e, #16a34a, #15803d)",
        "gradient_user": "linear-gradient(135deg, #22c55e, #16a34a)",
        "gradient_assistant": "linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.08))",
        "glow_primary": "0 0 40px rgba(34, 197, 94, 0.3)",
        "glow_accent": "0 0 60px rgba(74, 222, 128, 0.2)",
    }
    
    SUNSET_ORANGE = {
        **DARK,
        "accent_primary": "#f97316",  # Orange
        "accent_secondary": "#ea580c",  # Darker orange
        "accent_tertiary": "#fb923c",  # Light orange
        "gradient_primary": "linear-gradient(135deg, #f97316, #ea580c, #c2410c)",
        "gradient_user": "linear-gradient(135deg, #f97316, #ea580c)",
        "gradient_assistant": "linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(234, 88, 12, 0.08))",
        "glow_primary": "0 0 40px rgba(249, 115, 22, 0.3)",
        "glow_accent": "0 0 60px rgba(251, 146, 60, 0.2)",
    }
    
    ROSE_PINK = {
        **DARK,
        "accent_primary": "#ec4899",  # Pink
        "accent_secondary": "#db2777",  # Darker pink
        "accent_tertiary": "#f472b6",  # Light pink
        "gradient_primary": "linear-gradient(135deg, #ec4899, #db2777, #be185d)",
        "gradient_user": "linear-gradient(135deg, #ec4899, #db2777)",
        "gradient_assistant": "linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(219, 39, 119, 0.08))",
        "glow_primary": "0 0 40px rgba(236, 72, 153, 0.3)",
        "glow_accent": "0 0 60px rgba(244, 114, 182, 0.2)",
    }
    
    # Theme selector mapping
    THEMES = {
        "default": DARK,
        "ocean_blue": OCEAN_BLUE,
        "forest_green": FOREST_GREEN,
        "sunset_orange": SUNSET_ORANGE,
        "rose_pink": ROSE_PINK,
        "light": LIGHT,
    }
    
    THEME_NAMES = {
        "default": "🌙 Default (Indigo)",
        "ocean_blue": "🌊 Ocean Blue",
        "forest_green": "🌲 Forest Green",
        "sunset_orange": "🌅 Sunset Orange",
        "rose_pink": "🌸 Rose Pink",
        "light": "☀️ Light Mode",
    }


def get_premium_base_styles(theme: str = "default") -> str:
    """Get premium base CSS styles with selected theme."""
    # Get theme colors from mapping or default to DARK
    c = Theme.THEMES.get(theme, Theme.DARK)
    
    return f"""
    <style>
    /* ============================================
       NEXUSAI PREMIUM STYLES v4.1
       Enhanced Design System with Animations
       ============================================ */
    
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* CSS Variables */
    :root {{
        --bg-primary: {c["bg_primary"]};
        --bg-secondary: {c["bg_secondary"]};
        --bg-tertiary: {c["bg_tertiary"]};
        --bg-card: {c["bg_card"]};
        --glass-bg: {c["glass_bg"]};
        --glass-border: {c["glass_border"]};
        --border: {c["border"]};
        --text-primary: {c["text_primary"]};
        --text-secondary: {c["text_secondary"]};
        --text-muted: {c["text_muted"]};
        --accent-primary: {c["accent_primary"]};
        --accent-secondary: {c["accent_secondary"]};
        --accent-tertiary: {c["accent_tertiary"]};
        --gradient-primary: {c["gradient_primary"]};
        --glow-primary: {c["glow_primary"]};
    }}
    
    /* Base Reset */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    
    code, pre {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }}
    
    /* Hide Streamlit Defaults */
    #MainMenu, footer, .stDeployButton {{ display: none !important; }}
    
    header, [data-testid="stHeader"] {{
        background: transparent !important;
        pointer-events: none;
    }}
    
    /* Smooth scrolling */
    html {{
        scroll-behavior: smooth;
    }}
    
    /* Main App Background with subtle gradient */
    .stApp {{
        background: var(--bg-primary) !important;
        background-image: 
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.15), transparent),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139, 92, 246, 0.1), transparent) !important;
    }}
    
    
    @keyframes particleFloat {{
        0% {{ background-position: 0% 0%; }}
        100% {{ background-position: 100% 100%; }}
    }}
    
    /* Typing Indicator Animation */
    .typing-indicator {{
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 12px 16px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%);
        border-radius: 16px;
        width: fit-content;
    }}
    
    .typing-dot {{
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 50%;
        animation: typingBounce 1.4s ease-in-out infinite;
    }}
    
    .typing-dot:nth-child(1) {{ animation-delay: 0s; }}
    .typing-dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .typing-dot:nth-child(3) {{ animation-delay: 0.4s; }}
    
    @keyframes typingBounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.5; }}
        30% {{ transform: translateY(-8px); opacity: 1; }}
    }}
    
    /* Skeleton Loader */
    .skeleton {{
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.03) 25%,
            rgba(255, 255, 255, 0.08) 50%,
            rgba(255, 255, 255, 0.03) 75%
        );
        background-size: 200% 100%;
        animation: skeletonPulse 1.5s ease-in-out infinite;
        border-radius: 8px;
    }}
    
    @keyframes skeletonPulse {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    /* =================================================================
       PREMIUM MICRO-INTERACTIONS
       ================================================================= */
    
    /* Message Fade-In Slide Animation - Simplified to prevent disappearing */
    .stChatMessage {{
        animation: messageFadeIn 0.3s ease-out;
        /* Note: Removed initial opacity:0 which was causing messages to disappear */
    }}
    
    @keyframes messageFadeIn {{
        0% {{
            opacity: 0.7;
            transform: translateY(5px);
        }}
        100% {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Button Hover Glow Effect */
    .stButton > button {{
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3), 0 0 40px rgba(99, 102, 241, 0.1);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.2);
    }}
    
    /* Button Ripple Effect */
    .stButton > button::after {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.4s, height 0.4s;
    }}
    
    .stButton > button:active::after {{
        width: 200px;
        height: 200px;
    }}
    
    /* Typing Cursor Blink Animation */
    .typing-cursor {{
        display: inline-block;
        width: 2px;
        height: 1em;
        background: #6366f1;
        margin-left: 2px;
        animation: cursorBlink 1s step-end infinite;
    }}
    
    @keyframes cursorBlink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
    }}
    
    /* Collapsible Long Answer Styling */
    details.nexus-collapsible {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.02));
        border: 1px solid rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    details.nexus-collapsible[open] {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.04));
    }}
    
    details.nexus-collapsible summary {{
        padding: 12px 16px;
        cursor: pointer;
        font-weight: 500;
        color: #a5b4fc;
        display: flex;
        align-items: center;
        gap: 8px;
        user-select: none;
        transition: all 0.2s ease;
    }}
    
    details.nexus-collapsible summary:hover {{
        background: rgba(99, 102, 241, 0.1);
    }}
    
    details.nexus-collapsible summary::marker {{
        display: none;
    }}
    
    details.nexus-collapsible summary::before {{
        content: '▶';
        font-size: 10px;
        transition: transform 0.2s ease;
    }}
    
    details.nexus-collapsible[open] summary::before {{
        transform: rotate(90deg);
    }}
    
    /* Card Hover Lift Effect */
    .hover-lift {{
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .hover-lift:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }}
    
    /* Focus Glow Ring */
    input:focus, textarea:focus, select:focus {{
        outline: none;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
    }}
    
    /* Smooth Progress Bar */
    .progress-smooth {{
        height: 4px;
        background: rgba(99, 102, 241, 0.2);
        border-radius: 2px;
        overflow: hidden;
    }}
    
    .progress-smooth .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border-radius: 2px;
        animation: progressPulse 2s ease-in-out infinite;
    }}
    
    @keyframes progressPulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    /* Scale In Animation for Modals/Cards */
    .scale-in {{
        animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}
    
    @keyframes scaleIn {{
        0% {{
            opacity: 0;
            transform: scale(0.95);
        }}
        100% {{
            opacity: 1;
            transform: scale(1);
        }}
    }}
    
    /* Toast Slide Animation */
    .toast-slide {{
        animation: toastSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}
    
    @keyframes toastSlide {{
        0% {{
            opacity: 0;
            transform: translateX(100%);
        }}
        100% {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    /* Toast Notifications */
    .toast-notification {{
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: rgba(26, 27, 30, 0.95);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 20px;
        color: var(--text-primary);
        font-size: 0.9rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        z-index: 10000;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .toast-notification.show {{
        transform: translateX(-50%) translateY(0);
        opacity: 1;
    }}
    
    .toast-success {{ border-left: 3px solid #10b981; }}
    .toast-error {{ border-left: 3px solid #ef4444; }}
    .toast-info {{ border-left: 3px solid #6366f1; }}
    
    /* Copy Button Styles */
    .copy-btn {{
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 8px;
        padding: 6px 10px;
        color: var(--text-secondary);
        cursor: pointer;
        opacity: 0;
        transform: scale(0.9);
        transition: all 0.2s ease;
        font-size: 0.75rem;
    }}
    
    .message-wrapper:hover .copy-btn {{
        opacity: 1;
        transform: scale(1);
    }}
    
    .copy-btn:hover {{
        background: rgba(99, 102, 241, 0.2);
        color: var(--text-primary);
    }}
    
    .copy-btn.copied {{
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }}
    
    /* Message Timestamp */
    .message-timestamp {{
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 8px;
        opacity: 0;
        transform: translateY(-4px);
        transition: all 0.2s ease;
    }}
    
    .message-wrapper:hover .message-timestamp {{
        opacity: 1;
        transform: translateY(0);
    }}
    
    /* Sidebar Toggle - Always Visible */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        pointer-events: auto !important;
        z-index: 1000001 !important;
        position: fixed !important;
        top: 16px !important;
        left: 16px !important;
        background: var(--glass-bg) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease !important;
        padding: 8px !important;
    }}
    
    [data-testid="stSidebarCollapsedControl"]:hover {{
        color: var(--accent-primary) !important;
        background: var(--bg-tertiary) !important;
        border-color: var(--accent-primary) !important;
        box-shadow: var(--glow-primary);
    }}
    
    /* Main Container */
    .main .block-container {{
        padding: 2rem 2rem 8rem 2rem !important;
        max-width: 900px !important;
        margin: 0 auto !important;
        position: relative;
        z-index: 1;
    }}
    
    /* ============================================
       GLASSMORPHISM SIDEBAR
       ============================================ */
    
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        background: transparent !important;
        padding: 1.5rem 1rem !important;
    }}
    
    /* Sidebar glass card effect */
    [data-testid="stSidebar"] .stButton > button {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid var(--glass-border) !important;
    }}
    
    /* Pulse animation for important elements */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    /* Glow animation */
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(99, 102, 241, 0.2); }}
        50% {{ box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }}
    }}
    
    /* Shimmer effect for buttons */
    .shimmer {{
        position: relative;
        overflow: hidden;
    }}
    
    .shimmer::after {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        animation: shimmerMove 2s infinite;
    }}
    
    @keyframes shimmerMove {{
        0% {{ left: -100%; }}
        100% {{ left: 100%; }}
    }}
    </style>
    """


def get_premium_welcome_styles() -> str:
    """Get styles for the animated welcome screen."""
    return """
    <style>
    /* ============================================
       PREMIUM WELCOME SCREEN
       ============================================ */
    
    .welcome-hero {
        min-height: 60vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    /* Animated gradient orb */
    .welcome-orb {
        position: absolute;
        width: 400px;
        height: 400px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
        filter: blur(60px);
        animation: orbFloat 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    .welcome-orb-2 {
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, transparent 70%);
        animation: orbFloat2 10s ease-in-out infinite;
        animation-delay: -5s;
    }
    
    @keyframes orbFloat {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-30%, -60%) scale(1.2); }
    }
    
    @keyframes orbFloat2 {
        0%, 100% { transform: translate(50%, 50%) scale(1); }
        50% { transform: translate(30%, 30%) scale(1.3); }
    }
    
    /* Sparkle icon with gradient */
    .welcome-icon {
        font-size: 4.5rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7, #6366f1);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite, iconPulse 2s ease-in-out infinite;
        filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.5));
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
        50% { transform: scale(1.05); }
    }
    
    /* Title with subtle animation */
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        z-index: 1;
        position: relative;
        animation: fadeSlideUp 0.6s ease-out;
    }
    
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Subtitle */
    .welcome-subtitle {
        font-size: 1.15rem;
        color: var(--text-secondary);
        max-width: 480px;
        line-height: 1.7;
        z-index: 1;
        position: relative;
        animation: fadeSlideUp 0.6s ease-out 0.1s backwards;
    }
    
    /* Quick Actions Container */
    .quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        margin-top: 2.5rem;
        z-index: 1;
        position: relative;
        animation: fadeSlideUp 0.6s ease-out 0.2s backwards;
    }
    
    /* Quick Action Buttons - Glass Style */
    .stButton > button {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: var(--text-primary) !important;
        padding: 12px 24px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    </style>
    """


def get_premium_chat_styles() -> str:
    """Get styles for glassmorphism chat bubbles."""
    return """
    <style>
    /* ============================================
       PREMIUM CHAT MESSAGES - GLASSMORPHISM
       ============================================ */
    
    /* Message Animation */
    @keyframes messageSlideIn {
        from { 
            opacity: 0; 
            transform: translateY(16px) scale(0.98);
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes messageFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Chat Container */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 10px 0 !important;
        animation: messageSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* User Message - Solid Gradient */
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%) !important;
        border: none !important;
        border-radius: 24px 24px 6px 24px !important;
        padding: 16px 20px !important;
        box-shadow: 
            0 4px 20px rgba(59, 130, 246, 0.3),
            0 2px 8px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        max-width: 85% !important;
        margin-left: auto !important;
        color: white !important;
    }
    
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] p {
        color: white !important;
    }
    
    /* Assistant Message - Glassmorphism */
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.08) 0%,
            rgba(139, 92, 246, 0.05) 50%,
            rgba(99, 102, 241, 0.03) 100%
        ) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 24px 24px 24px 6px !important;
        padding: 18px 22px !important;
        box-shadow: 
            0 4px 24px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        max-width: 90% !important;
    }
    
    /* Avatar Styling - Premium */
    [data-testid="stChatMessage"] [data-testid^="chatAvatarIcon"] {
        width: 42px !important;
        height: 42px !important;
        border-radius: 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: transform 0.2s ease !important;
    }
    
    [data-testid="stChatMessage"]:hover [data-testid^="chatAvatarIcon"] {
        transform: scale(1.05);
    }
    
    /* User Avatar - Blue */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
    }
    
    /* Assistant Avatar - Purple/Indigo */
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }
    
    /* Message Text */
    [data-testid="stChatMessageContent"] {
        color: var(--text-primary) !important;
        line-height: 1.75 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stChatMessageContent"] p { 
        color: var(--text-primary) !important;
        margin-bottom: 0.5em !important;
    }
    
    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 { 
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        margin-top: 1em !important;
    }
    
    /* Code Blocks - Premium */
    [data-testid="stChatMessageContent"] code {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-size: 0.88em !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stChatMessageContent"] pre {
        background: #0d0d0f !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 18px !important;
        overflow-x: auto !important;
    }
    
    [data-testid="stChatMessageContent"] pre code {
        background: transparent !important;
        padding: 0 !important;
        color: #e2e8f0 !important;
    }
    
    /* Tables */
    [data-testid="stChatMessageContent"] table { 
        width: 100%; 
        margin: 16px 0; 
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stChatMessageContent"] th {
        background: rgba(99, 102, 241, 0.1);
        color: var(--text-primary);
        padding: 12px 16px;
        font-weight: 600;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stChatMessageContent"] td {
        padding: 12px 16px;
        color: var(--text-secondary);
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    [data-testid="stChatMessageContent"] tr:last-child td {
        border-bottom: none;
    }
    </style>
    """


def get_premium_input_styles() -> str:
    """Get styles for the premium floating input bar."""
    return """
    <style>
    /* ============================================
       PREMIUM FLOATING INPUT BAR
       ============================================ */
    
    .stChatInput {
        position: fixed !important;
        bottom: 24px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        max-width: 820px !important;
        width: calc(100% - 48px) !important;
        padding: 0 !important;
        background: transparent !important;
        z-index: 1000 !important;
    }
    
    /* Premium Capsule Container */
    .stChatInput > div {
        background: linear-gradient(
            145deg,
            rgba(26, 27, 30, 0.95) 0%,
            rgba(19, 20, 22, 0.98) 100%
        ) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 28px !important;
        box-shadow: 
            0 8px 40px rgba(0, 0, 0, 0.4),
            0 2px 8px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05),
            0 0 0 1px rgba(99, 102, 241, 0) !important;
        padding: 6px 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stChatInput > div:hover {
        border-color: rgba(255, 255, 255, 0.12) !important;
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.5),
            0 4px 12px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.5),
            0 0 0 3px rgba(99, 102, 241, 0.15),
            0 0 40px rgba(99, 102, 241, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Textarea */
    .stChatInput textarea {
        background: transparent !important;
        color: #f0f0f0 !important;
        border: none !important;
        padding: 14px 20px !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
        min-height: 52px !important;
        resize: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #6b7280 !important;
        font-weight: 400 !important;
    }
    
    /* Send Button - Gradient */
    .stChatInput button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stChatInput button:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
        transform: scale(1.08) !important;
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stChatInput button:active {
        transform: scale(1.02) !important;
    }
    
    .stChatInput button svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }
    </style>
    """


def get_premium_component_styles() -> str:
    """Get styles for premium UI components."""
    return """
    <style>
    /* ============================================
       PREMIUM COMPONENTS
       ============================================ */
    
    /* Form Elements */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 12px 16px !important;
    }
    
    /* Toggle */
    .stToggle label { 
        color: var(--text-primary) !important; 
    }
    
    /* Divider */
    hr { 
        border: none !important;
        height: 1px !important;
        background: linear-gradient(
            90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent
        ) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Status Messages */
    .stSuccess { 
        background: rgba(16, 185, 129, 0.1) !important; 
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        color: #34d399 !important; 
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    
    .stError { 
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        color: #f87171 !important; 
        border-radius: 12px !important;
    }
    
    .stWarning { 
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        color: #fbbf24 !important; 
        border-radius: 12px !important;
    }
    
    .stInfo { 
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        color: #a5b4fc !important; 
        border-radius: 12px !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { 
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track { 
        background: transparent; 
    }
    ::-webkit-scrollbar-thumb { 
        background: rgba(255, 255, 255, 0.1); 
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: rgba(255, 255, 255, 0.2); 
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
    }
    
    /* Popover */
    .stPopover [data-testid="stPopoverBody"] {
        background: rgba(26, 27, 30, 0.95) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4) !important;
    }
    </style>
    """


def get_mobile_responsive_styles() -> str:
    """Get enhanced mobile-responsive CSS with touch-friendly improvements."""
    return """
    <style>
    /* ============================================
       ENHANCED MOBILE RESPONSIVE STYLES
       Touch-friendly, performance-optimized
       ============================================ */
    
    /* Touch-friendly minimum sizes (44px tap targets) */
    @media (pointer: coarse) {
        button, a, [role="button"] {
            min-height: 44px !important;
            min-width: 44px !important;
        }
    }
    
    /* Reduced motion for accessibility and performance */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Tablet and below (768px) */
    @media (max-width: 768px) {
        /* Disable particle animation for performance */
        .stApp::before {
            animation: none !important;
            opacity: 0.3 !important;
        }
        
        /* HIDE SIDEBAR BY DEFAULT ON MOBILE */
        [data-testid="stSidebar"] {
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="true"] {
            transform: translateX(0) !important;
        }
        
        /* Main container - ensure full width and no left margin */
        .main .block-container {
            padding: 0.5rem 0.75rem 7rem 0.75rem !important;
            max-width: 100% !important;
            margin-left: 0 !important;
        }
        
        /* Ensure main area takes full width */
        .main {
            margin-left: 0 !important;
            width: 100% !important;
        }
        
        section[data-testid="stSidebarContent"] {
            width: 85vw !important;
        }
        
        /* Welcome screen - CENTER properly */
        .welcome-hero {
            min-height: 50vh;
            padding: 1rem 0.5rem;
            margin: 0 auto;
            text-align: center;
            width: 100%;
        }
        
        .welcome-icon {
            font-size: 3rem;
            margin: 0 auto;
        }
        
        .welcome-title {
            font-size: 1.5rem;
            text-align: center;
            word-wrap: break-word;
            padding: 0 0.5rem;
        }
        
        .welcome-subtitle {
            font-size: 0.9rem;
            padding: 0 0.5rem;
            text-align: center;
        }
        
        .welcome-orb {
            width: 150px;
            height: 150px;
            filter: blur(40px);
        }
        
        /* Quick actions - stack vertically */
        .quick-actions {
            display: flex !important;
            flex-direction: column !important;
            gap: 0.5rem !important;
            padding: 0 0.5rem !important;
        }
        
        /* Chat messages - full width */
        .stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"],
        .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
            max-width: 95% !important;
            padding: 14px 16px !important;
            border-radius: 18px !important;
        }
        
        [data-testid="stChatMessage"] [data-testid^="chatAvatarIcon"] {
            width: 36px !important;
            height: 36px !important;
            border-radius: 12px !important;
        }
        
        /* Input bar - optimized for mobile keyboard */
        .stChatInput {
            bottom: 12px !important;
            width: calc(100% - 24px) !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
        }
        
        .stChatInput > div {
            border-radius: 24px !important;
            padding: 4px 6px !important;
        }
        
        .stChatInput textarea {
            font-size: 16px !important; /* Prevents iOS zoom */
            padding: 12px 14px !important;
            min-height: 48px !important;
        }
        
        .stChatInput button {
            width: 44px !important;
            height: 44px !important;
            min-width: 44px !important;
        }
        
        /* Quick actions - vertical stack */
        .quick-actions {
            flex-direction: column;
            gap: 8px;
        }
        
        .stButton > button {
            width: 100% !important;
            padding: 14px 20px !important;
            min-height: 48px !important;
        }
        
        /* Sidebar toggle */
        [data-testid="stSidebarCollapsedControl"] {
            top: 8px !important;
            left: 8px !important;
            width: 44px !important;
            height: 44px !important;
        }
        
        /* Floating toolbar - touch optimized */
        .nexus-toolbar {
            bottom: 75px !important;
            padding: 8px !important;
            gap: 8px !important;
            border-radius: 20px !important;
        }
        
        .nexus-btn {
            width: 44px !important;
            height: 44px !important;
        }
        
        /* Status display */
        #nexus-status {
            font-size: 12px !important;
            padding: 8px 12px !important;
            max-width: calc(100% - 32px) !important;
        }
        
        /* Code blocks - horizontal scroll */
        [data-testid="stChatMessageContent"] pre {
            max-width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        
        /* Tables - horizontal scroll */
        [data-testid="stChatMessageContent"] table {
            display: block !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
    }
    
    /* Small phones (480px and below) */
    @media (max-width: 480px) {
        .welcome-title {
            font-size: 1.4rem;
        }
        
        .welcome-subtitle {
            font-size: 0.9rem;
        }
        
        .welcome-icon {
            font-size: 3rem;
        }
        
        [data-testid="stChatMessageContent"] {
            font-size: 0.9rem !important;
        }
        
        /* Even smaller avatars */
        [data-testid="stChatMessage"] [data-testid^="chatAvatarIcon"] {
            width: 32px !important;
            height: 32px !important;
            border-radius: 10px !important;
            font-size: 12px !important;
        }
        
        /* Compact input */
        .stChatInput textarea {
            padding: 10px 12px !important;
        }
        
        /* Hide orbs on very small screens */
        .welcome-orb, .orb {
            display: none !important;
        }
        
        /* ========== SMALL SCREEN SIDEBAR (ChatGPT 5.2) ========== */
        /* Sidebar takes full width on mobile when open */
        [data-testid="stSidebar"] {
            width: 100vw !important;
            max-width: 100vw !important;
            min-width: 100vw !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            width: 100vw !important;
        }
        
        /* Close button more visible */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
            width: 48px !important;
            height: 48px !important;
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 50% !important;
        }
        
        /* File uploader touch-optimized */
        [data-testid="stFileUploader"] {
            min-height: 60px !important;
        }
        
        [data-testid="stFileUploader"] button {
            min-height: 48px !important;
            padding: 12px 20px !important;
        }
        
        /* Toasts positioned better on mobile */
        .stToast {
            bottom: 100px !important;
            max-width: calc(100vw - 40px) !important;
            left: 20px !important;
            right: 20px !important;
        }
        
        /* Select boxes touch-friendly */
        .stSelectbox > div > div {
            min-height: 48px !important;
        }
        
        /* Toggle switches larger */
        .stToggle label {
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* Source citation chips wrap better */
        .rag-sources {
            flex-wrap: wrap !important;
            gap: 6px !important;
        }
        
        .source-chip {
            font-size: 11px !important;
            padding: 4px 8px !important;
        }
    }
    
    /* Landscape orientation on mobile */
    @media (max-height: 500px) and (orientation: landscape) {
        .welcome-hero {
            min-height: 70vh;
            padding: 1rem;
        }
        
        .welcome-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .welcome-title {
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }
        
        .welcome-subtitle {
            font-size: 0.85rem;
        }
        
        /* Compact input bar */
        .stChatInput {
            bottom: 8px !important;
        }
        
        .main .block-container {
            padding-bottom: 5rem !important;
        }
    }
    
    /* Safe area insets for notched phones */
    @supports (padding-bottom: env(safe-area-inset-bottom)) {
        .stChatInput {
            padding-bottom: env(safe-area-inset-bottom) !important;
        }
        
        .nexus-toolbar {
            bottom: calc(75px + env(safe-area-inset-bottom)) !important;
        }
    }
    
    /* Dark mode adjustments for OLED screens */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: #000 !important;
        }
    }
    </style>
    """


@st.cache_resource
def get_all_premium_styles(theme: str = "default") -> str:
    """Get all premium CSS styles combined (cached)."""
    return (
        get_premium_base_styles(theme) +
        get_premium_welcome_styles() +
        get_premium_chat_styles() +
        get_premium_input_styles() +
        get_premium_component_styles() +
        get_mobile_responsive_styles()
    )


def apply_styles(theme: str = "default"):
    """Apply all premium styles to the Streamlit app."""
    st.markdown(get_all_premium_styles(theme), unsafe_allow_html=True)

