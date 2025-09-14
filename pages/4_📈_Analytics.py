import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.api_client import APIClient
from components.auth_component import AuthComponent

st.set_page_config(page_title="Analytics - Mini CRM", page_icon="📈", layout="wide")

# Authentication check
auth_component = AuthComponent()
auth_component.require_auth()

# Initialize API client
api_client = APIClient()

# Page header
st.title("📈 Analytics & Insights")
st.markdown("Monitor your CRM performance and customer insights.")

try:
    # Get analytics data
    analytics_data = api_client.get_dashboard_stats()
    
    if analytics_data:
        overview = analytics_data.get("overview", {})
        
        # Key performance indicators
        st.markdown("## 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "👥 Total Customers",
                overview.get("total_customers", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "💰 Total Revenue",
                f"₹{overview.get('total_revenue', 0):,.0f}",
                delta=None
            )
        
        with col3:
            st.metric(
                "📦 Total Orders",
                overview.get("total_orders", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                "🎯 Active Campaigns",
                overview.get("total_campaigns", 0),
                delta=None
            )
        
        # Campaign performance
        if "campaign_performance" in analytics_data:
            st.markdown("## 📈 Campaign Performance")
            
            performance_data = analytics_data["campaign_performance"]
            
            if performance_data:
                for campaign in performance_data:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**{campaign['name']}**")
                    
                    with col2:
                        delivery_rate = campaign['delivery_rate']
                        if delivery_rate >= 90:
                            st.success(f"📈 {delivery_rate}% delivery rate")
                        elif delivery_rate >= 70:
                            st.warning(f"📊 {delivery_rate}% delivery rate")
                        else:
                            st.error(f"📉 {delivery_rate}% delivery rate")
                    
                    with col3:
                        st.info(f"📤 {campaign['total_sent']} messages sent")
            else:
                st.info("📊 No campaign performance data available yet.")
        
        # Recent campaigns
        if "recent_campaigns" in analytics_data:
            st.markdown("## 🎯 Recent Campaigns")
            
            recent_campaigns = analytics_data["recent_campaigns"]
            
            if recent_campaigns:
                for campaign in recent_campaigns:
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**📋 {campaign['name']}**")
                        
                        with col2:
                            status = campaign['status']
                            status_emoji = "🟢" if status == "active" else "✅"
                            st.write(f"{status_emoji} {status.title()}")
                        
                        with col3:
                            st.write(f"👥 {campaign['audience_size']} customers")
                        
                        st.markdown("---")
            else:
                st.info("🎯 No recent campaigns to display.")
        
        # Customer insights
        st.markdown("## 👥 Customer Insights")
        
        try:
            customers = api_client.get_customers()
            if customers:
                # Customer spend distribution
                high_spend = len([c for c in customers if c['total_spend'] > 50000])
                medium_spend = len([c for c in customers if 10000 < c['total_spend'] <= 50000])
                low_spend = len([c for c in customers if c['total_spend'] <= 10000])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💎 High Spenders", high_spend, help="Customers with >₹50,000 spend")
                
                with col2:
                    st.metric("⭐ Medium Spenders", medium_spend, help="Customers with ₹10,000-₹50,000 spend")
                
                with col3:
                    st.metric("👤 Low Spenders", low_spend, help="Customers with <₹10,000 spend")
                
                # Top customers
                st.markdown("### 🌟 Top Customers by Revenue")
                
                top_customers = sorted(customers, key=lambda x: x['total_spend'], reverse=True)[:5]
                
                for i, customer in enumerate(top_customers):
                    st.write(f"**{i+1}. {customer['name']}** - ₹{customer['total_spend']:,.0f} ({customer['total_orders']} orders)")
            
        except Exception as e:
            st.warning(f"Could not load customer insights: {str(e)}")
    
    else:
        st.warning("⚠️ Analytics data not available. Please ensure the backend is running.")

except Exception as e:
    st.error(f"Failed to load analytics: {str(e)}")
    st.info("💡 **Troubleshooting:** Make sure the backend server is running on http://localhost:8000")

# Refresh data
st.markdown("---")
if st.button("🔄 Refresh Analytics", use_container_width=True):
    st.rerun()

# Tips section
with st.expander("💡 Analytics Tips"):
    st.markdown("""
    **Getting the most from your analytics:**
    
    - 📊 Monitor delivery rates to optimize campaign performance
    - 👥 Focus on high-value customer segments for better ROI
    - 📈 Track customer lifecycle stages for targeted campaigns
    - 🎯 Use campaign insights to refine messaging strategies
    """)
