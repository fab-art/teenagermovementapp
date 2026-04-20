import streamlit as st
from utils import get_db_connection, log_audit
from styles import apply_styles

st.set_page_config(page_title="Order Management", layout="wide")
apply_styles()

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the home page")
    st.stop()

st.title("📋 Order Management")

conn = get_db_connection()

# Tabs for order views
tab1, tab2 = st.tabs(["All Orders", "Order Details & Voiding"])

with tab1:
    st.subheader("Order History")
    
    if conn:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "pending", "completed", "cancelled", "voided"])
        with col2:
            date_from = st.date_input("From Date")
        with col3:
            date_to = st.date_input("To Date")
        
        # Fetch orders
        if status_filter == "All":
            orders = conn.execute("""
                SELECT * FROM orders 
                WHERE date(created_at) BETWEEN ? AND ?
                ORDER BY created_at DESC
            """, (date_from, date_to)).fetchall()
        else:
            orders = conn.execute("""
                SELECT * FROM orders 
                WHERE status = ? AND date(created_at) BETWEEN ? AND ?
                ORDER BY created_at DESC
            """, (status_filter, date_from, date_to)).fetchall()
        
        if orders:
            st.dataframe(orders, use_container_width=True)
            
            # Summary metrics
            total_orders = len(orders)
            total_revenue = sum(o['total_amount'] for o in orders if o['status'] == 'completed')
            pending_orders = len([o for o in orders if o['status'] == 'pending'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orders", total_orders)
            with col2:
                st.metric("Revenue", f"${total_revenue:.2f}")
            with col3:
                st.metric("Pending", pending_orders)
        else:
            st.info("No orders found")

with tab2:
    st.subheader("Order Details & Line Voiding")
    
    if conn:
        # Select order
        orders = conn.execute("SELECT id, order_number, customer_name, total_amount, status FROM orders").fetchall()
        order_options = {f"{o['order_number']} - {o['customer_name'] or 'Walk-in'}": o['id'] for o in orders}
        
        selected_order = st.selectbox("Select Order", list(order_options.keys()))
        
        if selected_order:
            order_id = order_options[selected_order]
            order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            
            # Order header
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Order #", order['order_number'])
            with col2:
                st.metric("Customer", order['customer_name'] or 'Walk-in')
            with col3:
                st.metric("Total", f"${order['total_amount']:.2f}")
            with col4:
                st.metric("Status", order['status'])
            
            # Order items
            st.markdown("### Order Items")
            items = conn.execute("""
                SELECT oi.*, p.name as product_name, p.sku
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            """, (order_id,)).fetchall()
            
            if items:
                items_df = st.dataframe(items, use_container_width=True)
                
                # Line voiding
                st.markdown("### Void Line Items")
                item_options = {f"{i['product_name']} (Qty: {i['quantity']}, ${i['subtotal']:.2f})": i['id'] for i in items}
                item_to_void = st.selectbox("Select Item to Void", list(item_options.keys()))
                void_reason = st.text_input("Void Reason")
                
                if st.button("Void Selected Line"):
                    if item_to_void and void_reason and order['status'] != 'cancelled':
                        item_id = item_options[item_to_void]
                        item = conn.execute("SELECT * FROM order_items WHERE id = ?", (item_id,)).fetchone()
                        
                        # Calculate new total
                        new_total = order['total_amount'] - item['subtotal']
                        
                        # Update order total
                        conn.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (new_total, order_id))
                        
                        # Restore inventory
                        conn.execute(
                            "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                            (item['quantity'], item['product_id'])
                        )
                        
                        # Delete or mark item as voided (simplified: delete)
                        conn.execute("DELETE FROM order_items WHERE id = ?", (item_id,))
                        
                        conn.commit()
                        
                        log_audit(
                            st.session_state.username,
                            "LINE_VOID",
                            f"Voided line item from order {order['order_number']}. Reason: {void_reason}"
                        )
                        
                        st.success("Line item voided successfully!")
                        st.rerun()
                
                # Full order void/cancel
                st.markdown("---")
                if order['status'] not in ['cancelled', 'voided']:
                    if st.button("⚠️ Cancel Entire Order", type="error"):
                        cancel_reason = st.text_input("Cancellation Reason")
                        if st.button("Confirm Cancellation"):
                            conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
                            
                            # Restore all inventory
                            for item in items:
                                conn.execute(
                                    "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                                    (item['quantity'], item['product_id'])
                                )
                            
                            conn.commit()
                            
                            log_audit(
                                st.session_state.username,
                                "ORDER_CANCEL",
                                f"Cancelled order {order['order_number']}. Reason: {cancel_reason}"
                            )
                            
                            st.success("Order cancelled!")
                            st.rerun()
            else:
                st.info("No items in this order")
