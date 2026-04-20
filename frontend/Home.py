import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from styles import inject, badge, section_header
from utils import get_sb, login, logout, current_user, current_role, can, audit, fmt_dt, ROLE_COLORS

st.set_page_config(page_title="Duka ERP", page_icon="🪟", layout="wide")
inject()

# ── Login gate ────────────────────────────────────────────────
if not current_user():
    st.markdown("""
<div style="max-width:420px;margin:6vh auto 0;">
  <div style="text-align:center;margin-bottom:32px">
    <div style="font-family:Cormorant Garamond,serif;font-size:42px;font-weight:600;color:#c8922a;letter-spacing:.1em">Duka</div>
    <div style="font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#5a5247;margin-top:4px">Shop Management System</div>
  </div>
</div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Tabbed interface for Sign In / Sign Up
        tab_signin, tab_signup = st.tabs(["Sign In", "Sign Up"])
        
        with tab_signin:
            with st.form("login_form"):
                st.markdown('<h3 style="margin-bottom:16px">Sign In</h3>', unsafe_allow_html=True)
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Enter email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            profile = login(email, password)
                            st.success(f"Welcome, {profile['full_name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login failed: {str(e)}")
            
            # Google Sign In Button
            st.markdown('<div style="margin:16px 0;text-align:center">— OR —</div>', unsafe_allow_html=True)
            if st.button("🔐 Sign in with Google", use_container_width=True, type="secondary"):
                try:
                    sb = get_sb()
                    # Get the OAuth URL for Google provider
                    oauth_url = sb.auth.sign_in_with_oauth({
                        'provider': 'google',
                        'options': {
                            'redirectTo': st.secrets.get("SUPABASE_REDIRECT_URL", os.environ.get("SUPABASE_REDIRECT_URL", ""))
                        }
                    })
                    # Redirect user to Google OAuth
                    st.redirect(oauth_url.url)
                except Exception as e:
                    st.error(f"Google sign-in failed: {str(e)}")
        
        with tab_signup:
            with st.form("signup_form"):
                st.markdown('<h3 style="margin-bottom:16px">Create Account</h3>', unsafe_allow_html=True)
                signup_name = st.text_input("Full Name", key="signup_name")
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_password", help="Minimum 6 characters")
                signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
                submitted_signup = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
            
            if submitted_signup:
                if not signup_name or not signup_email or not signup_password:
                    st.error("All fields are required.")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match.")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            sb = get_sb()
                            # Create user via Supabase Auth
                            res = sb.auth.sign_up({
                                "email": signup_email,
                                "password": signup_password,
                                "options": {
                                    "data": {"full_name": signup_name}
                                }
                            })
                            user = res.user
                            # Create profile entry
                            sb.table("profiles").insert({
                                "user_id": user.id,
                                "full_name": signup_name,
                                "role": "cashier"  # Default role for new signups
                            }).execute()
                            audit("profiles", user.id, "INSERT", new_data={"email": signup_email, "role": "cashier"}, reason="User self-registered")
                            st.success("Account created! Please check your email to verify, or sign in below.")
                        except Exception as e:
                            st.error(f"Sign up failed: {str(e)}")
            
            # Google Sign Up Button
            st.markdown('<div style="margin:16px 0;text-align:center">— OR —</div>', unsafe_allow_html=True)
            if st.button("🔐 Sign up with Google", use_container_width=True, type="secondary", key="google_signup"):
                try:
                    sb = get_sb()
                    oauth_url = sb.auth.sign_in_with_oauth({
                        'provider': 'google',
                        'options': {
                            'redirectTo': st.secrets.get("SUPABASE_REDIRECT_URL", os.environ.get("SUPABASE_REDIRECT_URL", ""))
                        }
                    })
                    st.redirect(oauth_url.url)
                except Exception as e:
                    st.error(f"Google sign-up failed: {str(e)}")
    
    st.stop()

# ── Authenticated ─────────────────────────────────────────────
user = current_user()
role = current_role()
name = st.session_state.get("full_name", "User")

# Sidebar info
with st.sidebar:
    st.markdown(f"""
<div style="padding:12px 0;border-bottom:1px solid rgba(240,234,216,0.08);margin-bottom:8px">
  <div style="font-family:Cormorant Garamond,serif;font-size:20px;color:#c8922a;letter-spacing:.06em">Duka</div>
  <div style="font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#5a5247">Shop Management</div>
</div>
<div style="padding:10px 0;border-bottom:1px solid rgba(240,234,216,0.08);margin-bottom:8px">
  <div style="font-size:12px;color:#f0ead8">{name}</div>
  <div style="margin-top:4px">{badge(role.upper(), ROLE_COLORS.get(role,'neutral'))}</div>
</div>""", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()

section_header("Dashboard", f"Welcome back, {name}")

sb = get_sb()

# KPI row
orders = sb.table("sales_orders").select("total_amount,deposit_paid,balance_due,status").execute().data
inventory = sb.table("catalog").select("item_id").eq("is_active", True).execute().data
lines = sb.table("order_lines").select("line_cogs").eq("is_voided", False).execute().data
expenses = sb.table("expenses").select("amount").eq("is_voided", False).execute().data

revenue = sum(o["total_amount"] for o in orders)
balance = sum(o["balance_due"] for o in orders if o["status"] not in ["Cancelled", "Delivered"])
cogs = sum(l["line_cogs"] for l in lines)
total_exp = sum(e["amount"] for e in expenses)
pending = sum(1 for o in orders if o["status"] == "Pending")

cols = st.columns(5)
from styles import metric_card
with cols[0]: st.markdown(metric_card("Revenue", f"{revenue:,.0f}",    "gold"),    unsafe_allow_html=True)
with cols[1]: st.markdown(metric_card("Gross Profit", f"{revenue-cogs:,.0f}", "success"), unsafe_allow_html=True)
with cols[2]: st.markdown(metric_card("Outstanding Balance", f"{balance:,.0f}", "danger"), unsafe_allow_html=True)
with cols[3]: st.markdown(metric_card("Pending Orders", str(pending), "gold"),    unsafe_allow_html=True)
with cols[4]: st.markdown(metric_card("Catalog Items", str(len(inventory))),      unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Recent orders
st.markdown('<h3>Recent Orders</h3>', unsafe_allow_html=True)
recent = sb.table("sales_orders").select("*").order("created_at", desc=True).limit(8).execute().data
if recent:
    import pandas as pd
    df = pd.DataFrame(recent)[["created_at","customer_name","customer_phone","status","total_amount","deposit_paid","balance_due"]]
    df.columns = ["Date","Customer","Phone","Status","Total","Deposit","Balance"]
    df["Date"] = df["Date"].apply(fmt_dt)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── User Management (admin only) ─────────────────────────────
if can("manage_users"):
    st.markdown("<hr>", unsafe_allow_html=True)
    section_header("User Management", "Admin only")

    profiles = sb.table("profiles").select("user_id,full_name,role,created_at").order("created_at").execute().data

    for p in profiles:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1: st.markdown(f'<span style="color:#f0ead8;font-size:13px">{p["full_name"]}</span>', unsafe_allow_html=True)
        with col2: st.markdown(badge(p["role"].upper(), ROLE_COLORS.get(p["role"],"neutral")), unsafe_allow_html=True)
        with col3: st.markdown(f'<span style="font-size:11px;color:#5a5247;font-family:DM Mono,monospace">{fmt_dt(p["created_at"])}</span>', unsafe_allow_html=True)
        with col4:
            if p["user_id"] != str(user.id):
                new_role = st.selectbox("", ["cashier","manager","admin"], key=f"role_{p['user_id']}",
                    index=["cashier","manager","admin"].index(p["role"]), label_visibility="collapsed")
                if new_role != p["role"]:
                    old = dict(p)
                    sb.table("profiles").update({"role": new_role}).eq("user_id", p["user_id"]).execute()
                    audit("profiles", p["user_id"], "UPDATE", old_data=old, new_data={"role": new_role}, changed_fields=["role"], reason="Role changed by admin")
                    st.success(f"Role updated to {new_role}")
                    st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    with st.expander("Invite New User"):
        with st.form("invite_form"):
            ni_email = st.text_input("Email")
            ni_name  = st.text_input("Full Name")
            ni_pass  = st.text_input("Temporary Password", type="password")
            ni_role  = st.selectbox("Role", ["cashier","manager","admin"])
            if st.form_submit_button("Create User", type="primary"):
                try:
                    res = sb.auth.admin.create_user({
                        "email": ni_email, "password": ni_pass,
                        "user_metadata": {"full_name": ni_name},
                        "email_confirm": True
                    })
                    sb.table("profiles").update({"role": ni_role, "full_name": ni_name}).eq("user_id", res.user.id).execute()
                    audit("profiles", res.user.id, "INSERT", new_data={"email": ni_email, "role": ni_role}, reason="User created by admin")
                    st.success(f"User {ni_email} created with role {ni_role}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
