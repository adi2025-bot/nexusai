"""
Authentication UI Components.
Premium login/signup interface for NexusAI.
"""

import streamlit as st
from services.auth_service import create_auth_service, AuthService


def render_login_page():
    """
    Render the premium login/signup page.
    Returns True if user is authenticated, False otherwise.
    """
    auth_service = create_auth_service()
    
    if not auth_service.is_configured():
        st.warning("⚠️ Authentication not configured. Running in guest mode.")
        return True  # Allow access without auth
    
    # Check if already authenticated
    if auth_service.is_authenticated():
        return True
    
    # Premium login page styling
    st.markdown("""
    <style>
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .auth-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .auth-subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 30px;
    }
    .stTextInput > div > div > input {
        background: #0e0e1a !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 12px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="auth-title">✨ NexusAI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Your AI-Powered Assistant</p>', unsafe_allow_html=True)
        
        # Tab selection
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    remember = st.checkbox("Remember me", value=True)
                with col_b:
                    forgot = st.form_submit_button("Forgot password?", type="secondary")
                
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                
                if login_btn and email and password:
                    with st.spinner("Signing in..."):
                        result = auth_service.sign_in(email, password)
                        if result["success"]:
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Login failed')}")
                
                if forgot:
                    if email:
                        result = auth_service.reset_password(email)
                        if result["success"]:
                            st.info(result["message"])
                        else:
                            st.error(result.get("error", "Failed to send reset email"))
                    else:
                        st.warning("Enter your email first")
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                new_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="confirm_pass")
                
                agree = st.checkbox("I agree to the Terms of Service")
                
                signup_btn = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
                
                if signup_btn:
                    if not new_email or not new_password:
                        st.error("Please fill in all fields")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif not agree:
                        st.error("Please agree to the Terms of Service")
                    else:
                        with st.spinner("Creating your account..."):
                            result = auth_service.sign_up(new_email, new_password)
                            if result["success"]:
                                st.success("✅ Account created! Check your email to confirm.")
                            else:
                                st.error(f"❌ {result.get('error', 'Registration failed')}")
        
        # Social login options
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #888; margin-bottom: 16px;">Or continue with</p>', unsafe_allow_html=True)
        
        # Google Sign In button
        if st.button("🔵 Continue with Google", use_container_width=True, type="primary"):
            google_url = auth_service.get_google_oauth_url()
            if google_url:
                st.markdown(f'<meta http-equiv="refresh" content="0;url={google_url}">', unsafe_allow_html=True)
                st.info("Redirecting to Google...")
            else:
                st.error("Google sign-in is not configured. Please contact admin.")
        
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        # Guest mode option (secondary)
        if st.button("👤 Continue as Guest", use_container_width=True):
            st.session_state.guest_mode = True
            st.session_state.authenticated = True
            st.rerun()
    
    return False


def render_user_menu():
    """Render user menu in sidebar when authenticated."""
    auth_service = create_auth_service()
    user = auth_service.get_user()
    
    if user:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"👤 **{user.email}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ Profile", use_container_width=True):
                    st.session_state.show_profile = True
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    auth_service.sign_out()
                    st.rerun()
    elif st.session_state.get("guest_mode"):
        with st.sidebar:
            st.markdown("---")
            st.markdown("👤 **Guest Mode**")
            if st.button("🔐 Login to Save Chats", use_container_width=True):
                st.session_state.guest_mode = False
                st.session_state.authenticated = False
                st.rerun()


def is_authenticated() -> bool:
    """Check if user is authenticated (including guest mode)."""
    return st.session_state.get("authenticated", False) or st.session_state.get("guest_mode", False)


def require_auth(allow_guest: bool = True):
    """
    Decorator/function to require authentication.
    
    Args:
        allow_guest: If True, allows guest mode access
    """
    auth_service = create_auth_service()
    
    # Not configured - allow access
    if not auth_service.is_configured():
        return True
    
    # Authenticated user
    if auth_service.is_authenticated():
        return True
    
    # Guest mode allowed
    if allow_guest and st.session_state.get("guest_mode"):
        return True
    
    # Show login page
    return render_login_page()
