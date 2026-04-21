"""
sidebar.py — call render_sidebar() at the top of every page.
Builds the persistent nav panel, respects role-based visibility.
"""
import streamlit as st
from users import can, current_role, current_user, logout
from styles import badge

# Nav items: (label, icon, page_file, required_permission_or_None)
NAV_ITEMS = [
    ("Dashboard",  "◈", "Home.py",                   None),
    ("POS",        "◉", "pages/1_POS.py",             "place_orders"),
    ("Inventory",  "◫", "pages/2_Inventory.py",       "view_inventory"),
    ("Orders",     "◎", "pages/3_Orders.py",          "view_orders"),
    ("Finance",    "◑", "pages/4_Finance.py",         "view_finance"),
    ("Audit Log",  "◌", "pages/5_Audit_Log.py",       "view_audit"),
]

ROLE_BADGE = {
    "admin":   ("admin",   "Administrator"),
    "manager": ("manager", "Manager"),
    "cashier": ("cashier", "Cashier"),
}

def render_sidebar(active_page: str = ""):
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────
        st.markdown("""
<div style="padding:22px 20px 16px;border-bottom:1px solid rgba(232,224,204,0.07)">
  <div style="font-family:Playfair Display,serif;font-size:22px;font-weight:600;color:#c49a2c;letter-spacing:.06em;line-height:1">Duka</div>
  <div style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#534f47;margin-top:3px">Shop Management</div>
</div>""", unsafe_allow_html=True)

        # ── User info ──────────────────────────────────────────
        user = current_user()
        if user:
            role = current_role()
            bs, blabel = ROLE_BADGE.get(role, ("neutral", role))
            st.markdown(f"""
<div style="padding:12px 20px 10px;border-bottom:1px solid rgba(232,224,204,0.07)">
  <div style="font-size:12.5px;color:#e8e0cc;font-family:Jost,sans-serif;margin-bottom:4px">{user.get('full_name','User')}</div>
  {badge(blabel, bs)}
</div>""", unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────────
        st.markdown('<div style="padding:10px 10px 0">', unsafe_allow_html=True)

        for label, icon, page, perm in NAV_ITEMS:
            # Hide items user can't access
            if perm and not can(perm):
                continue

            is_active = active_page == label
            if is_active:
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:9px;padding:9px 12px;margin-bottom:2px;border-radius:4px;background:rgba(196,154,44,0.11);border:1px solid rgba(196,154,44,0.22)">
  <span style="font-size:13px;color:#c49a2c;width:16px;text-align:center">{icon}</span>
  <span style="font-size:12.5px;font-weight:500;color:#c49a2c;font-family:Jost,sans-serif">{label}</span>
</div>""", unsafe_allow_html=True)
            else:
                # Use a button styled to look like a nav item
                if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                    st.switch_page(page)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Footer / sign out ──────────────────────────────────
        st.markdown('<div style="position:absolute;bottom:0;left:0;right:0;padding:14px 20px;border-top:1px solid rgba(232,224,204,0.07)">', unsafe_allow_html=True)
        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)
