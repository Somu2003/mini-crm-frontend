import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="Mini CRM Platform",
    page_icon="🎯",
    layout="wide"
)

# Initialize API client
api_client = APIClient()

# Sidebar navigation
st.sidebar.title("🎯 Mini CRM Platform")
st.sidebar.markdown("Welcome, Demo User! 👋")

# Navigation menu
page = st.sidebar.selectbox("Navigate to:", [
    "🏠 Dashboard",
    "👥 Customers", 
    "🎯 Campaigns",
    "📊 Analytics"
])

# Page content based on selection
if page == "🏠 Dashboard":
    st.title("📊 Dashboard Overview")
    
    # Get dashboard stats
    try:
        stats = api_client.get_dashboard_stats()
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Total Customers", stats.get('total_customers', 0))
            with col2:
                st.metric("📦 Total Orders", stats.get('total_orders', 0))
            with col3:
                st.metric("🎯 Total Campaigns", stats.get('total_campaigns', 0))
            with col4:
                st.metric("💰 Total Revenue", f"₹{stats.get('total_revenue', 0):,.0f}")
        else:
            st.error("Could not load dashboard data")
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")

elif page == "👥 Customers":
    st.title("👥 Customer Management")
    
    # Customer management interface
    tab1, tab2 = st.tabs(["📋 All Customers", "➕ Add Customer"])
    
    with tab1:
        try:
            customers = api_client.get_customers()
            if customers:
                st.success(f"📊 Found {len(customers)} customers")
                for customer in customers:
                    with st.expander(f"👤 {customer['name']} - {customer['email']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Spend", f"₹{customer['total_spend']:,.0f}")
                        with col2:
                            st.metric("Total Orders", customer['total_orders'])
                        with col3:
                            st.metric("Status", "Active" if customer['is_active'] else "Inactive")
            else:
                st.info("No customers found.")
        except Exception as e:
            st.error(f"Error loading customers: {str(e)}")
    
    with tab2:
        st.subheader("➕ Add New Customer")
        with st.form("add_customer"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Customer Name *")
                email = st.text_input("Email Address *")
            with col2:
                phone = st.text_input("Phone Number")
            
            if st.form_submit_button("➕ Add Customer", type="primary"):
                if name and email:
                    customer_data = {"name": name, "email": email, "phone": phone}
                    result = api_client.create_customer(customer_data)
                    if result:
                        st.success("✅ Customer added successfully!")
                else:
                    st.error("❌ Name and email are required")

elif page == "🎯 Campaigns":
    st.title("🎯 Campaign Management")
    
    # Campaign interface
    tab1, tab2 = st.tabs(["📝 Create Campaign", "📊 All Campaigns"])
    
    with tab1:
        st.subheader("📝 Create New Campaign")
        with st.form("create_campaign"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Campaign Name *")
                audience_type = st.selectbox("Audience Type", [
                    "All Customers", "High Value Customers", 
                    "Inactive Customers", "New Customers"
                ])
            with col2:
                created_by = st.text_input("Created By", value="demo@example.com")
            
            message_template = st.text_area(
                "Message Template *", 
                value="Hi {name}, special offer for you! 🎉",
                help="Use {name} as placeholder for customer name"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🤖 Generate AI Messages", type="secondary"):
                    try:
                        ai_result = api_client.generate_ai_message("increase sales")
                        if ai_result and "messages" in ai_result:
                            st.success("✅ AI generated message options!")
                            for i, msg in enumerate(ai_result["messages"]):
                                st.code(msg, language="text")
                    except Exception as e:
                        st.error(f"AI generation failed: {str(e)}")
            
            with col2:
                if st.form_submit_button("🚀 Launch Campaign", type="primary"):
                    if name and message_template:
                        campaign_data = {
                            "name": name,
                            "message_template": message_template,
                            "audience_type": audience_type,
                            "created_by": created_by
                        }
                        result = api_client.create_campaign(campaign_data)
                        if result:
                            st.success("🚀 Campaign launched successfully!")
                    else:
                        st.error("❌ Name and message template are required")
    
    with tab2:
        st.subheader("📊 All Campaigns")
        try:
            campaigns = api_client.get_campaigns()
            if campaigns:
                for campaign in campaigns:
                    with st.expander(f"📋 {campaign['name']} - {campaign['status'].title()}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Audience Size", campaign['audience_size'])
                        with col2:
                            st.metric("Status", campaign['status'].title())
                        with col3:
                            st.metric("Created", campaign['created_at'][:10] if campaign['created_at'] else "Unknown")
                        st.code(campaign['message_template'])
            else:
                st.info("No campaigns found.")
        except Exception as e:
            st.error(f"Error loading campaigns: {str(e)}")

elif page == "📊 Analytics":
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
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("High Value Customers", seg_data['high_value_customers'])
                    st.metric("Recently Active", seg_data['recently_active'])
                with col2:
                    st.metric("Inactive Customers", seg_data['inactive_customers'])
                    st.metric("New Customers", seg_data['new_customers'])
        else:
            st.error("Could not load analytics data")
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** All changes are saved automatically to the database")
