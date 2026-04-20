import streamlit as st
from datetime import datetime

# ── Hardcoded Users Database ──────────────────────────────────
# Format: username: {password, role, full_name}
USERS_DB = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "full_name": "System Administrator"
    },
    "manager": {
        "password": "manager123",
        "role": "manager",
        "full_name": "Store Manager"
    },
    "cashier": {
        "password": "cashier123",
        "role": "cashier",
        "full_name": "Front Desk Cashier"
    }
}

# ── Auth Functions ────────────────────────────────────────────
def login(username: str, password: str):
    """Authenticate user against hardcoded DB."""
    if username in USERS_DB:
        if USERS_DB[username]["password"] == password:
            user_data = {
                "username": username,
                "role": USERS_DB[username]["role"],
                "full_name": USERS_DB[username]["full_name"]
            }
            st.session_state.user = user_data
            st.session_state.role = user_data["role"]
            st.session_state.full_name = user_data["full_name"]
            st.session_state.logged_in = True
            return user_data
    return None

def logout():
    """Clear session state and rerun."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def current_user():
    """Get current user data."""
    return st.session_state.get("user")

def current_role():
    """Get current user role."""
    return st.session_state.get("role", "cashier")

def current_username():
    """Get current username."""
    user = current_user()
    return user["username"] if user else None

def require_auth():
    """Gate: redirect to login if not authenticated. Returns True if ok."""
    if not current_user():
        st.error("Please log in from the Home page.")
        st.stop()
    return True

def require_role(allowed: list):
    """Gate: stop if role not in allowed list."""
    require_auth()
    if current_role() not in allowed:
        st.error(f"Access denied. Required role: {', '.join(allowed)}. Your role: {current_role()}")
        st.stop()

def can(action: str) -> bool:
    """Convenience permission checks."""
    role = current_role()
    perms = {
        "view_finance":     ["admin", "manager"],
        "edit_orders":      ["admin", "manager"],
        "void_lines":       ["admin", "manager"],
        "receive_stock":    ["admin", "manager"],
        "adjust_inventory": ["admin"],
        "manage_users":     ["admin"],
        "delete_expense":   ["admin"],
        "view_audit":       ["admin", "manager"],
        "edit_prices":      ["admin", "manager"],
        "place_orders":     ["admin", "manager", "cashier"],
    }
    return role in perms.get(action, [])


# ── Supabase Client (for data only, no auth) ─────────────────
@st.cache_resource
def get_sb():
    """Get Supabase client for data operations."""
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except (KeyError, ImportError):
        return None


# ── Audit Log ────────────────────────────────────────────────
def audit(table: str, record_id: str, action: str, old_data=None, new_data=None, reason: str = None, changed_fields=None):
    sb = get_sb()
    if sb is None:
        return
    uid = current_username()
    entry = {
        "table_name": table,
        "record_id": str(record_id),
        "action": action,
        "old_data": str(old_data) if old_data else None,
        "new_data": str(new_data) if new_data else None,
        "changed_fields": changed_fields,
        "reason": reason,
        "performed_by": uid,
    }
    try:
        sb.table("audit_log").insert(entry).execute()
    except Exception:
        pass  # Fail silently for audit logs


# ── Inventory helpers ─────────────────────────────────────────
def load_inventory():
    sb = get_sb()
    if sb is None:
        return []
    cat = sb.table("catalog").select("item_id,name,type,uom,current_landed_cost,default_sell_price,is_active").eq("is_active", True).order("name").execute().data
    led = sb.table("inventory_ledger").select("item_id,quantity_change").execute().data
    totals = {}
    for r in led:
        totals[r["item_id"]] = totals.get(r["item_id"], 0) + r["quantity_change"]
    for c in cat:
        c["stock"] = round(max(totals.get(c["item_id"], 0), 0), 3)
    return cat or []

def moving_avg_landed_cost(sb, item_id, new_qty, new_lc):
    if sb is None:
        return new_lc
    cat = sb.table("catalog").select("current_landed_cost").eq("item_id", item_id).single().execute()
    led = sb.table("inventory_ledger").select("quantity_change").eq("item_id", item_id).execute()
    old_cost = cat.data["current_landed_cost"] if cat.data else 0
    old_qty = max(sum(r["quantity_change"] for r in led.data) if led.data else 0, 0)
    if old_qty + new_qty > 0:
        return round(((old_qty * old_cost) + (new_qty * new_lc)) / (old_qty + new_qty), 2)
    return round(new_lc, 2)


# ── Format helpers ────────────────────────────────────────────
def fmt(n):
    try:
        return f"{float(n):,.2f}"
    except (TypeError, ValueError):
        return "—"

def fmt_dt(s):
    if not s:
        return "—"
    try:
        return datetime.fromisoformat(s.replace("Z","")).strftime("%d %b %Y %H:%M")
    except Exception:
        return s

STATUS_COLORS = {
    "Pending":   "gold",
    "Ready":     "info",
    "Delivered": "success",
    "Cancelled": "danger",
}
ROLE_COLORS = {
    "admin":   "danger",
    "manager": "gold",
    "cashier": "neutral",
}
