import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import inject, section_header, badge, metric_card
from utils import get_sb, require_auth, current_uid, audit, fmt, can

st.set_page_config(page_title="POS — Duka", page_icon="◈", layout="wide")
inject()
require_auth()

with st.sidebar:
    from utils import current_role, current_user, logout, ROLE_COLORS
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
section_header("Point of Sale", "Create new orders")

catalog = sb.table("catalog").select("item_id,name,uom,default_sell_price,current_landed_cost").eq("is_active", True).order("name").execute().data
if "cart" not in st.session_state:
    st.session_state.cart = []

col_left, col_right = st.columns([1, 1], gap="large")

# ── Left: item selector ───────────────────────────────────────
with col_left:
    st.markdown('<h3>Add Item</h3>', unsafe_allow_html=True)
    if not catalog:
        st.info("No items in catalog. Add stock from Inventory first.")
    else:
        cat_options = {f"{c['name']} ({c['uom']})": c for c in catalog}
        selected_label = st.selectbox("Product / Material", list(cat_options.keys()))
        item = cat_options[selected_label]
        c1, c2 = st.columns(2)
        with c1: qty = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.5)
        with c2: price = st.number_input("Unit Price", min_value=0.0, value=float(item["default_sell_price"]), step=0.5)

        if can("edit_prices"):
            st.markdown(f'<span style="font-size:11px;color:#5a5247">Landed cost: {fmt(item["current_landed_cost"])} · Margin: {fmt(price - item["current_landed_cost"])} ({((price/item["current_landed_cost"]-1)*100):.1f}% markup)</span>' if item["current_landed_cost"] else "", unsafe_allow_html=True)

        if st.button("➕ Add to Cart", use_container_width=True):
            existing = next((l for l in st.session_state.cart if l["item_id"] == item["item_id"] and l["unit_price"] == price), None)
            if existing:
                existing["quantity"] = round(existing["quantity"] + qty, 3)
            else:
                st.session_state.cart.append({
                    "item_id": item["item_id"], "name": item["name"], "uom": item["uom"],
                    "quantity": qty, "unit_price": price,
                    "landed_cost": item["current_landed_cost"]
                })
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<h3>Customer</h3>', unsafe_allow_html=True)
    cname  = st.text_input("Customer Name")
    cphone = st.text_input("Customer Phone")
    deposit = st.number_input("Upfront Deposit", min_value=0.0, value=0.0, step=100.0)
    notes  = st.text_area("Order Notes", height=70)

# ── Right: cart ───────────────────────────────────────────────
with col_right:
    st.markdown('<h3>Cart</h3>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown('<div style="text-align:center;padding:40px;color:#5a5247;border:1px solid rgba(240,234,216,0.08);border-radius:8px"><div style="font-family:Cormorant Garamond,serif;font-size:20px;color:#9a8f7a;margin-bottom:6px">Cart is empty</div>Add items from the left</div>', unsafe_allow_html=True)
    else:
        # Cart table HTML
        rows_html = ""
        total = 0.0
        for i, line in enumerate(st.session_state.cart):
            line_total = line["quantity"] * line["unit_price"]
            total += line_total
            rows_html += f"""
<tr>
  <td style="color:#f0ead8;font-size:13px">{line['name']}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right">{line['quantity']} {line['uom']}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;text-align:right">{fmt(line['unit_price'])}</td>
  <td style="font-family:DM Mono,monospace;font-size:12px;color:#c8922a;text-align:right">{fmt(line_total)}</td>
</tr>"""

        balance = total - deposit
        st.markdown(f"""
<div style="background:#1c1916;border:1px solid rgba(240,234,216,0.08);border-radius:8px;overflow:hidden">
  <table style="width:100%;border-collapse:collapse;font-size:13px">
    <thead><tr style="border-bottom:1px solid rgba(240,234,216,0.08)">
      <th style="text-align:left;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Item</th>
      <th style="text-align:right;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Qty</th>
      <th style="text-align:right;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Price</th>
      <th style="text-align:right;padding:10px 14px;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5a5247">Total</th>
    </tr></thead>
    <tbody style="border-collapse:collapse">
      {rows_html}
    </tbody>
    <tfoot><tr style="border-top:1px solid rgba(240,234,216,0.08)">
      <td colspan="3" style="padding:12px 14px;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Total</td>
      <td style="padding:12px 14px;font-family:Cormorant Garamond,serif;font-size:24px;font-weight:500;color:#c8922a;text-align:right">{fmt(total)}</td>
    </tr>
    <tr><td colspan="3" style="padding:4px 14px 12px;font-size:11px;color:#5a5247;font-family:DM Mono,monospace">Balance due</td>
    <td style="padding:4px 14px 12px;font-family:DM Mono,monospace;font-size:12px;color:#c0402a;text-align:right">{fmt(balance)}</td>
    </tr></tfoot>
  </table>
</div>""", unsafe_allow_html=True)

        st.markdown("")

        # Per-line removal
        st.markdown('<h3 style="margin-top:8px">Remove Items</h3>', unsafe_allow_html=True)
        for i, line in enumerate(st.session_state.cart):
            col_n, col_b = st.columns([4, 1])
            col_n.markdown(f'<span style="font-size:12px;color:#9a8f7a">{line["name"]} × {line["quantity"]}</span>', unsafe_allow_html=True)
            if col_b.button("×", key=f"rm_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑 Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
        with col_b:
            if st.button("✓ Place Order", type="primary", use_container_width=True):
                if not cname:
                    st.error("Customer name is required.")
                else:
                    with st.spinner("Processing order..."):
                        item_ids = [l["item_id"] for l in st.session_state.cart]
                        cat_res = sb.table("catalog").select("item_id,current_landed_cost").in_("item_id", item_ids).execute()
                        cost_map = {r["item_id"]: r["current_landed_cost"] for r in cat_res.data}
                        total = sum(l["quantity"] * l["unit_price"] for l in st.session_state.cart)

                        order_res = sb.table("sales_orders").insert({
                            "customer_name": cname, "customer_phone": cphone,
                            "total_amount": total, "deposit_paid": deposit,
                            "status": "Pending", "notes": notes,
                            "created_by": current_uid()
                        }).execute()
                        order = order_res.data[0]
                        oid = order["order_id"]

                        for line in st.session_state.cart:
                            cogs = (cost_map.get(line["item_id"], 0) or 0) * line["quantity"]
                            sb.table("order_lines").insert({
                                "order_id": oid, "item_id": line["item_id"],
                                "quantity": line["quantity"], "unit_price": line["unit_price"],
                                "line_cogs": cogs
                            }).execute()
                            sb.table("inventory_ledger").insert({
                                "item_id": line["item_id"], "transaction_type": "SALE",
                                "quantity_change": -line["quantity"],
                                "unit_cost": cost_map.get(line["item_id"], 0),
                                "reference_id": oid, "created_by": current_uid()
                            }).execute()

                        audit("sales_orders", oid, "INSERT", new_data=order, reason="New POS order")
                        st.success(f"✓ Order placed! Balance due: {fmt(total - deposit)}")
                        st.info(f"Order ID: `{oid}`")
                        st.session_state.cart = []
                        st.rerun()
