import streamlit as st
from utils import get_db_connection, log_audit
from styles import apply_styles

st.set_page_config(page_title="Inventory Management", layout="wide")
apply_styles()

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the home page")
    st.stop()

st.title("📦 Inventory Management")

# Tabs for different inventory functions
tab1, tab2, tab3 = st.tabs(["Product Catalog", "Stock Adjustments", "Add New Product"])

conn = get_db_connection()

with tab1:
    st.subheader("Product Catalog")
    
    if conn:
        products = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
        
        if products:
            # Search and filter
            col1, col2 = st.columns(2)
            with col1:
                search = st.text_input("Search Products")
            with col2:
                category_filter = st.selectbox("Category", ["All"] + list(set(p['category'] for p in products if p['category'])))
            
            # Display products
            st.dataframe(products, use_container_width=True)
            
            # Low stock warning
            low_stock = [p for p in products if p['quantity'] < 10]
            if low_stock:
                st.warning(f"⚠️ {len(low_stock)} products have low stock (< 10 units)")
        else:
            st.info("No products in catalog. Add your first product!")

with tab2:
    st.subheader("Stock Adjustments")
    
    if conn:
        products = conn.execute("SELECT id, sku, name, quantity FROM products").fetchall()
        product_options = {f"{p['sku']} - {p['name']}": p['id'] for p in products}
        
        selected_product = st.selectbox("Select Product", list(product_options.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            adjustment_type = st.radio("Adjustment Type", ["Add Stock", "Remove Stock", "Set Quantity"])
        with col2:
            quantity = st.number_input("Quantity", min_value=0, value=1)
        
        reason = st.text_area("Reason for Adjustment")
        
        if st.button("Apply Adjustment"):
            if selected_product and conn:
                product_id = product_options[selected_product]
                current_product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                
                if adjustment_type == "Add Stock":
                    new_qty = current_product['quantity'] + quantity
                elif adjustment_type == "Remove Stock":
                    new_qty = max(0, current_product['quantity'] - quantity)
                else:  # Set Quantity
                    new_qty = quantity
                
                conn.execute(
                    "UPDATE products SET quantity = ? WHERE id = ?",
                    (new_qty, product_id)
                )
                conn.commit()
                
                log_audit(
                    st.session_state.username, 
                    "INVENTORY_ADJUSTMENT",
                    f"Adjusted {current_product['name']}: {current_product['quantity']} → {new_qty}. Reason: {reason}"
                )
                
                st.success(f"Stock updated! New quantity: {new_qty}")
                st.rerun()

with tab3:
    st.subheader("Add New Product")
    
    col1, col2 = st.columns(2)
    with col1:
        sku = st.text_input("SKU *")
        name = st.text_input("Product Name *")
        category = st.text_input("Category")
    with col2:
        price = st.number_input("Selling Price *", min_value=0.0, step=0.01)
        cost = st.number_input("Cost *", min_value=0.0, step=0.01)
        quantity = st.number_input("Initial Quantity", min_value=0, value=0)
    
    description = st.text_area("Description")
    
    if st.button("Add Product"):
        if sku and name and price and cost and conn:
            try:
                conn.execute(
                    """INSERT INTO products (sku, name, description, price, cost, quantity, category) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (sku, name, description, price, cost, quantity, category)
                )
                conn.commit()
                
                log_audit(st.session_state.username, "PRODUCT_CREATE", f"Created product: {name} ({sku})")
                
                st.success("Product added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding product: {e}")
        else:
            st.warning("Please fill in all required fields (*)")
