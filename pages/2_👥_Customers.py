import streamlit as st
import requests
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.api_client import APIClient
from components.auth_component import AuthComponent

st.set_page_config(page_title="Customers - Mini CRM", page_icon="👥", layout="wide")

# Authentication check
auth_component = AuthComponent()
auth_component.require_auth()

# Initialize API client
api_client = APIClient()

# Page header
st.title("👥 Customer Management")
st.markdown("Complete customer lifecycle management - Create, Read, Update, Delete")

# Tabs for different customer views
tab1, tab2, tab3, tab4 = st.tabs(["📋 All Customers", "➕ Add Customer", "📦 Orders Management", "🗑️ Bulk Operations"])

with tab1:
    st.header("📋 Customer Directory")
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search customers", placeholder="Search by name or email...", key="main_customer_search")
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True, key="main_refresh_btn"):
            st.rerun()
    
    # Fetch and display customers
    try:
        customers = api_client.get_customers(search=search_query if search_query else None)
        
        if customers:
            st.success(f"📊 Found {len(customers)} customers")
            
            # Display customers - REMOVED key parameter from expander
            for customer_index, customer in enumerate(customers):
                customer_id = customer['id']
                customer_prefix = f"customer_{customer_id}_idx_{customer_index}"
                
                # Fixed: Removed key parameter from st.expander
                with st.expander(f"👤 {customer['name']} - {customer['email']}", expanded=False):
                    
                    # Customer metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Spend", f"₹{customer['total_spend']:,.0f}")
                    
                    with col2:
                        st.metric("Total Orders", customer['total_orders'])
                    
                    with col3:
                        last_order = customer.get('last_order_date')
                        if last_order:
                            st.metric("Last Order", last_order[:10])
                        else:
                            st.metric("Last Order", "Never")
                    
                    # Edit customer form with unique keys
                    st.markdown("### ✏️ Edit Customer Details")
                    
                    with st.form(key=f"edit_form_{customer_prefix}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Name *", value=customer['name'], key=f"edit_name_{customer_prefix}")
                            new_email = st.text_input("Email *", value=customer['email'], key=f"edit_email_{customer_prefix}")
                            new_phone = st.text_input("Phone", value=customer.get('phone', ''), key=f"edit_phone_{customer_prefix}")
                        
                        with col2:
                            st.markdown("**💰 Financial Data:**")
                            new_total_spend = st.number_input(
                                "Total Spend (₹)", 
                                value=float(customer['total_spend']), 
                                min_value=0.0, 
                                step=100.0,
                                key=f"edit_spend_{customer_prefix}"
                            )
                            new_total_orders = st.number_input(
                                "Total Orders", 
                                value=customer['total_orders'], 
                                min_value=0, 
                                step=1,
                                key=f"edit_total_orders_{customer_prefix}"
                            )
                        
                        # Submit button for form
                        submitted = st.form_submit_button("💾 Save All Changes", type="primary")
                        
                        if submitted:
                            if not new_name.strip():
                                st.error("❌ Customer name is required")
                            elif not new_email.strip():
                                st.error("❌ Email is required")
                            elif "@" not in new_email:
                                st.error("❌ Invalid email format")
                            else:
                                update_data = {
                                    "name": new_name.strip(),
                                    "email": new_email.strip(),
                                    "phone": new_phone.strip() if new_phone.strip() else None,
                                    "total_spend": new_total_spend,
                                    "total_orders": new_total_orders
                                }
                                
                                result = api_client.update_customer(customer_id, update_data)
                                if result:
                                    st.rerun()
                    
                    # Action buttons with unique keys
                    st.markdown("### 🔧 Quick Actions")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📦 View Orders", key=f"view_orders_btn_{customer_prefix}"):
                            st.session_state[f'show_orders_{customer_prefix}'] = True
                    
                    with col2:
                        if st.button(f"➕ Add Order", key=f"add_order_btn_{customer_prefix}"):
                            st.session_state[f'add_order_form_{customer_prefix}'] = True
                    
                    with col3:
                        if st.button(f"🎯 Campaign", key=f"campaign_btn_{customer_prefix}"):
                            st.info("💡 Navigate to Campaigns section to create targeted campaigns.")
                    
                    with col4:
                        if st.button(f"🗑️ Delete", key=f"delete_btn_{customer_prefix}", type="secondary"):
                            st.session_state[f'confirm_delete_{customer_prefix}'] = True
                    
                    # Show orders if requested
                    if st.session_state.get(f'show_orders_{customer_prefix}', False):
                        try:
                            orders = api_client.get_orders(customer_id=customer_id)
                            if orders:
                                st.write("**📦 Order History:**")
                                for order_idx, order in enumerate(orders):
                                    st.write(f"• Order #{order['id']}: ₹{order['order_value']:,.0f} on {order['order_date'][:10]} - {order.get('status', 'completed').title()}")
                            else:
                                st.info("No orders found for this customer.")
                            
                            if st.button("✖️ Close", key=f"close_orders_btn_{customer_prefix}"):
                                st.session_state[f'show_orders_{customer_prefix}'] = False
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed to load orders: {str(e)}")
                    
                    # Add order form
                    if st.session_state.get(f'add_order_form_{customer_prefix}', False):
                        with st.form(f"add_order_form_{customer_prefix}"):
                            st.markdown("### 📦 Add New Order")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                order_value = st.number_input(
                                    "Order Value (₹)", 
                                    min_value=0.01, 
                                    value=1000.0, 
                                    step=10.0, 
                                    key=f"new_order_value_{customer_prefix}"
                                )
                            
                            with col2:
                                product_category = st.selectbox(
                                    "Product Category",
                                    ["Electronics", "Fashion", "Books", "Home & Garden", "Sports", "Food & Beverages", "Other"],
                                    key=f"new_order_category_{customer_prefix}"
                                )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("📦 Add Order", type="primary"):
                                    order_data = {
                                        "customer_id": customer_id,
                                        "order_value": order_value,
                                        "product_category": product_category
                                    }
                                    
                                    result = api_client.create_order(order_data)
                                    if result:
                                        st.session_state[f'add_order_form_{customer_prefix}'] = False
                                        st.rerun()
                            
                            with col2:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state[f'add_order_form_{customer_prefix}'] = False
                                    st.rerun()
                    
                    # Delete confirmation
                    if st.session_state.get(f'confirm_delete_{customer_prefix}', False):
                        st.markdown("---")
                        st.error(f"⚠️ **Confirm Deletion of {customer['name']}**")
                        st.write("This will permanently delete the customer and all their orders. This action cannot be undone.")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(f"🗑️ Yes, Delete", key=f"confirm_delete_yes_{customer_prefix}", type="primary"):
                                result = api_client.delete_customer(customer_id)
                                if result:
                                    st.session_state[f'confirm_delete_{customer_prefix}'] = False
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"❌ Cancel", key=f"confirm_delete_no_{customer_prefix}"):
                                st.session_state[f'confirm_delete_{customer_prefix}'] = False
                                st.rerun()
        
        else:
            st.info("📄 No customers found. Add your first customer using the 'Add Customer' tab.")
    
    except Exception as e:
        st.error(f"Failed to load customers: {str(e)}")

