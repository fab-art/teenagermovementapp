import streamlit as st
from utils import get_db_connection, log_audit
from styles import apply_styles

st.set_page_config(page_title="POS - Point of Sale", layout="wide")
apply_styles()

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the home page")
    st.stop()

st.title("🛒 Point of Sale")

# Initialize cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Product selection
st.subheader("Products")
conn = get_db_connection()
if conn:
    products = conn.execute("SELECT * FROM products").fetchall()
    
    if products:
        # Display products in grid
        cols = st.columns(3)
        for idx, product in enumerate(products):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{product['name']}</h4>
                        <p>SKU: {product['sku']}</p>
                        <p><strong>${product['price']:.2f}</strong></p>
                        <p>Stock: {product['quantity']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    qty = st.number_input(
                        "Qty", 
                        min_value=1, 
                        max_value=product['quantity'],
                        value=1,
                        key=f"qty_{product['id']}"
                    )
                    
                    if st.button("Add to Cart", key=f"add_{product['id']}"):
                        st.session_state.cart.append({
                            'id': product['id'],
                            'name': product['name'],
                            'price': product['price'],
                            'quantity': qty,
                            'subtotal': product['price'] * qty
                        })
                        st.success(f"Added {product['name']} to cart")
    else:
        st.info("No products available. Add products in Inventory.")

# Shopping Cart
st.subheader("🛍️ Shopping Cart")
if st.session_state.cart:
    cart_df = st.dataframe(st.session_state.cart, use_container_width=True)
    
    total = sum(item['subtotal'] for item in st.session_state.cart)
    st.metric("Cart Total", f"${total:.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
    with col2:
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "Credit"])
    
    if st.button("Complete Sale", type="primary"):
        if conn:
            try:
                # Create order
                order_number = f"ORD-{st.time.time()}"
                conn.execute(
                    "INSERT INTO orders (order_number, customer_name, total_amount, status) VALUES (?, ?, ?, ?)",
                    (order_number, customer_name, total, "completed")
                )
                order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                
                # Add order items and update inventory
                for item in st.session_state.cart:
                    conn.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (order_id, item['id'], item['quantity'], item['price'], item['subtotal'])
                    )
                    conn.execute(
                        "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                        (item['quantity'], item['id'])
                    )
                
                conn.commit()
                
                # Log audit
                log_audit(st.session_state.username, "SALE", f"Order {order_number} completed - ${total:.2f}")
                
                st.success("Sale completed successfully!")
                st.session_state.cart = []
                st.rerun()
            except Exception as e:
                st.error(f"Error processing sale: {e}")
                conn.rollback()
    
    if st.button("Clear Cart"):
        st.session_state.cart = []
        st.rerun()
else:
    st.info("Cart is empty")
