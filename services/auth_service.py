"""
Authentication Service using Supabase Auth.
Handles user registration, login, logout, and session management.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class User:
    """User data class."""
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None



# Cached Supabase client - persists across page refreshes
@st.cache_resource
def get_cached_supabase_client(supabase_url: str, supabase_key: str):
    """Create a cached Supabase client that persists across refreshes."""
    try:
        from supabase import create_client
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise


class AuthService:
    """
    Supabase Authentication Service.
    Handles all auth operations with session persistence in Streamlit.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    @property
    def client(self):
        """Get cached Supabase client that persists across refreshes."""
        return get_cached_supabase_client(self.supabase_url, self.supabase_key)
    
    def is_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.supabase_url and self.supabase_key)
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password (min 6 chars)
            
        Returns:
            Dict with user data or error
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Store session in Streamlit
                st.session_state.user = User(
                    id=response.user.id,
                    email=response.user.email,
                    display_name=response.user.user_metadata.get("display_name"),
                    created_at=str(response.user.created_at)
                )
                st.session_state.access_token = response.session.access_token if response.session else None
                
                return {"success": True, "user": response.user, "message": "Account created! Please check your email to confirm."}
            
            return {"success": False, "error": "Registration failed"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Sign up error: {error_msg}")
            return {"success": False, "error": error_msg}
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Log in an existing user.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict with user data or error
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Store session in Streamlit
                st.session_state.user = User(
                    id=response.user.id,
                    email=response.user.email,
                    display_name=response.user.user_metadata.get("display_name"),
                    created_at=str(response.user.created_at)
                )
                st.session_state.access_token = response.session.access_token if response.session else None
                st.session_state.authenticated = True
                
                return {"success": True, "user": response.user}
            
            return {"success": False, "error": "Login failed"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Sign in error: {error_msg}")
            
            # Parse common errors
            if "Invalid login credentials" in error_msg:
                return {"success": False, "error": "Invalid email or password"}
            elif "Email not confirmed" in error_msg:
                return {"success": False, "error": "Please confirm your email first"}
            
            return {"success": False, "error": error_msg}
    
    def sign_out(self) -> Dict[str, Any]:
        """Log out the current user."""
        try:
            self.client.auth.sign_out()
            
            # Clear session state
            st.session_state.user = None
            st.session_state.access_token = None
            st.session_state.authenticated = False
            st.session_state.messages = []
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user(self) -> Optional[User]:
        """Get the current logged-in user from session state."""
        return st.session_state.get("user")
    
    def restore_session(self) -> bool:
        """
        Try to restore existing session from Supabase on page refresh.
        Returns True if session was restored, False otherwise.
        """
        # Already authenticated in session state
        if st.session_state.get("authenticated") and st.session_state.get("user"):
            return True
        
        # Don't restore in guest mode
        if st.session_state.get("guest_mode"):
            return False
        
        try:
            # Check if Supabase has an active session
            session = self.client.auth.get_session()
            
            if session and session.user:
                # Restore to session state
                st.session_state.user = User(
                    id=session.user.id,
                    email=session.user.email,
                    display_name=session.user.user_metadata.get("display_name") if session.user.user_metadata else None,
                    created_at=str(session.user.created_at)
                )
                st.session_state.access_token = session.access_token
                st.session_state.authenticated = True
                logger.info(f"Session restored for user: {session.user.email}")
                return True
        except Exception as e:
            logger.debug(f"No session to restore: {e}")
        
        return False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        # First try to restore any existing session
        if not st.session_state.get("authenticated"):
            self.restore_session()
        
        return st.session_state.get("authenticated", False) and st.session_state.get("user") is not None
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with success status
        """
        try:
            self.client.auth.reset_password_email(email)
            return {"success": True, "message": "Password reset email sent!"}
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_google_oauth_url(self, redirect_to: str = None) -> str:
        """
        Get the Google OAuth sign-in URL.
        
        Args:
            redirect_to: Optional URL to redirect after login
            
        Returns:
            The OAuth URL to redirect the user to
        """
        try:
            response = self.client.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_to or "http://localhost:8517"
                }
            })
            return response.url
        except Exception as e:
            logger.error(f"Google OAuth error: {e}")
            return None


# Factory function
def create_auth_service() -> AuthService:
    """Create an auth service with settings from environment."""
    from config.settings import settings
    
    return AuthService(
        supabase_url=settings.ai.supabase_url,
        supabase_key=settings.ai.supabase_key
    )
