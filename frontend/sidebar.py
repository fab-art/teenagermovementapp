"""
sidebar.py — call render_sidebar() at the top of every page.
Builds the persistent nav panel and role-aware navigation.
"""

import streamlit as st
from users import can, current_role, current_user, logout
from styles import badge

# Nav items: (label, icon, page_file, required_permission_or_None)
NAV_ITEMS = [
    ("Dashboard", "◈", "Home.py", None),
    ("POS", "◉", "pages/1_POS.py", "place_orders"),
    ("Inventory", "◫", "pages/2_Inventory.py", "view_inventory"),
    ("Orders", "◎", "pages/3_Orders.py", "view_orders"),
    ("Finance", "◑", "pages/4_Finance.py", "view_finance"),
    ("Audit Log", "◌", "pages/5_Audit_Log.py", "view_audit"),
]

ROLE_BADGE = {
    "admin": ("admin", "Administrator"),
    "manager": ("manager", "Manager"),
    "cashier": ("cashier", "Cashier"),
}


def _visible_nav_items():
    """Return navigation items filtered by user permissions."""
    return [
        (label, icon, page)
        for label, icon, page, perm in NAV_ITEMS
        if perm is None or can(perm)
    ]


def _render_user_profile():
    """Render user profile section in sidebar."""
    user = current_user()
    if not user:
        return
    
    role = current_role()
    bs, blabel = ROLE_BADGE.get(role, ("neutral", role))
    st.markdown(
        f"""
<div style="padding:10px 20px 12px;border-bottom:1px solid rgba(232,224,204,0.07);margin-bottom:8px">
  <div style="font-size:12.5px;color:#e8e0cc;font-family:Jost,sans-serif;margin-bottom:4px">{user.get('full_name','User')}</div>
  {badge(blabel, bs)}
</div>""",
        unsafe_allow_html=True,
    )


def _render_current_section(active_page: str):
    """Render current section indicator."""
    if not active_page:
        return
    st.markdown(
        f"""<div style="padding:0 20px 8px;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:#534f47">
Current section · <span style="color:#c49a2c">{active_page}</span>
</div>""",
        unsafe_allow_html=True,
    )


def _render_nav_links(active_page: str):
    """Render navigation links in sidebar."""
    for label, icon, page in _visible_nav_items():
        if label == active_page:
            st.markdown(
                f"""<div style="margin:2px 10px;padding:9px 12px;border-radius:4px;
background:rgba(196,154,44,0.11);border:1px solid rgba(196,154,44,0.22);
color:#c49a2c;font-size:12.5px;font-family:Jost,sans-serif;font-weight:500">
{icon} &nbsp; {label}
</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.page_link(page, label=f"{icon}  {label}")


def _render_signout():
    """Render sign out button."""
    st.markdown(
        "<div style='margin-top:16px;border-top:1px solid rgba(232,224,204,0.07);padding-top:12px'>",
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
        logout()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_top_navigation(active_page: str):
    """Render top navigation bar."""
    nav_items = _visible_nav_items()
    if not nav_items:
        return
    
    st.markdown(
        """<div style="margin:-8px 0 14px;padding:8px 10px;border:1px solid rgba(232,224,204,0.07);
border-radius:6px;background:#1a1814"><span style="font-size:9px;letter-spacing:.12em;
text-transform:uppercase;color:#534f47">Quick Navigation</span></div>""",
        unsafe_allow_html=True,
    )
    
    cols = st.columns(len(nav_items))
    for idx, (label, icon, page) in enumerate(nav_items):
        with cols[idx]:
            is_active = label == active_page
            btn_label = f"{icon} {label}"
            if st.button(
                btn_label,
                key=f"topnav_{label.lower().replace(' ', '_')}",
                use_container_width=True,
                disabled=is_active,
            ):
                st.switch_page(page)


SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {
    background: #1a1812 !important;
    border-right: 1px solid rgba(232,224,204,0.07) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    gap: 9px !important;
    padding: 9px 12px !important;
    margin: 2px 10px !important;
    border-radius: 4px !important;
    font-size: 12.5px !important;
    font-family: Jost, sans-serif !important;
    font-weight: 400 !important;
    color: #9a9080 !important;
    text-decoration: none !important;
    border: 1px solid transparent !important;
    transition: background .15s, color .15s !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(232,224,204,0.05) !important;
    color: #e8e0cc !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink-active"] a {
    background: rgba(196,154,44,0.11) !important;
    border-color: rgba(196,154,44,0.22) !important;
    color: #c49a2c !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid rgba(232,224,204,0.1) !important;
    color: #534f47 !important;
    font-size: 11.5px !important;
    font-family: Jost, sans-serif !important;
    letter-spacing: .05em !important;
    margin: 0 10px !important;
    width: calc(100% - 20px) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    border-color: rgba(184,64,48,0.4) !important;
    color: #b84030 !important;
}
</style>
"""

BRANDING_HTML = """
<div style="padding:22px 20px 16px;border-bottom:1px solid rgba(232,224,204,0.07);margin-bottom:4px">
  <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:#c49a2c;letter-spacing:.06em;line-height:1">Duka</div>
  <div style="font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#534f47;margin-top:3px">Shop Management</div>
</div>
"""


def render_sidebar(active_page: str = ""):
    """Render the sidebar with branding, user profile, navigation, and sign-out."""
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(BRANDING_HTML, unsafe_allow_html=True)
        _render_user_profile()
        _render_current_section(active_page)
        _render_nav_links(active_page)
        _render_signout()

    _render_top_navigation(active_page)
