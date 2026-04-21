import streamlit as st
import pandas as pd
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import inject, section_header, badge
from utils import get_sb, require_role, fmt_dt, ROLE_COLORS, current_user, current_role, logout, can

st.set_page_config(page_title="Audit Log — Duka", page_icon="◌", layout="wide", menu_items=None)
inject()
require_role(["admin", "manager"])

# Persistent Sidebar Navigation (same as Home.py)
user = current_user()
role = current_role()
name = user.get("full_name", "User")
username = user.get("username", "user")

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

sb = get_sb()
section_header("Audit Log", "Immutable record of all data changes")

st.markdown("""
<div style="background:rgba(200,146,42,0.07);border:1px solid rgba(200,146,42,0.18);border-radius:6px;padding:11px 16px;margin-bottom:20px;font-size:12px;color:#9a8f7a">
  This log is append-only. Entries cannot be modified or deleted. Every insert, update, void, and adjustment across all tables is recorded here.
</div>""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1: search_rid  = st.text_input("Search by record ID or reason")
with c2: table_filter = st.selectbox("Table", ["All","sales_orders","order_lines","catalog","inventory_ledger","purchase_invoices","expenses","profiles"])
with c3: action_filter = st.selectbox("Action", ["All","INSERT","UPDATE","VOID","ADJUST","DELETE"])
with c4: limit = st.selectbox("Show", [50, 100, 200])

# ── Query ────────────────────────────────────────────────────
q = sb.table("audit_log").select("*,profiles(full_name)").order("performed_at", desc=True).limit(limit)
if table_filter  != "All": q = q.eq("table_name",  table_filter)
if action_filter != "All": q = q.eq("action",       action_filter)
logs = q.execute().data

if search_rid:
    search_rid_lower = search_rid.lower()
    logs = [l for l in logs if
            search_rid_lower in (l.get("record_id") or "").lower() or
            search_rid_lower in (l.get("reason") or "").lower()]

# ── Action badge colors ───────────────────────────────────────
ACTION_COLORS = {
    "INSERT": "success",
    "UPDATE": "gold",
    "VOID":   "danger",
    "ADJUST": "info",
    "DELETE": "danger",
}

# ── Log table ─────────────────────────────────────────────────
if not logs:
    st.info("No audit entries found.")
else:
    for log in logs:
        action  = log.get("action", "?")
        table   = log.get("table_name", "?")
        perf_by = log.get("profiles", {})
        user_name = perf_by.get("full_name", "Unknown") if perf_by else "Unknown"
        ac = ACTION_COLORS.get(action, "neutral")

        header = f'{badge(action, ac)} <span style="color:#9a8f7a;font-size:12px;margin-left:6px">{table}</span> <span style="color:#5a5247;font-size:11px;margin-left:8px;font-family:DM Mono,monospace">{log["record_id"][:16]}...</span>'
        sub    = f'{fmt_dt(log.get("performed_at",""))} · {user_name}'
        if log.get("reason"):
            sub += f' · <em style="color:#9a8f7a">{log["reason"]}</em>'

        with st.expander(f"{action} on {table} — {user_name} — {fmt_dt(log.get('performed_at',''))}"):
            st.markdown(f"""
<div style="font-family:DM Mono,monospace;font-size:11px;color:#5a5247;margin-bottom:10px">
  Record ID: <span style="color:#9a8f7a">{log['record_id']}</span>
  &nbsp;·&nbsp; By: <span style="color:#9a8f7a">{user_name}</span>
  &nbsp;·&nbsp; At: <span style="color:#9a8f7a">{fmt_dt(log.get('performed_at',''))}</span>
</div>""", unsafe_allow_html=True)

            if log.get("reason"):
                st.markdown(f'<div style="background:rgba(200,146,42,0.07);border-left:2px solid #c8922a;padding:8px 12px;border-radius:0 4px 4px 0;font-size:12px;color:#9a8f7a;margin-bottom:10px"><strong style="color:#c8922a">Reason:</strong> {log["reason"]}</div>', unsafe_allow_html=True)

            if log.get("changed_fields"):
                st.markdown(f'<div style="font-size:11px;color:#5a5247;margin-bottom:8px">Changed fields: <span style="color:#9a8f7a">{", ".join(log["changed_fields"])}</span></div>', unsafe_allow_html=True)

            diff_cols = st.columns(2)
            with diff_cols[0]:
                if log.get("old_data"):
                    st.markdown('<h3>Before</h3>', unsafe_allow_html=True)
                    try:
                        old = json.loads(log["old_data"]) if isinstance(log["old_data"], str) else log["old_data"]
                        rows = "".join(f'<tr><td style="color:#5a5247;padding:3px 8px;font-size:11px">{k}</td><td style="color:#c0402a;padding:3px 8px;font-size:11px;font-family:DM Mono,monospace">{v}</td></tr>' for k, v in old.items())
                        st.markdown(f'<table style="width:100%;border-collapse:collapse;background:#141210;border:1px solid rgba(240,234,216,0.06);border-radius:4px">{rows}</table>', unsafe_allow_html=True)
                    except Exception:
                        st.code(str(log["old_data"]))

            with diff_cols[1]:
                if log.get("new_data"):
                    st.markdown('<h3>After</h3>', unsafe_allow_html=True)
                    try:
                        new = json.loads(log["new_data"]) if isinstance(log["new_data"], str) else log["new_data"]
                        rows = "".join(f'<tr><td style="color:#5a5247;padding:3px 8px;font-size:11px">{k}</td><td style="color:#4a8c5c;padding:3px 8px;font-size:11px;font-family:DM Mono,monospace">{v}</td></tr>' for k, v in new.items())
                        st.markdown(f'<table style="width:100%;border-collapse:collapse;background:#141210;border:1px solid rgba(240,234,216,0.06);border-radius:4px">{rows}</table>', unsafe_allow_html=True)
                    except Exception:
                        st.code(str(log["new_data"]))

# ── Summary stats ────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<h3>Summary</h3>', unsafe_allow_html=True)
if logs:
    action_counts = {}
    table_counts  = {}
    for l in logs:
        action_counts[l["action"]] = action_counts.get(l["action"], 0) + 1
        table_counts[l["table_name"]] = table_counts.get(l["table_name"], 0) + 1

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<h3>By Action</h3>', unsafe_allow_html=True)
        rows = "".join(f'<tr><td>{badge(a, ACTION_COLORS.get(a,"neutral"))}</td><td style="font-family:DM Mono,monospace;font-size:12px;color:#9a8f7a;padding-left:10px">{c}</td></tr>' for a, c in sorted(action_counts.items(), key=lambda x: -x[1]))
        st.markdown(f'<table style="border-collapse:collapse;width:100%">{rows}</table>', unsafe_allow_html=True)
    with c2:
        st.markdown('<h3>By Table</h3>', unsafe_allow_html=True)
        rows = "".join(f'<tr><td style="font-size:12px;color:#9a8f7a;padding:3px 0">{t}</td><td style="font-family:DM Mono,monospace;font-size:12px;color:#5a5247;padding-left:10px">{c}</td></tr>' for t, c in sorted(table_counts.items(), key=lambda x: -x[1]))
        st.markdown(f'<table style="border-collapse:collapse;width:100%">{rows}</table>', unsafe_allow_html=True)
