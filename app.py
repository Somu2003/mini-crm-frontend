import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="Mini CRM Platform",
    page_icon="🎯",
    layout="wide"
)

# Initialize API client
api_client = APIClient()

# Simple authentication
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Mini CRM Login")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="demo@example.com")
            password = st.text_input("Password", type="password", placeholder="password")
            
            if st.form_submit_button("Login", type="primary"):
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("❌ Please enter email and password")
        
        st.info("💡 Demo: Use any email + any password")
        st.stop()

def main():
    check_auth()
    
    # Sidebar
    st.sidebar.title("🎯 Mini CRM Platform")
    st.sidebar.markdown(f"Welcome, **{st.session_state.get('user_email', 'Demo User')}**! 👋")
    
    # Navigation
    page = st.sidebar.selectbox("Navigate to:", [
        "🏠 Dashboard",
        "👥 Customers", 
        "🎯 Campaigns",
        "📊 Analytics"
    ])
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    # Main content
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Customers":
        show_customers()
    elif page == "🎯 Campaigns":
        show_campaigns()
    elif page == "📊 Analytics":
        show_analytics()

def show_dashboard():
    st.title("📊 Dashboard Overview")
    
    try:
        # Get dashboard data
        stats = api_client.get_dashboard_stats()
        
        if stats:
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="👥 Total Customers",
                    value=stats.get('total_customers', 0),
                    delta=f"+{min(5, stats.get('total_customers', 0))} New"
                )
            
            with col2:
                st.metric(
                    label="📦 Total Orders", 
                    value=stats.get('total_orders', 0),
                    delta="📈 Growing"
                )
            
            with col3:
                st.metric(
                    label="🎯 Active Campaigns",
                    value=stats.get('active_campaigns', 0),
                    delta=f"of {stats.get('total_campaigns', 0)} total"
                )
            
            with col4:
                revenue = stats.get('total_revenue', 0)
                st.metric(
                    label="💰 Total Revenue",
                    value=f"₹{revenue:,.0f}",
                    delta="💎 Premium"
                )
            
            st.markdown("---")
            
            # Recent activity
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 Recent Customers")
                customers = api_client.get_customers()
                if customers:
                    recent_customers = customers[:5]
                    for customer in recent_customers:
                        st.write(f"• **{customer['name']}** - {customer['email']}")
                        st.write(f"  💰 ₹{customer.get('total_spend', 0):,.0f} spent, {customer.get('total_orders', 0)} orders")
                else:
                    st.info("No customers yet.")
            
            with col2:
                st.subheader("🎯 Recent Campaigns")
                campaigns = api_client.get_campaigns()
                if campaigns:
                    recent_campaigns = campaigns[:5]
                    for campaign in recent_campaigns:
                        status_emoji = "🟢" if campaign.get('status') == 'active' else "⏸️" if campaign.get('status') == 'paused' else "✅"
                        st.write(f"• **{campaign['name']}** {status_emoji}")
                        st.write(f"  👥 {campaign.get('audience_size', 0)} audience • {campaign.get('status', 'unknown').title()}")
                else:
                    st.info("No campaigns yet.")
        
        else:
            st.error("❌ Failed to load dashboard data")
    
    except Exception as e:
        st.error(f"❌ Dashboard error: {str(e)}")

