import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import inject, section_header, badge, metric_card
from utils import get_sb, require_auth, require_role, current_uid, audit, fmt, load_inventory, moving_avg_landed_cost, can, ROLE_COLORS

st.set_page_config(page_title="Inventory — Duka", page_icon="◫", layout="wide")
inject()
require_auth()

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

require_role(["admin", "manager"])
sb = get_sb()
section_header("Inventory", "Stock levels, inwarding & adjustments")

inv = load_inventory()
df = pd.DataFrame(inv) if inv else pd.DataFrame()

# ── KPI row ──────────────────────────────────────────────────
if not df.empty:
    low_count = int((df["stock"] < 5).sum())
    inv_val   = float((df["stock"] * df["current_landed_cost"]).sum())
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card("Total Items",       str(len(df))),                         unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Low Stock (<5)",    str(low_count), "danger" if low_count else "success"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Inventory Value",   f"{inv_val:,.0f}", "gold"),             unsafe_allow_html=True)
    with c4:
        total_stock = float(df["stock"].sum())
        st.markdown(metric_card("Total Units on Hand",   f"{total_stock:,.1f}"),                  unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab_stock, tab_receive, tab_adjust, tab_catalog = st.tabs(["Stock Levels", "Receive Stock", "Adjustments", "Catalog"])

# ── TAB 1: Stock Levels ───────────────────────────────────────
with tab_stock:
    search = st.text_input("Search items", placeholder="Type to filter...")
    if not df.empty:
        display = df if not search else df[df["name"].str.contains(search, case=False, na=False)]
        display = display.copy()
        display["stock_display"] = display["stock"].apply(lambda x: f"⚠ {x}" if x < 5 else str(x))
        st.dataframe(
            display.rename(columns={
                "name":"Item","type":"Type","uom":"UOM",
                "stock_display":"Stock","current_landed_cost":"Landed Cost","default_sell_price":"Sell Price"
            })[["Item","Type","UOM","Stock","Landed Cost","Sell Price"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No inventory yet. Receive stock below.")

# ── TAB 2: Receive Stock ──────────────────────────────────────
with tab_receive:
    suppliers = sb.table("suppliers").select("supplier_id,name").order("name").execute().data
    sup_map = {s["name"]: s["supplier_id"] for s in suppliers}

    with st.expander("➕ Add New Supplier"):
        with st.form("new_sup"):
            sn = st.text_input("Supplier Name")
            sp = st.text_input("Phone")
            if st.form_submit_button("Add Supplier"):
                if sn:
                    sb.table("suppliers").insert({"name":sn,"phone":sp}).execute()
                    audit("suppliers", "new", "INSERT", new_data={"name":sn}, reason="New supplier added")
                    st.success("Supplier added!"); st.rerun()

    st.markdown("")
    mode = st.radio("Item", ["Existing Item", "New Item"], horizontal=True)

    with st.form("receive_form"):
        if mode == "Existing Item" and not df.empty:
            item_name_sel = st.selectbox("Select Item", df["name"].tolist())
            item_row = df[df["name"] == item_name_sel].iloc[0]
            item_id = item_row["item_id"]
            item_name_new = item_type_new = item_uom_new = None
        else:
            item_id = None
            item_name_new = st.text_input("Item Name")
            c1, c2 = st.columns(2)
            item_type_new = c1.selectbox("Type", ["Material","Product","Service"])
            item_uom_new  = c2.selectbox("UOM",  ["Meters","Pieces","Flat Rate"])

        c1, c2 = st.columns(2)
        qty      = c1.number_input("Quantity Received", min_value=0.01, value=1.0, step=0.5)
        purchase = c2.number_input("Total Purchase Price", min_value=0.0, value=0.0)
        c1, c2 = st.columns(2)
        freight  = c1.number_input("Freight Cost", min_value=0.0, value=0.0)
        pay_stat = c2.selectbox("Payment", ["On Credit","Paid"])
        sup_name = st.selectbox("Supplier", list(sup_map.keys()) if sup_map else ["—"])

        lc = (purchase + freight) / qty if qty else 0
        st.markdown(f"""
<div style="background:rgba(200,146,42,0.1);border:1px solid rgba(200,146,42,0.25);border-radius:4px;padding:10px 14px;display:flex;justify-content:space-between">
  <span style="font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#5a5247">Landed Cost / Unit</span>
  <span style="font-family:DM Mono,monospace;font-size:13px;color:#c8922a">{fmt(lc)}</span>
</div>""", unsafe_allow_html=True)

        if st.form_submit_button("✓ Receive Stock", type="primary", use_container_width=True):
            with st.spinner("Saving..."):
                if not item_id:
                    if not item_name_new:
                        st.error("Item name required.")
                        st.stop()
                    res = sb.table("catalog").insert({
                        "name": item_name_new, "type": item_type_new, "uom": item_uom_new,
                        "current_landed_cost": round(lc,2), "default_sell_price": round(lc*1.3,2)
                    }).execute()
                    item_id = res.data[0]["item_id"]
                    audit("catalog", item_id, "INSERT", new_data=res.data[0], reason="New item created on inward")
                else:
                    old_cat = sb.table("catalog").select("current_landed_cost").eq("item_id", item_id).single().execute().data
                    new_avg = moving_avg_landed_cost(sb, item_id, qty, lc)
                    sb.table("catalog").update({"current_landed_cost": new_avg}).eq("item_id", item_id).execute()
                    audit("catalog", item_id, "UPDATE", old_data=old_cat, new_data={"current_landed_cost": new_avg}, changed_fields=["current_landed_cost"], reason="Landed cost updated on stock receive")

                led = sb.table("inventory_ledger").insert({
                    "item_id": item_id, "transaction_type": "INWARD",
                    "quantity_change": qty, "unit_cost": round(lc,2), "created_by": current_uid()
                }).execute().data[0]

                inv_data = {
                    "item_id": item_id, "quantity": qty,
                    "purchase_price": purchase, "freight_cost": freight, "status": pay_stat,
                    "created_by": current_uid()
                }
                if sup_map.get(sup_name):
                    inv_data["supplier_id"] = sup_map[sup_name]
                inv_res = sb.table("purchase_invoices").insert(inv_data).execute().data[0]

                audit("inventory_ledger", led["ledger_id"], "INSERT", new_data=led, reason="Stock received")
                st.success("Stock received successfully!"); st.rerun()

# ── TAB 3: Adjustments ───────────────────────────────────────
with tab_adjust:
    st.markdown("""
<div style="background:rgba(192,64,42,0.08);border:1px solid rgba(192,64,42,0.2);border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:12px;color:#c0402a">
  Adjustments are permanent entries in the audit trail. Every change is logged with reason and user.
</div>""", unsafe_allow_html=True)

    adj_tab1, adj_tab2 = st.tabs(["Inventory Adjustment", "Edit Item Prices"])

    with adj_tab1:
        require_role(["admin"])
        if df.empty:
            st.info("No items to adjust.")
        else:
            with st.form("adj_form"):
                adj_item = st.selectbox("Item", df["name"].tolist(), key="adj_item_sel")
                adj_row  = df[df["name"] == adj_item].iloc[0]
                st.markdown(f'<span style="font-size:12px;color:#9a8f7a">Current stock: <span style="color:#f0ead8;font-family:DM Mono,monospace">{adj_row["stock"]}</span> {adj_row["uom"]}</span>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                adj_type   = c1.selectbox("Adjustment Type", ["Physical Count Correction", "Damaged/Waste", "Manual Addition", "Opening Balance"])
                adj_change = c2.number_input("Quantity Change (+ add, - remove)", value=0.0, step=0.5)
                adj_reason = st.text_area("Reason (required)", placeholder="Explain why this adjustment is needed...")

                if st.form_submit_button("Apply Adjustment", type="primary"):
                    if not adj_reason:
                        st.error("Reason is required for all adjustments.")
                    elif adj_change == 0:
                        st.error("Quantity change cannot be zero.")
                    else:
                        led = sb.table("inventory_ledger").insert({
                            "item_id": adj_row["item_id"], "transaction_type": "ADJUSTMENT",
                            "quantity_change": adj_change,
                            "notes": f"{adj_type}: {adj_reason}",
                            "created_by": current_uid()
                        }).execute().data[0]
                        audit("inventory_ledger", led["ledger_id"], "ADJUST",
                              new_data={"item": adj_item, "change": adj_change, "type": adj_type},
                              reason=adj_reason)
                        st.success(f"Adjustment applied: {'+' if adj_change>0 else ''}{adj_change} {adj_row['uom']}"); st.rerun()

    with adj_tab2:
        if not can("edit_prices"):
            st.warning("Requires manager or admin role.")
        else:
            if not df.empty:
                with st.form("price_edit"):
                    pe_item = st.selectbox("Item", df["name"].tolist(), key="pe_item_sel")
                    pe_row  = df[df["name"] == pe_item].iloc[0]
                    c1, c2 = st.columns(2)
                    new_lc    = c1.number_input("New Landed Cost",  value=float(pe_row["current_landed_cost"]), min_value=0.0, step=0.01)
                    new_sell  = c2.number_input("New Sell Price",   value=float(pe_row["default_sell_price"]),  min_value=0.0, step=0.01)
                    pe_reason = st.text_input("Reason", placeholder="e.g. Supplier price increase")
                    if st.form_submit_button("Update Prices", type="primary"):
                        if not pe_reason:
                            st.error("Reason required.")
                        else:
                            old = {"current_landed_cost": pe_row["current_landed_cost"], "default_sell_price": pe_row["default_sell_price"]}
                            new = {"current_landed_cost": new_lc, "default_sell_price": new_sell}
                            sb.table("catalog").update(new).eq("item_id", pe_row["item_id"]).execute()
                            audit("catalog", pe_row["item_id"], "UPDATE", old_data=old, new_data=new, changed_fields=["current_landed_cost","default_sell_price"], reason=pe_reason)
                            st.success("Prices updated!"); st.rerun()

# ── TAB 4: Catalog management ─────────────────────────────────
with tab_catalog:
    st.markdown('<h3>Catalog Items</h3>', unsafe_allow_html=True)
    all_cat = sb.table("catalog").select("*").order("name").execute().data
    for item in all_cat:
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        active = item.get("is_active", True)
        c1.markdown(f'<span style="color:{("#f0ead8" if active else "#5a5247")};font-size:13px">{"" if active else "⊘ "}{item["name"]}</span> <span style="font-size:11px;color:#5a5247">{item["uom"]}</span>', unsafe_allow_html=True)
        c2.markdown(f'<span style="font-size:11px;font-family:DM Mono,monospace;color:#9a8f7a">LC: {fmt(item["current_landed_cost"])}</span>', unsafe_allow_html=True)
        c3.markdown(f'<span style="font-size:11px;font-family:DM Mono,monospace;color:#c8922a">SP: {fmt(item["default_sell_price"])}</span>', unsafe_allow_html=True)
        if can("adjust_inventory"):
            label = "Deactivate" if active else "Reactivate"
            if c4.button(label, key=f"tog_{item['item_id']}"):
                old = {"is_active": active}
                sb.table("catalog").update({"is_active": not active}).eq("item_id", item["item_id"]).execute()
                audit("catalog", item["item_id"], "UPDATE", old_data=old, new_data={"is_active": not active}, changed_fields=["is_active"], reason=f"Item {'deactivated' if active else 'reactivated'} by admin")
                st.rerun()
