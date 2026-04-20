import streamlit as st
from utils import get_db_connection, log_audit
from styles import apply_styles
from datetime import datetime

st.set_page_config(page_title="Finance", layout="wide")
apply_styles()

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the home page")
    st.stop()

st.title("💰 Finance Management")

conn = get_db_connection()

# Tabs for finance sections
tab1, tab2, tab3 = st.tabs(["P&L Statement", "Expenses", "Payables"])

with tab1:
    st.subheader("Profit & Loss Statement")
    
    if conn:
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().replace(day=1))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        # Calculate revenue (completed orders)
        revenue_result = conn.execute("""
            SELECT SUM(total_amount) as total 
            FROM orders 
            WHERE status = 'completed' 
            AND date(created_at) BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()
        total_revenue = revenue_result['total'] or 0
        
        # Calculate COGS (cost of goods sold from order items)
        cogs_result = conn.execute("""
            SELECT SUM(oi.quantity * p.cost) as total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'completed'
            AND date(o.created_at) BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()
        total_cogs = cogs_result['total'] or 0
        
        # Calculate gross profit
        gross_profit = total_revenue - total_cogs
        
        # Get expenses
        expenses_result = conn.execute("""
            SELECT SUM(amount) as total 
            FROM expenses 
            WHERE date(date) BETWEEN ? AND ?
        """, (start_date, end_date)).fetchone()
        total_expenses = expenses_result['total'] or 0
        
        # Net profit
        net_profit = gross_profit - total_expenses
        
        # Display P&L
        st.markdown("### Revenue")
        st.metric("Total Revenue", f"${total_revenue:.2f}")
        
        st.markdown("### Cost of Goods Sold")
        st.metric("COGS", f"${total_cogs:.2f}")
        
        st.markdown("### Gross Profit")
        st.metric("Gross Profit", f"${gross_profit:.2f}", delta=f"{(gross_profit/total_revenue*100) if total_revenue > 0 else 0:.1f}% Margin")
        
        st.markdown("### Operating Expenses")
        st.metric("Total Expenses", f"${total_expenses:.2f}")
        
        st.markdown("### Net Profit")
        st.metric("Net Profit", f"${net_profit:.2f}", delta="▲" if net_profit > 0 else "▼")
        
        # Visual breakdown
        st.markdown("---")
        st.markdown("### Financial Summary")
        
        if total_revenue > 0:
            data = {
                'Category': ['Revenue', 'COGS', 'Expenses', 'Net Profit'],
                'Amount': [total_revenue, -total_cogs, -total_expenses, net_profit]
            }
            st.bar_chart(data, x='Category', y='Amount')

with tab2:
    st.subheader("Expense Management")
    
    # Add new expense
    with st.expander("➕ Add New Expense"):
        col1, col2 = st.columns(2)
        with col1:
            expense_category = st.selectbox(
                "Category",
                ["Rent", "Utilities", "Salaries", "Supplies", "Marketing", "Insurance", "Other"]
            )
            expense_amount = st.number_input("Amount", min_value=0.0, step=0.01)
        with col2:
            expense_date = st.date_input("Date", value=datetime.now())
            expense_description = st.text_input("Description")
        
        if st.button("Record Expense"):
            if conn and expense_amount > 0:
                conn.execute(
                    "INSERT INTO expenses (category, description, amount, date) VALUES (?, ?, ?, ?)",
                    (expense_category, expense_description, expense_amount, expense_date)
                )
                conn.commit()
                
                log_audit(
                    st.session_state.username,
                    "EXPENSE_RECORD",
                    f"Recorded expense: ${expense_amount:.2f} - {expense_category}"
                )
                
                st.success("Expense recorded!")
                st.rerun()
    
    # Expense list
    st.markdown("### Expense History")
    expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    
    if expenses:
        st.dataframe(expenses, use_container_width=True)
        
        # Category breakdown
        st.markdown("### Expenses by Category")
        category_totals = {}
        for exp in expenses:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
        
        st.write(category_totals)
    else:
        st.info("No expenses recorded yet")

with tab3:
    st.subheader("Accounts Payable")
    
    st.info("Accounts Payable module - Track outstanding vendor bills and payments")
    
    # Mock AP tracking (could be expanded with an AP table)
    st.markdown("### Outstanding Payables")
    
    # Example payables (in production, this would come from a payables table)
    payables_data = {
        'Vendor': ['Supplier A', 'Supplier B', 'Utility Co'],
        'Invoice #': ['INV-001', 'INV-002', 'INV-003'],
        'Amount': [500.00, 750.00, 200.00],
        'Due Date': ['2024-02-01', '2024-02-15', '2024-02-10'],
        'Status': ['pending', 'pending', 'overdue']
    }
    
    st.dataframe(payables_data, use_container_width=True)
    
    total_payable = sum(payables_data['Amount'])
    st.metric("Total Payables", f"${total_payable:.2f}")
    
    if st.button("Record Payment"):
        st.info("Payment recording functionality - Would integrate with expense tracking")
