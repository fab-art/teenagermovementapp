import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from styles import inject, badge, section_header, metric_card
from utils import login, logout, current_user, current_role, can, fmt_dt, ROLE_COLORS, get_sb

st.set_page_config(page_title="Duka ERP", page_icon="🪟", layout="wide", menu_items=None)
inject()

# ── Authentication Check ──────────────────────────────────────
if not current_user():
    # Login Page
    st.markdown("""
<div style="max-width:420px;margin:8vh auto 0;">
  <div style="text-align:center;margin-bottom:32px">
    <div style="font-family:Cormorant Garamond,serif;font-size:48px;font-weight:600;color:#c8922a;letter-spacing:.1em">Duka</div>
    <div style="font-size:11px;letter-spacing:.25em;text-transform:uppercase;color:#5a5247;margin-top:6px">Shop Management System</div>
  </div>
</div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown('<h3 style="margin-bottom:20px;text-align:center">Sign In</h3>', unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="admin, manager, or cashier")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Authenticating..."):
                    profile = login(username.lower().strip(), password)
                    if profile:
                        st.success(f"Welcome, {profile['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Try: admin/admin123, manager/manager123, cashier/cashier123")
        
        # Demo credentials info
        st.markdown("""
<div style="margin-top:24px;padding:16px;background:rgba(200,146,42,0.08);border-radius:8px;border:1px solid rgba(200,146,42,0.2)">
  <div style="font-size:12px;color:#f0ead8;margin-bottom:8px"><strong>Demo Credentials:</strong></div>
  <div style="font-size:11px;color:#c8922a;font-family:DM Mono,monospace">
    👑 Admin: <code>admin</code> / <code>admin123</code><br>
    📋 Manager: <code>manager</code> / <code>manager123</code><br>
    💰 Cashier: <code>cashier</code> / <code>cashier123</code>
  </div>
</div>""", unsafe_allow_html=True)
    
    st.stop()

# ── Authenticated App with Persistent Sidebar ─────────────────
user = current_user()
role = current_role()
name = user.get("full_name", "User")
username = user.get("username", "user")

# Persistent Sidebar Navigation
with st.sidebar:
    st.markdown(f"""
<div style="padding:16px 0;border-bottom:1px solid rgba(240,234,216,0.1);margin-bottom:16px">
  <div style="font-family:Cormorant Garamond,serif;font-size:24px;font-weight:600;color:#c8922a;letter-spacing:.08em">Duka</div>
  <div style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#5a5247;margin-top:4px">Shop Management</div>
</div>
<div style="padding:12px;background:rgba(200,146,42,0.08);border-radius:6px;margin-bottom:16px;border:1px solid rgba(200,146,42,0.15)">
  <div style="font-size:13px;color:#f0ead8;font-weight:500">{name}</div>
  <div style="margin-top:4px;display:flex;align-items:center;gap:6px">
    <span style="font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">@{username}</span>
    <span style="width:4px;height:4px;background:#5a5247;border-radius:50%"></span>
    {badge(role.upper(), ROLE_COLORS.get(role,'neutral'))}
  </div>
</div>""", unsafe_allow_html=True)
    
    # Navigation Menu
    st.markdown('<div style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#5a5247;margin:16px 0 8px">Navigation</div>', unsafe_allow_html=True)
    
    # Always show all pages, but role-based access is handled in each page
    menu_items = {
        "🏠 Home": "/",
        "💳 POS": "/1_POS",
        "📦 Inventory": "/2_Inventory",
        "📋 Orders": "/3_Orders",
    }
    
    if can("view_finance"):
        menu_items["💰 Finance"] = "/4_Finance"
    
    if can("view_audit"):
        menu_items["📜 Audit Log"] = "/5_Audit_Log"
    
    for label, path in menu_items.items():
        if st.button(label, use_container_width=True, key=f"nav_{label}"):
            st.switch_page(f"pages{path}.py" if path != "/" else "Home.py")
    
    st.markdown('<div style="height:1px;background:rgba(240,234,216,0.1);margin:16px 0"></div>', unsafe_allow_html=True)
    
    if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
        logout()

# ── Main Content Area ─────────────────────────────────────────
section_header("Dashboard", f"Welcome back, {name}")

sb = get_sb()

# KPI row - handle case where Supabase is not configured
try:
    if sb:
        orders = sb.table("sales_orders").select("total_amount,deposit_paid,balance_due,status").eq("is_active", True).execute().data or []
        inventory = sb.table("catalog").select("item_id").eq("is_active", True).execute().data or []
        lines = sb.table("order_lines").select("line_cogs").eq("is_voided", False).execute().data or []
        expenses = sb.table("expenses").select("amount").eq("is_voided", False).execute().data or []
    else:
        orders, inventory, lines, expenses = [], [], [], []
except Exception:
    orders, inventory, lines, expenses = [], [], [], []

revenue = sum(o.get("total_amount", 0) for o in orders)
balance = sum(o.get("balance_due", 0) for o in orders if o.get("status") not in ["Cancelled", "Delivered"])
cogs = sum(l.get("line_cogs", 0) for l in lines)
total_exp = sum(e.get("amount", 0) for e in expenses)
pending = sum(1 for o in orders if o.get("status") == "Pending")

cols = st.columns(5)
with cols[0]: st.markdown(metric_card("Revenue", f"{revenue:,.0f}", "gold"), unsafe_allow_html=True)
with cols[1]: st.markdown(metric_card("Gross Profit", f"{revenue-cogs:,.0f}", "success"), unsafe_allow_html=True)
with cols[2]: st.markdown(metric_card("Outstanding Balance", f"{balance:,.0f}", "danger"), unsafe_allow_html=True)
with cols[3]: st.markdown(metric_card("Pending Orders", str(pending), "gold"), unsafe_allow_html=True)
with cols[4]: st.markdown(metric_card("Catalog Items", str(len(inventory))), unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Recent orders
st.markdown('<h3>Recent Orders</h3>', unsafe_allow_html=True)
try:
    if sb:
        recent = sb.table("sales_orders").select("*").order("created_at", desc=True).limit(8).execute().data or []
    else:
        recent = []
except Exception:
    recent = []

if recent:
    import pandas as pd
    df = pd.DataFrame(recent)[["created_at","customer_name","customer_phone","status","total_amount","deposit_paid","balance_due"]]
    df.columns = ["Date","Customer","Phone","Status","Total","Deposit","Balance"]
    df["Date"] = df["Date"].apply(fmt_dt)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No orders found. Start by creating orders in the POS page.")

# ── User Management (admin only) ─────────────────────────────
if can("manage_users"):
    st.markdown("<hr>", unsafe_allow_html=True)
    section_header("User Management", "Admin only - Pre-configured Users")
    
    st.markdown("""
<div style="padding:16px;background:rgba(200,146,42,0.08);border-radius:8px;border:1px solid rgba(200,146,42,0.15);margin-bottom:16px">
  <div style="font-size:13px;color:#f0ead8;margin-bottom:8px"><strong>ℹ️ Hardcoded User Accounts</strong></div>
  <div style="font-size:12px;color:#c8922a;line-height:1.8">
    This system uses pre-configured user accounts. To add or modify users, edit the <code>USERS_DB</code> dictionary in <code>utils.py</code>.
  </div>
</div>""", unsafe_allow_html=True)
    
    # Display current users
    from utils import USERS_DB
    for uname, udata in USERS_DB.items():
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1: st.markdown(f'<span style="color:#f0ead8;font-size:13px">{udata["full_name"]}</span>', unsafe_allow_html=True)
        with col2: st.markdown(badge(udata["role"].upper(), ROLE_COLORS.get(udata["role"],"neutral")), unsafe_allow_html=True)
        with col3: st.markdown(f'<span style="font-size:11px;color:#5a5247;font-family:DM Mono,monospace">@{uname}</span>', unsafe_allow_html=True)
