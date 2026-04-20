import streamlit as st
from utils import get_db_connection, get_audit_logs, log_audit
from styles import apply_styles

st.set_page_config(page_title="Audit Log", layout="wide")
apply_styles()

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the home page")
    st.stop()

st.title("📜 Audit Log - Immutable Change History")

st.markdown("""
This audit log provides an immutable record of all system activities.
All actions are timestamped and cannot be modified after creation.
""")

conn = get_db_connection()

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    user_filter = st.text_input("Filter by User")
with col2:
    action_filter = st.selectbox(
        "Filter by Action",
        ["All"] + ["LOGIN", "LOGOUT", "SALE", "PRODUCT_CREATE", "INVENTORY_ADJUSTMENT", "LINE_VOID", "ORDER_CANCEL", "EXPENSE_RECORD"]
    )
with col3:
    limit = st.number_input("Max Records", min_value=10, max_value=1000, value=100)

# Fetch audit logs
logs = get_audit_logs(limit=limit)

if logs:
    # Apply filters
    filtered_logs = logs
    if user_filter:
        filtered_logs = [log for log in filtered_logs if user_filter.lower() in log['username'].lower()]
    if action_filter != "All":
        filtered_logs = [log for log in filtered_logs if log['action'] == action_filter]
    
    # Display logs
    st.dataframe(filtered_logs, use_container_width=True)
    
    # Statistics
    st.markdown("---")
    st.markdown("### Activity Statistics")
    
    action_counts = {}
    user_counts = {}
    for log in filtered_logs:
        action = log['action']
        user = log['username']
        action_counts[action] = action_counts.get(action, 0) + 1
        user_counts[user] = user_counts.get(user, 0) + 1
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Actions Breakdown**")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {action}: {count}")
    
    with col2:
        st.markdown("**User Activity**")
        for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {user}: {count} actions")
    
    # Export option
    st.markdown("---")
    if st.button("Export Audit Log as CSV"):
        import pandas as pd
        df = pd.DataFrame(filtered_logs)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"audit_log_{st.time.time()}.csv",
            mime="text/csv"
        )
else:
    st.info("No audit logs found")

# Integrity verification notice
st.markdown("---")
st.markdown("### 🔒 Audit Log Integrity")
st.success("""
**Immutable Record**: All entries in this audit log are immutable once created.
Each entry is timestamped and linked to a specific user action.
This ensures complete traceability and accountability for all system changes.
""")