with tab2:
    st.header("➕ Add New Customer")
    
    with st.form("add_customer_main_form"):
        st.markdown("Fill in the customer details below:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_customer_name = st.text_input("Customer Name *", placeholder="John Doe", key="add_new_customer_name")
            new_customer_email = st.text_input("Email Address *", placeholder="john@example.com", key="add_new_customer_email")
        
        with col2:
            new_customer_phone = st.text_input("Phone Number", placeholder="+91-9876543210", key="add_new_customer_phone")
        
        submitted = st.form_submit_button("➕ Add Customer", type="primary")
        
        if submitted:
            if not new_customer_name.strip():
                st.error("❌ Customer name is required")
            elif not new_customer_email.strip():
                st.error("❌ Email address is required")
            elif "@" not in new_customer_email:
                st.error("❌ Invalid email format")
            else:
                customer_data = {
                    "name": new_customer_name.strip(),
                    "email": new_customer_email.strip(),
                    "phone": new_customer_phone.strip() if new_customer_phone else None
                }
                
                result = api_client.create_customer(customer_data)
                if result:
                    st.balloons()

with tab3:
    st.header("📦 Orders Management")
    
    try:
        orders = api_client.get_orders()
        
        if orders:
            st.success(f"📦 Found {len(orders)} orders")
            
            for order_index, order in enumerate(orders):
                order_id = order['id']
                order_prefix = f"order_{order_id}_idx_{order_index}"
                
                # Fixed: Removed key parameter from st.expander
                with st.expander(f"📦 Order #{order_id} - ₹{order['order_value']:,.0f}", expanded=False):
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Order Value", f"₹{order['order_value']:,.0f}")
                    
                    with col2:
                        st.metric("Status", order['status'].title())
                    
                    with col3:
                        st.metric("Date", order['order_date'][:10])
                    
                    st.write(f"**Customer ID:** {order['customer_id']}")
                    st.write(f"**Category:** {order.get('product_category', 'N/A')}")
                    
                    with st.form(f"edit_order_form_{order_prefix}"):
                        st.markdown("### ✏️ Edit Order")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_order_value = st.number_input(
                                "Order Value (₹)", 
                                value=float(order['order_value']), 
                                min_value=0.01, 
                                step=10.0,
                                key=f"edit_order_value_{order_prefix}"
                            )
                            
                            new_status = st.selectbox(
                                "Status",
                                ["pending", "completed", "cancelled", "refunded"],
                                index=["pending", "completed", "cancelled", "refunded"].index(order['status']) if order['status'] in ["pending", "completed", "cancelled", "refunded"] else 1,
                                key=f"edit_order_status_{order_prefix}"
                            )
                        
                        with col2:
                            categories = ["Electronics", "Fashion", "Books", "Home & Garden", "Sports", "Food & Beverages", "Other"]
                            current_category = order.get('product_category', 'Other')
                            category_index = categories.index(current_category) if current_category in categories else 6
                            
                            new_category = st.selectbox(
                                "Product Category",
                                categories,
                                index=category_index,
                                key=f"edit_order_category_{order_prefix}"
                            )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                update_data = {
                                    "order_value": new_order_value,
                                    "status": new_status,
                                    "product_category": new_category
                                }
                                
                                result = api_client.update_order(order_id, update_data)
                                if result:
                                    st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete Order", type="secondary"):
                                st.session_state[f'delete_order_{order_prefix}'] = True
                    
                    if st.session_state.get(f'delete_order_{order_prefix}', False):
                        st.error("⚠️ **Confirm Order Deletion**")
                        st.write("This will permanently delete this order and update customer totals.")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(f"🗑️ Yes, Delete", key=f"delete_order_confirm_{order_prefix}", type="primary"):
                                result = api_client.delete_order(order_id)
                                if result:
                                    st.session_state[f'delete_order_{order_prefix}'] = False
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"❌ Cancel", key=f"delete_order_cancel_{order_prefix}"):
                                st.session_state[f'delete_order_{order_prefix}'] = False
                                st.rerun()
        
        else:
            st.info("📦 No orders found. Orders will appear here once customers place orders.")
    
    except Exception as e:
        st.error(f"Failed to load orders: {str(e)}")

with tab4:
    st.header("🗑️ Bulk Operations")
    st.warning("⚠️ **Caution:** Bulk operations permanently delete data and cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Data Summary")
        try:
            customers = api_client.get_customers()
            orders = api_client.get_orders()
            campaigns = api_client.get_campaigns()
            
            st.metric("Total Customers", len(customers))
            st.metric("Total Orders", len(orders))
            st.metric("Total Campaigns", len(campaigns))
            
        except:
            st.error("Could not load data summary")
    
    with col2:
        st.markdown("### 🧹 Cleanup Operations")
        
        st.info("🚧 **Coming Soon:**")
        st.write("• Bulk customer import/export")
        st.write("• Delete customers with zero orders")
        st.write("• Archive old campaigns")
        st.write("• Data backup and restore")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** All changes are saved immediately to the database. Use caution with delete operations as they cannot be undone.")
