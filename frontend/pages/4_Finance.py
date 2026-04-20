import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import inject, section_header, badge, metric_card
from utils import get_sb, require_role, current_uid, audit, fmt, fmt_dt, can, ROLE_COLORS

st.set_page_config(page_title="Finance — Duka", page_icon="◉", layout="wide")
inject()
require_role(["admin", "manager"])

with st.sidebar:
    from utils import current_role, logout
    name = st.session_state.get("full_name", "User")
    role = current_role()
    st.markdown(f"""
<div style="padding:12px 0;border-bottom:1px solid rgba(240,234,216,0.08);margin-bottom:8px">
  <div style="font-family:Cormorant Garamond,serif;font-size:20px;color:#c8922a">Duka</div>
</div>
<div style="padding:8px 0;margin-bottom:8px">
  <div style="font-size:12px;color:#f0ead8">{name}</div>
  <div style="margin-top:4px">{badge(role.upper(), ROLE_COLORS.get(role,'neutral'))}</div>
</div>""", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()

sb = get_sb()
section_header("Finance", "P&L, payables & expense management")

# ── Pull data ─────────────────────────────────────────────────
orders   = sb.table("sales_orders").select("total_amount,status").neq("status","Cancelled").execute().data
lines    = sb.table("order_lines").select("line_cogs").eq("is_voided", False).execute().data
expenses = sb.table("expenses").select("amount").eq("is_voided", False).execute().data
invoices = sb.table("purchase_invoices").select("landed_cost,suppliers(name)").eq("status","On Credit").eq("is_voided",False).execute().data

revenue   = sum(o["total_amount"] for o in orders)
cogs      = sum(l["line_cogs"] for l in lines)
gross     = revenue - cogs
total_exp = sum(e["amount"] for e in expenses)
net       = gross - total_exp

# ── KPI metrics ───────────────────────────────────────────────
cols = st.columns(5)
kpis = [
    ("Revenue",       fmt(revenue), "gold"),
    ("COGS",          fmt(cogs),    "cream"),
    ("Gross Profit",  fmt(gross),   "success" if gross >= 0 else "danger"),
    ("Expenses",      fmt(total_exp), "danger"),
    ("Net Profit",    fmt(net),     "success" if net >= 0 else "danger"),
]
for i, (label, value, color) in enumerate(kpis):
    with cols[i]:
        st.markdown(metric_card(label, value, color), unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

tab_ap, tab_exp, tab_invoices = st.tabs(["Accounts Payable", "Expenses", "Purchase Invoices"])

# ── Accounts Payable ─────────────────────────────────────────
with tab_ap:
    if invoices:
        ap = {}
        for inv in invoices:
            name = inv["suppliers"]["name"] if inv.get("suppliers") else "Unknown"
            ap[name] = ap.get(name, 0) + (inv["landed_cost"] or 0)
        total_ap = sum(ap.values())

        rows = "".join(f"""
<tr>
  <td style="color:#f0ead8;font-size:13px">{n}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;color:#c0402a;text-align:right">{fmt(a)}</td>
  <td style="font-size:11px;color:#5a5247;text-align:right">{(a/total_ap*100):.1f}%</td>
</tr>""" for n, a in sorted(ap.items(), key=lambda x: -x[1]))

        st.markdown(f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:8px;overflow:hidden">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="border-bottom:1px solid rgba(240,234,216,0.08)">
      <th style="text-align:left;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Supplier</th>
      <th style="text-align:right;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Owed</th>
      <th style="text-align:right;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Share</th>
    </tr></thead>
    <tbody>{rows}</tbody>
    <tfoot><tr style="border-top:1px solid rgba(240,234,216,0.08)">
      <td colspan="2" style="padding:10px 14px;font-family:Cormorant Garamond,serif;font-size:18px;color:#c0402a">Total Payable</td>
      <td style="padding:10px 14px;font-family:DM Mono,monospace;font-size:13px;color:#c0402a;text-align:right">{fmt(total_ap)}</td>
    </tr></tfoot>
  </table>
</div>""", unsafe_allow_html=True)

        # Mark invoice as paid
        if can("edit_orders"):
            st.markdown("")
            st.markdown('<h3 style="margin-top:8px">Mark Invoice Paid</h3>', unsafe_allow_html=True)
            credit_invs = sb.table("purchase_invoices").select("invoice_id,quantity,purchase_price,freight_cost,suppliers(name),invoice_date").eq("status","On Credit").eq("is_voided",False).execute().data
            if credit_invs:
                inv_options = {f"{i.get('suppliers',{}).get('name','?')} — {fmt(i['purchase_price']+i['freight_cost'])} — {fmt_dt(i['invoice_date'])}": i for i in credit_invs}
                with st.form("mark_paid"):
                    sel = st.selectbox("Invoice", list(inv_options.keys()))
                    if st.form_submit_button("Mark as Paid", type="primary"):
                        inv = inv_options[sel]
                        old = dict(inv)
                        sb.table("purchase_invoices").update({"status":"Paid"}).eq("invoice_id",inv["invoice_id"]).execute()
                        audit("purchase_invoices", inv["invoice_id"], "UPDATE", old_data=old, new_data={"status":"Paid"}, changed_fields=["status"], reason="Manually marked as paid")
                        st.success("Invoice marked as paid."); st.rerun()
    else:
        st.success("No outstanding payables.")

# ── Expenses ─────────────────────────────────────────────────
with tab_exp:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<h3>Log Expense</h3>', unsafe_allow_html=True)
        with st.form("exp_form"):
            exp_desc = st.text_input("Description")
            c1, c2 = st.columns(2)
            exp_amt  = c1.number_input("Amount", min_value=0.0)
            exp_cat  = c2.selectbox("Category", ["Electricity","Transport","Rent","Salaries","Supplies","Other"])
            if st.form_submit_button("Log Expense", type="primary", use_container_width=True):
                if not exp_desc or not exp_amt:
                    st.error("Description and amount required.")
                else:
                    res = sb.table("expenses").insert({
                        "description": exp_desc, "amount": exp_amt,
                        "category": exp_cat, "created_by": current_uid()
                    }).execute().data[0]
                    audit("expenses", res["expense_id"], "INSERT", new_data=res, reason="Expense logged")
                    st.success("Logged!"); st.rerun()

    with col2:
        st.markdown('<h3>Recent Expenses</h3>', unsafe_allow_html=True)
        all_exp = sb.table("expenses").select("*").order("expense_date", desc=True).limit(30).execute().data
        for e in all_exp:
            voided = e.get("is_voided", False)
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"""
<div style="{'opacity:0.4;' if voided else ''}padding:6px 0;border-bottom:1px solid rgba(240,234,216,0.06)">
  <span style="font-size:13px;color:#f0ead8">{'~~' if voided else ''}{e['description']}{'~~' if voided else ''}</span>
  <span style="font-family:DM Mono,monospace;font-size:11px;color:#c8922a;margin-left:8px">{fmt(e['amount'])}</span>
  <span style="font-size:10px;color:#5a5247;margin-left:6px">{e.get('expense_date','')}</span>
</div>""", unsafe_allow_html=True)
            if not voided and can("delete_expense"):
                if c2.button("Void", key=f"vexp_{e['expense_id']}"):
                    old = dict(e)
                    sb.table("expenses").update({"is_voided": True}).eq("expense_id", e["expense_id"]).execute()
                    audit("expenses", e["expense_id"], "VOID", old_data=old, reason="Expense voided by admin")
                    st.rerun()

# ── Purchase Invoices ─────────────────────────────────────────
with tab_invoices:
    all_invs = sb.table("purchase_invoices").select("*,catalog(name),suppliers(name)").order("invoice_date", desc=True).limit(50).execute().data
    if all_invs:
        rows_html = ""
        for inv in all_invs:
            voided = inv.get("is_voided", False)
            item_name = inv["catalog"]["name"] if inv.get("catalog") else "—"
            sup_name  = inv["suppliers"]["name"] if inv.get("suppliers") else "—"
            style = "opacity:0.4" if voided else ""
            status_b = badge("VOIDED","danger") if voided else badge(inv["status"], "danger" if inv["status"]=="On Credit" else "success")
            rows_html += f"""
<tr style="{style}">
  <td style="font-size:11px;font-family:DM Mono,monospace;color:#5a5247">{fmt_dt(inv['invoice_date'])}</td>
  <td style="color:#f0ead8;font-size:13px">{item_name}</td>
  <td style="font-size:12px;color:#9a8f7a">{sup_name}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right">{inv['quantity']}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;color:#c8922a;text-align:right">{fmt(inv['landed_cost'])}</td>
  <td>{status_b}</td>
</tr>"""
        st.markdown(f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:8px;overflow:hidden">
  <div style="overflow-x:auto">
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="border-bottom:1px solid rgba(240,234,216,0.08)">
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247;text-align:left">Date</th>
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247;text-align:left">Item</th>
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247;text-align:left">Supplier</th>
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247;text-align:right">Qty</th>
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247;text-align:right">Landed Cost</th>
      <th style="padding:9px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Status</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("No purchase invoices yet.")
