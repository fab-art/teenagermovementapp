import streamlit as st
from utils import authenticate, get_db_connection, log_audit
from styles import apply_styles

def main():
    st.set_page_config(page_title="ERP System", layout="wide")
    apply_styles()
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Login Page
        st.title("Welcome to ERP System")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                log_audit(username, "LOGIN", "User logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        # Dashboard
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout"):
            log_audit(st.session_state.username, "LOGOUT", "User logged out")
            st.session_state.authenticated = False
            st.rerun()
        
        st.title("Dashboard")
        
        # Quick Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Today's Sales", "$0.00")
        with col2:
            st.metric("Orders Pending", "0")
        with col3:
            st.metric("Low Stock Items", "0")
        with col4:
            st.metric("Active Users", "1")
        
        # User Management Section
        st.subheader("User Management")
        conn = get_db_connection()
        if conn:
            users = conn.execute("SELECT * FROM users").fetchall() if conn else []
            if users:
                st.dataframe(users, use_container_width=True)
            else:
                st.info("No users found")
        
        st.markdown("---")
        st.caption("Navigate using the sidebar menu")

if __name__ == "__main__":
    main()
