import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import inject, section_header, badge, metric_card
from utils import get_sb, require_auth, current_username, audit, fmt, fmt_dt, can, STATUS_COLORS, ROLE_COLORS, current_user, current_role, logout

st.set_page_config(page_title="Orders — Duka", page_icon="◎", layout="wide", menu_items=None)
inject()
require_auth()

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
section_header("Orders", "Manage, edit & track all orders")

# ── Filters ───────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
with col_f1: search = st.text_input("Search by customer name")
with col_f2: status_filter = st.selectbox("Status", ["All","Pending","Ready","Delivered","Cancelled"])
with col_f3: limit = st.selectbox("Show", [25, 50, 100, 200])

q = sb.table("sales_orders").select("*").order("created_at", desc=True).limit(limit)
if status_filter != "All":
    q = q.eq("status", status_filter)
orders = q.execute().data

if search:
    orders = [o for o in orders if search.lower() in o["customer_name"].lower()]

# ── Orders table ──────────────────────────────────────────────
if not orders:
    st.info("No orders found.")
else:
    for order in orders:
        status = order["status"]
        sc = STATUS_COLORS.get(status, "neutral")
        with st.expander(f"{order['customer_name']} — {fmt(order['total_amount'])} — {badge(status, sc)} — {fmt_dt(order['created_at'])}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Order lines
                lines = sb.table("order_lines").select("*,catalog(name,uom)").eq("order_id", order["order_id"]).execute().data
                if lines:
                    rows_html = ""
                    for l in lines:
                        void_badge = badge("VOIDED","danger") if l.get("is_voided") else ""
                        item_name = l["catalog"]["name"] if l.get("catalog") else "—"
                        uom = l["catalog"]["uom"] if l.get("catalog") else ""
                        line_style = "color:#5a5247;text-decoration:line-through" if l.get("is_voided") else "color:#f0ead8"
                        rows_html += f"""
<tr>
  <td style="{line_style};font-size:13px">{item_name} {void_badge}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right;color:#9a8f7a">{l['quantity']} {uom}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right;color:#9a8f7a">{fmt(l['unit_price'])}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right;color:#c8922a">{fmt(l['quantity']*l['unit_price'])}</td>
</tr>"""
                        if l.get("void_reason"):
                            rows_html += f'<tr><td colspan="4" style="font-size:11px;color:#5a5247;padding:0 14px 8px;font-style:italic">Void reason: {l["void_reason"]}</td></tr>'

                    st.markdown(f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:6px;overflow:hidden;margin-bottom:12px">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="border-bottom:1px solid rgba(240,234,216,0.08)">
      <th style="text-align:left;padding:8px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Item</th>
      <th style="text-align:right;padding:8px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Qty</th>
      <th style="text-align:right;padding:8px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Price</th>
      <th style="text-align:right;padding:8px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Total</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
    <tfoot><tr style="border-top:1px solid rgba(240,234,216,0.08)">
      <td colspan="3" style="padding:10px 14px;font-size:11px;color:#5a5247">Total · Deposit · Balance</td>
      <td style="padding:10px 14px;text-align:right;font-family:DM Mono,monospace;font-size:12px;color:#c8922a">{fmt(order['total_amount'])} · {fmt(order['deposit_paid'])} · {fmt(order['balance_due'])}</td>
    </tr></tfoot>
  </table>
</div>""", unsafe_allow_html=True)

                    # ── Void a line (manager/admin) ───────────────────
                    if can("void_lines") and status not in ["Cancelled","Delivered"]:
                        active_lines = [l for l in lines if not l.get("is_voided")]
                        if active_lines:
                            st.markdown('<h3>Void a Line Item</h3>', unsafe_allow_html=True)
                            void_options = {f"{l['catalog']['name']} × {l['quantity']}": l for l in active_lines if l.get("catalog")}
                            if void_options:
                                with st.form(f"void_{order['order_id']}"):
                                    void_sel    = st.selectbox("Select line to void", list(void_options.keys()))
                                    void_reason = st.text_input("Void reason (required)")
                                    if st.form_submit_button("Void Line", type="primary"):
                                        if not void_reason:
                                            st.error("Reason required.")
                                        else:
                                            vl = void_options[void_sel]
                                            old = dict(vl)
                                            # Void the line
                                            sb.table("order_lines").update({
                                                "is_voided": True, "void_reason": void_reason,
                                                "voided_by": current_uid()
                                            }).eq("line_id", vl["line_id"]).execute()
                                            # Reverse inventory
                                            sb.table("inventory_ledger").insert({
                                                "item_id": vl["item_id"], "transaction_type": "VOID_SALE",
                                                "quantity_change": vl["quantity"],
                                                "unit_cost": vl["line_cogs"] / vl["quantity"] if vl["quantity"] else 0,
                                                "reference_id": order["order_id"],
                                                "notes": f"Void: {void_reason}", "created_by": current_uid()
                                            }).execute()
                                            # Recalculate order total
                                            remaining = sb.table("order_lines").select("quantity,unit_price").eq("order_id", order["order_id"]).eq("is_voided", False).execute().data
                                            new_total = sum(l["quantity"]*l["unit_price"] for l in remaining)
                                            old_order = dict(order)
                                            sb.table("sales_orders").update({"total_amount": new_total}).eq("order_id", order["order_id"]).execute()
                                            audit("order_lines", vl["line_id"], "VOID", old_data=old, reason=void_reason)
                                            audit("sales_orders", order["order_id"], "UPDATE", old_data=old_order, new_data={"total_amount": new_total}, changed_fields=["total_amount"], reason=f"Line voided: {void_reason}")
                                            st.success("Line voided and inventory reversed."); st.rerun()

            with col2:
                st.markdown('<h3>Order Details</h3>', unsafe_allow_html=True)
                st.markdown(f"""
<div style="font-size:12px;color:#9a8f7a;line-height:1.9">
  <span style="color:#5a5247">Customer:</span> <span style="color:#f0ead8">{order['customer_name']}</span><br>
  <span style="color:#5a5247">Phone:</span> {order.get('customer_phone') or '—'}<br>
  <span style="color:#5a5247">Created:</span> {fmt_dt(order['created_at'])}<br>
  <span style="color:#5a5247">Notes:</span> {order.get('notes') or '—'}
</div>""", unsafe_allow_html=True)

                # ── Edit order (manager/admin) ─────────────────────
                if can("edit_orders"):
                    st.markdown('<h3 style="margin-top:14px">Edit Order</h3>', unsafe_allow_html=True)
                    with st.form(f"edit_{order['order_id']}"):
                        new_status  = st.selectbox("Status", ["Pending","Ready","Delivered","Cancelled"],
                                        index=["Pending","Ready","Delivered","Cancelled"].index(status))
                        new_deposit = st.number_input("Deposit Paid", min_value=0.0,
                                        value=float(order["deposit_paid"]), step=100.0)
                        new_notes   = st.text_input("Notes", value=order.get("notes") or "")
                        edit_reason = st.text_input("Reason for change (required)")

                        if st.form_submit_button("Save Changes", type="primary"):
                            if not edit_reason:
                                st.error("Reason required.")
                            else:
                                changes = {}
                                changed_fields = []
                                old_data = dict(order)
                                if new_status != status:
                                    changes["status"] = new_status; changed_fields.append("status")
                                if new_deposit != order["deposit_paid"]:
                                    changes["deposit_paid"] = new_deposit; changed_fields.append("deposit_paid")
                                if new_notes != (order.get("notes") or ""):
                                    changes["notes"] = new_notes; changed_fields.append("notes")
                                if changes:
                                    changes["updated_at"] = "now()"
                                    sb.table("sales_orders").update(changes).eq("order_id", order["order_id"]).execute()
                                    audit("sales_orders", order["order_id"], "UPDATE",
                                          old_data=old_data, new_data=changes,
                                          changed_fields=changed_fields, reason=edit_reason)
                                    st.success("Order updated."); st.rerun()
                                else:
                                    st.info("No changes detected.")