def show_customers():
    st.title("👥 Customer Management")
    
    tab1, tab2 = st.tabs(["📋 All Customers", "➕ Add Customer"])
    
    with tab1:
        # Search
        search = st.text_input("🔍 Search customers", placeholder="Search by name or email...")
        
        try:
            customers = api_client.get_customers(search if search else None)
            
            if customers:
                st.success(f"📊 Found {len(customers)} customers")
                
                for idx, customer in enumerate(customers):
                    customer_id = customer['id']
                    unique_key = f"customer_{customer_id}_{idx}"
                    
                    with st.expander(f"👤 {customer['name']} - {customer['email']}"):
                        # Metrics
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
                        
                        # Edit form
                        with st.form(f"edit_customer_{unique_key}"):
                            st.markdown("### ✏️ Edit Customer")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Name", value=customer['name'], key=f"name_{unique_key}")
                                new_email = st.text_input("Email", value=customer['email'], key=f"email_{unique_key}")
                            with col2:
                                new_phone = st.text_input("Phone", value=customer.get('phone', '') or '', key=f"phone_{unique_key}")
                                new_spend = st.number_input("Total Spend", value=float(customer['total_spend']), min_value=0.0, key=f"spend_{unique_key}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                    if new_name and new_email:
                                        update_data = {
                                            "name": new_name,
                                            "email": new_email,
                                            "phone": new_phone,
                                            "total_spend": new_spend,
                                            "total_orders": customer['total_orders']
                                        }
                                        result = api_client.update_customer(customer_id, update_data)
                                        if result:
                                            st.success("✅ Customer updated!")
                                            st.rerun()
                                    else:
                                        st.error("❌ Name and email required")
                            
                            with col2:
                                if st.form_submit_button("🗑️ Delete", type="secondary"):
                                    result = api_client.delete_customer(customer_id)
                                    if result:
                                        st.success("🗑️ Customer deleted!")
                                        st.rerun()
                        
                        # Add order
                        if st.button(f"➕ Add Order", key=f"add_order_{unique_key}"):
                            st.session_state[f'show_order_form_{customer_id}'] = True
                        
                        if st.session_state.get(f'show_order_form_{customer_id}', False):
                            with st.form(f"add_order_{unique_key}"):
                                st.markdown("### 📦 Add New Order")
                                col1, col2 = st.columns(2)
                                with col1:
                                    order_value = st.number_input("Order Value (₹)", min_value=0.01, value=1000.0, key=f"order_val_{unique_key}")
                                with col2:
                                    category = st.selectbox("Category", ["Electronics", "Fashion", "Books", "Home & Garden", "Sports", "Other"], key=f"cat_{unique_key}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("📦 Add Order", type="primary"):
                                        order_data = {
                                            "customer_id": customer_id,
                                            "order_value": order_value,
                                            "product_category": category
                                        }
                                        result = api_client.create_order(order_data)
                                        if result:
                                            st.success("✅ Order added!")
                                            st.session_state[f'show_order_form_{customer_id}'] = False
                                            st.rerun()
                                with col2:
                                    if st.form_submit_button("❌ Cancel"):
                                        st.session_state[f'show_order_form_{customer_id}'] = False
                                        st.rerun()
            else:
                st.info("📄 No customers found.")
        
        except Exception as e:
            st.error(f"❌ Error loading customers: {str(e)}")
    
    with tab2:
        st.subheader("➕ Add New Customer")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Customer Name *", placeholder="John Doe")
                email = st.text_input("Email Address *", placeholder="john@example.com")
            with col2:
                phone = st.text_input("Phone Number", placeholder="+91-9876543210")
            
            if st.form_submit_button("➕ Add Customer", type="primary"):
                if name and email:
                    customer_data = {
                        "name": name,
                        "email": email,
                        "phone": phone
                    }
                    result = api_client.create_customer(customer_data)
                    if result:
                        st.success("✅ Customer added successfully!")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ Name and email are required")

def show_campaigns():
    st.title("🎯 Campaign Management")
    
    tab1, tab2 = st.tabs(["📝 Create Campaign", "📊 All Campaigns"])
    
    with tab1:
        st.subheader("📝 Create New Campaign")
        
        with st.form("create_campaign_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Campaign Name *", placeholder="Black Friday Sale")
                audience_type = st.selectbox("Audience Type", [
                    "All Customers", "High Value Customers", 
                    "Inactive Customers", "New Customers"
                ])
            with col2:
                created_by = st.text_input("Created By", value=st.session_state.get('user_email', 'demo@example.com'))
            
            message_template = st.text_area(
                "Message Template *", 
                value="Hi {name}, special offer just for you! 🎉",
                help="Use {name} as placeholder for customer name"
            )
            
            char_count = len(message_template)
            if char_count > 160:
                st.warning(f"⚠️ Message is {char_count} characters (recommended: under 160 for SMS)")
            else:
                st.info(f"✅ Message length: {char_count} characters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("🤖 Generate AI Messages", type="secondary"):
                    try:
                        ai_result = api_client.generate_ai_message("increase sales")
                        if ai_result and "messages" in ai_result:
                            st.session_state.ai_messages = ai_result["messages"]
                            st.success("✅ AI generated message options!")
                    except Exception as e:
                        st.error(f"❌ AI generation failed: {str(e)}")
            
            with col2:
                if st.form_submit_button("🚀 Launch Campaign", type="primary"):
                    if name and message_template:
                        if "{name}" not in message_template:
                            st.error("❌ Message must include {name} placeholder")
                        else:
                            campaign_data = {
                                "name": name,
                                "message_template": message_template,
                                "audience_type": audience_type,
                                "created_by": created_by
                            }
                            result = api_client.create_campaign(campaign_data)
                            if result:
                                st.success("🚀 Campaign launched successfully!")
                                st.balloons()
                                if 'ai_messages' in st.session_state:
                                    del st.session_state.ai_messages
                                st.rerun()
                    else:
                        st.error("❌ Campaign name and message template are required")
        
        # Show AI messages if generated
        if 'ai_messages' in st.session_state:
            st.markdown("---")
            st.markdown("### 🤖 AI Generated Messages")
            st.info("💡 Copy any message you like and paste it into the message template above")
            
            for i, message in enumerate(st.session_state.ai_messages):
                st.code(message, language="text")
            
            if st.button("🗑️ Clear AI Messages"):
                del st.session_state.ai_messages
                st.rerun()
    
    with tab2:
        st.subheader("📊 Campaign Management")
        
        try:
            campaigns = api_client.get_campaigns()
            
            if campaigns:
                st.success(f"📊 Found {len(campaigns)} campaigns")
                
                for idx, campaign in enumerate(campaigns):
                    campaign_id = campaign['id']
                    campaign_key = f"campaign_{campaign_id}_{idx}"
                    
                    with st.expander(f"📋 {campaign['name']} - {campaign['status'].title()}"):
                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Audience Size", campaign.get('audience_size', 0))
                        with col2:
                            status = campaign['status'].title()
                            status_emoji = "🟢" if status == "Active" else "⏸️" if status == "Paused" else "✅"
                            st.metric("Status", f"{status} {status_emoji}")
                        with col3:
                            created_date = campaign.get('created_at', 'Unknown')[:10] if campaign.get('created_at') else 'Unknown'
                            st.metric("Created", created_date)
                        
                        # Campaign details
                        st.write(f"**Audience Type:** {campaign.get('audience_type', 'All Customers')}")
                        st.write(f"**Created By:** {campaign.get('created_by', 'Unknown')}")
                        st.markdown("**📱 Message Template:**")
                        st.code(campaign['message_template'])
                        
                        # Actions
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button("📊 View Stats", key=f"stats_{campaign_key}"):
                                try:
                                    stats = api_client.get_campaign_stats(campaign_id)
                                    if stats:
                                        st.write("**📈 Campaign Statistics:**")
                                        st.write(f"• Total Sent: {stats['total_sent']}")
                                        st.write(f"• Delivered: {stats['delivered']}")
                                        st.write(f"• Failed: {stats['failed']}")
                                        st.write(f"• Delivery Rate: {stats['delivery_rate']:.1f}%")
                                        if 'open_rate' in stats:
                                            st.write(f"• Open Rate: {stats['open_rate']:.1f}%")
                                        if 'click_rate' in stats:
                                            st.write(f"• Click Rate: {stats['click_rate']:.1f}%")
                                except Exception as e:
                                    st.error(f"❌ Error loading stats: {str(e)}")
                        
                        with col2:
                            if campaign['status'] == 'active':
                                if st.button("⏸️ Pause", key=f"pause_{campaign_key}"):
                                    update_data = {
                                        "name": campaign['name'],
                                        "message_template": campaign['message_template'],
                                        "audience_type": campaign.get('audience_type'),
                                        "status": "paused"
                                    }
                                    result = api_client.update_campaign(campaign_id, update_data)
                                    if result:
                                        st.success("⏸️ Campaign paused!")
                                        st.rerun()
                            elif campaign['status'] == 'paused':
                                if st.button("▶️ Resume", key=f"resume_{campaign_key}"):
                                    update_data = {
                                        "name": campaign['name'],
                                        "message_template": campaign['message_template'],
                                        "audience_type": campaign.get('audience_type'),
                                        "status": "active"
                                    }
                                    result = api_client.update_campaign(campaign_id, update_data)
                                    if result:
                                        st.success("▶️ Campaign resumed!")
                                        st.rerun()
                        
                        with col3:
                            if st.button("📤 Export", key=f"export_{campaign_key}"):
                                export_data = f"""Campaign Export
Name: {campaign['name']}
Status: {campaign['status']}
Audience Type: {campaign.get('audience_type', 'All')}
Audience Size: {campaign.get('audience_size', 0)}
Created: {created_date}

Message Template:
{campaign['message_template']}
"""
                                st.download_button(
                                    label="💾 Download",
                                    data=export_data,
                                    file_name=f"{campaign['name']}_campaign.txt",
                                    mime="text/plain",
                                    key=f"download_{campaign_key}"
                                )
                        
                        with col4:
                            if st.button("🗑️ Delete", key=f"delete_{campaign_key}", type="secondary"):
                                result = api_client.delete_campaign(campaign_id)
                                if result:
                                    st.success("🗑️ Campaign deleted!")
                                    st.rerun()
            else:
                st.info("📄 No campaigns found.")
        
        except Exception as e:
            st.error(f"❌ Error loading campaigns: {str(e)}")

def show_analytics():
    st.title("📊 Analytics & Insights")
    
    try:
        stats = api_client.get_dashboard_stats()
        segments = api_client.get_customer_segments()
        
        if stats:
            # KPIs
            st.subheader("📈 Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue", f"₹{stats['total_revenue']:,.0f}")
            with col2:
                st.metric("Total Customers", stats['total_customers'])
            with col3:
                st.metric("Avg Customer Value", f"₹{stats['avg_spend']:,.0f}")
            with col4:
                st.metric("Total Orders", stats['total_orders'])
            
            # Customer segments
            if segments and 'segments' in segments:
                st.subheader("🎯 Customer Segmentation")
                seg_data = segments['segments']
                
                # Create pie chart
                segment_df = pd.DataFrame([
                    {'Segment': 'High Value', 'Count': seg_data['high_value_customers']},
                    {'Segment': 'Recently Active', 'Count': seg_data['recently_active']},
                    {'Segment': 'Inactive', 'Count': seg_data['inactive_customers']},
                    {'Segment': 'New Customers', 'Count': seg_data['new_customers']}
                ])
                
                if segment_df['Count'].sum() > 0:
                    fig = px.pie(segment_df, values='Count', names='Segment', title="Customer Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("High Value Customers", seg_data['high_value_customers'])
                    st.metric("Recently Active", seg_data['recently_active'])
                with col2:
                    st.metric("Inactive Customers", seg_data['inactive_customers'])
                    st.metric("New Customers", seg_data['new_customers'])
            
            # Insights
            st.subheader("💡 Business Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Recommendations")
                if segments and 'segments' in segments:
                    seg = segments['segments']
                    if seg['inactive_customers'] > 0:
                        st.write(f"• Re-engage {seg['inactive_customers']} inactive customers with targeted campaigns")
                    if seg['high_value_customers'] > 0:
                        st.write(f"• Focus on {seg['high_value_customers']} high-value customers for premium offerings")
                    if seg['new_customers'] > 0:
                        st.write(f"• Nurture {seg['new_customers']} new customers with onboarding campaigns")
            
            with col2:
                st.markdown("### 📊 Performance")
                if stats['total_customers'] > 0:
                    conversion_rate = (stats['total_orders'] / stats['total_customers']) * 100
                    st.write(f"• Average orders per customer: {conversion_rate:.1f}%")
                    st.write(f"• Revenue per customer: ₹{stats['avg_spend']:,.0f}")
                    if stats['active_campaigns'] > 0:
                        st.write(f"• {stats['active_campaigns']} active campaigns driving engagement")
        
        else:
            st.error("❌ Could not load analytics data")
    
    except Exception as e:
        st.error(f"❌ Analytics error: {str(e)}")

if __name__ == "__main__":
    main()
