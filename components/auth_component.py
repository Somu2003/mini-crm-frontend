import streamlit as st

class AuthComponent:
    def __init__(self):
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
    
    def is_authenticated(self):
        return st.session_state.get("authenticated", False)
    
    def login(self):
        try:
            demo_user = {
                "email": "demo@example.com",
                "name": "Demo User",
                "google_id": "demo_google_123",
                "picture": "https://via.placeholder.com/150/667eea/white?text=DU"
            }
            
            st.session_state.authenticated = True
            st.session_state.user_info = demo_user
            st.success(f"🎉 Successfully logged in as {demo_user['name']}!")
            return True
            
        except Exception as e:
            st.error(f"❌ Login failed: {str(e)}")
            return False
    
    def logout(self):
        try:
            user_name = st.session_state.get("user_info", {}).get("name", "User")
            st.session_state.authenticated = False
            st.session_state.user_info = None
            
            # Clear related session data
            for key in ["segment_rules", "ai_messages", "selected_message"]:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success(f"👋 Successfully logged out {user_name}!")
            return True
            
        except Exception as e:
            st.error(f"❌ Logout failed: {str(e)}")
            return False
    
    def get_user_info(self):
        return st.session_state.get("user_info", {})
    
    def get_user_email(self):
        user_info = self.get_user_info()
        return user_info.get("email", "demo@example.com")
    
    def get_user_name(self):
        user_info = self.get_user_info()
        return user_info.get("name", "Demo User")
    
    # THIS METHOD WAS MISSING
    def require_auth(self, redirect_message="Please log in to access this page."):
        if not self.is_authenticated():
            st.warning(redirect_message)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔐 Login Now", type="primary", use_container_width=True):
                    self.login()
                    st.rerun()
            st.stop()
        return True
