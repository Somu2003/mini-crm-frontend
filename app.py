import streamlit as st
import requests
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import APIClient
from components.auth_component import AuthComponent

st.set_page_config(
    page_title="Mini CRM Platform", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize components
    api_client = APIClient()
    auth_component = AuthComponent()
    
    # Check authentication
    if not auth_component.is_authenticated():
        # Login page
        st.markdown('<div class="main-header">🎯 Mini CRM Platform</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Welcome to Mini CRM Platform")
            st.markdown("**Your comprehensive customer relationship management solution**")
            
            if st.button("🔐 Login to Continue", type="primary", use_container_width=True):
                auth_component.login()
                st.rerun()
        
        return
    
    # Authenticated user dashboard
    render_dashboard(api_client, auth_component)

def render_dashboard(api_client, auth_component):
    """Render the main dashboard for authenticated users"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎯 Mini CRM Platform")
        
        user_info = auth_component.get_user_info()
        st.markdown(f"**Welcome, {user_info.get('name', 'User')}!** 👋")
        
        if st.button("🚪 Logout", use_container_width=True):
            auth_component.logout()
            st.rerun()
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 📍 Navigation")
        
        if st.button("👥 Customers", use_container_width=True):
            st.switch_page("pages/2_👥_Customers.py")
        
        if st.button("🎯 Campaigns", use_container_width=True):
            st.switch_page("pages/3_🎯_Campaigns.py") 
        
        if st.button("📈 Analytics", use_container_width=True):
            st.switch_page("pages/4_📈_Analytics.py")
    
    # Main dashboard content
    st.markdown('<div class="main-header">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    
    # Check backend connection - IMPROVED CONNECTION TEST
    try:
        health_check = requests.get("http://localhost:8000/health", timeout=5)
        if health_check.status_code == 200:
            st.markdown('<div class="success-box">✅ System Status: All services operational</div>', unsafe_allow_html=True)
            backend_connected = True
        else:
            st.error("⚠️ Backend services may be experiencing issues")
            backend_connected = False
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Cannot connect to backend: {str(e)}")
        st.info("💡 **To fix:** Ensure backend server is running on http://localhost:8000")
        backend_connected = False
    
    if not backend_connected:
        st.markdown("### 🚀 Start Backend Server")
        st.code("cd backend\npython app.py", language="bash")
        return
    
    # Dashboard metrics - FIXED TO SHOW REAL DATA
    render_dashboard_metrics(api_client)
    
    # Recent activity
    render_recent_activity(api_client)
    
    # Quick actions
    render_quick_actions()

def render_dashboard_metrics(api_client):
    """Render the main dashboard metrics with REAL data"""
    
    st.markdown("### 📊 Key Performance Indicators")
    
    try:
        # Get real customer data from API
        customers_response = requests.get("http://localhost:8000/customers", timeout=5)
        campaigns_response = requests.get("http://localhost:8000/campaigns", timeout=5)
        
        if customers_response.status_code == 200:
            customers = customers_response.json()
        else:
            customers = []
        
        if campaigns_response.status_code == 200:
            campaigns = campaigns_response.json()
        else:
            campaigns = []
        
        # Calculate real metrics
        total_customers = len(customers)
        total_revenue = sum(c.get('total_spend', 0) for c in customers)
        total_orders = sum(c.get('total_orders', 0) for c in customers)
        total_campaigns = len(campaigns)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("👥 Total Customers", total_customers, col1, "#667eea"),
            ("💰 Total Revenue", f"₹{total_revenue:,.0f}", col2, "#28a745"),
            ("📦 Total Orders", total_orders, col3, "#17a2b8"),
            ("🎯 Active Campaigns", total_campaigns, col4, "#ffc107")
        ]
        
        for title, value, col, color in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: {color};">{title}</h3>
                    <h2 style="margin: 10px 0 0 0; color: #333;">{value}</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Additional insights
        if customers:
            avg_spend = total_revenue / len(customers) if customers else 0
            active_customers = len([c for c in customers if c.get('total_orders', 0) > 0])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Customer Value", f"₹{avg_spend:,.0f}")
            
            with col2:
                st.metric("Active Customers", f"{active_customers}/{len(customers)}")
            
            with col3:
                activation_rate = (active_customers / len(customers)) * 100 if customers else 0
                st.metric("Activation Rate", f"{activation_rate:.1f}%")
        
        # Debug info
        if st.checkbox("🔍 Show Debug Info"):
            st.write(f"**API Response Status:**")
            st.write(f"- Customers API: {customers_response.status_code}")
            st.write(f"- Campaigns API: {campaigns_response.status_code}")
            st.write(f"**Raw Data:**")
            st.write(f"- Customers count: {len(customers)}")
            st.write(f"- Campaigns count: {len(campaigns)}")
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to load dashboard data: {str(e)}")
        st.info("💡 Check that backend server is running and accessible")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

def render_recent_activity(api_client):
    """Render recent activity section"""
    
    st.markdown("---")
    st.markdown("### 📈 Recent Activity")
    
    tab1, tab2 = st.tabs(["📊 Recent Campaigns", "👥 New Customers"])
    
    with tab1:
        try:
            campaigns_response = requests.get("http://localhost:8000/campaigns", timeout=5)
            
            if campaigns_response.status_code == 200:
                campaigns = campaigns_response.json()
                
                if campaigns:
                    st.success(f"📊 {len(campaigns)} campaigns found")
                    
                    for campaign in campaigns[:3]:  # Show latest 3
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid #667eea; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h4 style="margin: 0 0 10px 0; color: #333;">
                                📋 {campaign.get('name', 'Untitled Campaign')}
                            </h4>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span><strong>Audience:</strong> {campaign.get('audience_size', 0)} customers</span>
                                <span><strong>Status:</strong> <span style="color: #28a745;">{campaign.get('status', 'active').title()}</span></span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("🎯 No campaigns yet! Create your first campaign to get started.")
            else:
                st.error("Failed to load campaigns")
                
        except Exception as e:
            st.warning(f"Could not load campaign data: {str(e)}")
    
    with tab2:
        try:
            customers_response = requests.get("http://localhost:8000/customers", timeout=5)
            
            if customers_response.status_code == 200:
                customers = customers_response.json()
                
                if customers:
                    recent_customers = customers[-5:] if len(customers) > 5 else customers
                    
                    st.success(f"👥 {len(customers)} total customers")
                    
                    for customer in reversed(recent_customers):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"👤 **{customer['name']}** - {customer['email']}")
                        
                        with col2:
                            st.write(f"₹{customer.get('total_spend', 0):,.0f}")
                        
                        with col3:
                            orders = customer.get('total_orders', 0)
                            st.write(f"📦 {orders} orders")
                else:
                    st.info("👥 No customers yet! Add your first customer to get started.")
            else:
                st.error("Failed to load customers")
                
        except Exception as e:
            st.warning(f"Could not load customer data: {str(e)}")

def render_quick_actions():
    """Render quick action buttons"""
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Customer", use_container_width=True, type="primary"):
            st.switch_page("pages/2_👥_Customers.py")
    
    with col2:
        if st.button("🎯 Create Campaign", use_container_width=True, type="secondary"):
            st.switch_page("pages/3_🎯_Campaigns.py")
    
    with col3:
        if st.button("👥 View All Customers", use_container_width=True, type="secondary"):
            st.switch_page("pages/2_👥_Customers.py")
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True, type="secondary"):
            st.switch_page("pages/4_📈_Analytics.py")

if __name__ == "__main__":
    main()
