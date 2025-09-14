import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.api_client import APIClient
from components.auth_component import AuthComponent

st.set_page_config(page_title="Campaigns - Mini CRM", page_icon="🎯", layout="wide")

# Authentication check
auth_component = AuthComponent()
auth_component.require_auth()

# Initialize API client
api_client = APIClient()

# Page header
st.title("🎯 Campaign Management")
st.markdown("Complete campaign lifecycle management - Create, Edit, Delete, Monitor")

# Tabs for campaign management
tab1, tab2 = st.tabs(["📝 Create Campaign", "📊 Campaign Management"])

with tab1:
    st.header("📝 Create New Campaign")
    
    # Campaign creation form
    with st.form("campaign_form", clear_on_submit=True):
        # Campaign basic details
        st.markdown("### 📋 Campaign Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name *", placeholder="e.g., Black Friday Sale")
        
        with col2:
            campaign_objective = st.text_input("Campaign Objective", placeholder="e.g., Bring back inactive customers")
        
        st.markdown("### 🎯 Target Audience")
        
        # Audience targeting
        audience_type = st.selectbox(
            "Select Audience Type:",
            ["All Customers", "High Value Customers", "Inactive Customers", "New Customers"]
        )
        
        st.markdown("### 📱 Campaign Message")
        
        # Message template input
        message_template = st.text_area(
            "Message Template *",
            value="Hi {name}, special offer just for you! 🎉",
            height=100,
            help="Use {name} as placeholder for customer name"
        )
        
        # Character counter
        char_count = len(message_template)
        if char_count > 160:
            st.warning(f"⚠️ Message is {char_count} characters (recommended: under 160 for SMS)")
        else:
            st.info(f"✅ Message length: {char_count} characters")
        
        # Form submit buttons
        col1, col2 = st.columns(2)
        
        with col1:
            generate_ai_btn = st.form_submit_button("🤖 Generate AI Messages", type="secondary")
        
        with col2:
            launch_campaign_btn = st.form_submit_button("🚀 Launch Campaign", type="primary")
        
        # Handle AI message generation
        if generate_ai_btn and campaign_objective:
            with st.spinner("🤖 Generating AI messages..."):
                ai_result = api_client.generate_ai_message(campaign_objective)
                if ai_result and "messages" in ai_result:
                    st.session_state.ai_messages = ai_result["messages"]
                    st.success("✅ AI generated message options!")
                    st.rerun()
        
        # Handle campaign launch
        if launch_campaign_btn:
            # Validation
            if not campaign_name.strip():
                st.error("❌ Campaign name is required")
            elif not message_template.strip():
                st.error("❌ Message template is required")
            elif "{name}" not in message_template:
                st.error("❌ Message must include {name} placeholder")
            else:
                # Create campaign
                campaign_data = {
                    "name": campaign_name.strip(),
                    "message_template": message_template.strip(),
                    "audience_type": audience_type,
                    "created_by": auth_component.get_user_email()
                }
                
                with st.spinner("🚀 Launching campaign..."):
                    result = api_client.create_campaign(campaign_data)
                    if result:
                        st.balloons()
                        if "ai_messages" in st.session_state:
                            del st.session_state.ai_messages
                        st.success("🎉 Campaign launched successfully!")
    
    # Display AI messages outside the form
    if "ai_messages" in st.session_state:
        st.markdown("---")
        st.markdown("### 🤖 AI Generated Messages")
        st.info("💡 Copy any message you like and paste it into the message template above")
        
        for i, message in enumerate(st.session_state.ai_messages):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.code(message, language="text")
            
            with col2:
                if st.button("📋 Copy", key=f"copy_ai_msg_{i}"):
                    st.session_state[f"copied_message_{i}"] = message
                    st.success("✅ Copied!")
        
        if st.button("🗑️ Clear AI Messages"):
            del st.session_state.ai_messages
            st.rerun()

with tab2:
    st.header("📊 Campaign Management")
    
    # Auto-refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_campaigns"):
            st.rerun()
    
    try:
        campaigns = api_client.get_campaigns()
        
        if campaigns:
            st.success(f"📊 Found {len(campaigns)} campaigns")
            
            # Sort campaigns by creation date (newest first)
            campaigns.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            for campaign_index, campaign in enumerate(campaigns):
                campaign_id = campaign['id']
                campaign_prefix = f"campaign_{campaign_id}_idx_{campaign_index}"
                
                # Fixed: No key parameter for expander
                with st.expander(f"📋 {campaign['name']} - {campaign['status'].title()}", expanded=False):
                    
                    # Campaign metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Audience Size", campaign.get('audience_size', 0))
                    
                    with col2:
                        status = campaign['status'].title()
                        status_emoji = "🟢" if status == "Active" else "✅"
                        st.metric("Status", f"{status} {status_emoji}")
                    
                    with col3:
                        created_date = campaign.get('created_at', 'Unknown')[:10]
                        st.metric("Created", created_date)
                    
                    # Campaign details (read-only)
                    st.markdown("**🎯 Current Details:**")
                    st.write(f"**Audience Type:** {campaign.get('audience_type', 'All Customers')}")
                    st.write(f"**Created By:** {campaign.get('created_by', 'Unknown')}")
                    st.markdown("**📱 Message Template:**")
                    st.code(campaign['message_template'])
                    
                    # Edit campaign form
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Campaign")
                    
                    with st.form(f"edit_campaign_form_{campaign_prefix}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_name = st.text_input("Campaign Name", value=campaign['name'], key=f"edit_name_{campaign_prefix}")
                            audience_options = ["All Customers", "High Value Customers", "Inactive Customers", "New Customers"]
                            current_audience = campaign.get('audience_type', 'All Customers')
                            audience_index = audience_options.index(current_audience) if current_audience in audience_options else 0
                            
                            new_audience_type = st.selectbox(
                                "Audience Type",
                                audience_options,
                                index=audience_index,
                                key=f"edit_audience_{campaign_prefix}"
                            )
                        
                        with col2:
                            status_options = ["active", "paused", "completed", "draft"]
                            current_status = campaign['status']
                            status_index = status_options.index(current_status) if current_status in status_options else 0
                            
                            new_status = st.selectbox(
                                "Status",
                                status_options,
                                index=status_index,
                                key=f"edit_status_{campaign_prefix}"
                            )
                        
                        new_message = st.text_area(
                            "Message Template",
                            value=campaign['message_template'],
                            height=100,
                            key=f"edit_message_{campaign_prefix}"
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                if not new_name.strip():
                                    st.error("❌ Campaign name is required")
                                elif not new_message.strip():
                                    st.error("❌ Message template is required")
                                else:
                                    update_data = {
                                        "name": new_name.strip(),
                                        "message_template": new_message.strip(),
                                        "audience_type": new_audience_type,
                                        "status": new_status
                                    }
                                    
                                    result = api_client.update_campaign(campaign_id, update_data)
                                    if result:
                                        st.rerun()
                        
                        with col2:
                            if st.form_submit_button("🗑️ Delete Campaign", type="secondary"):
                                st.session_state[f'delete_campaign_{campaign_prefix}'] = True
                    
                    # Campaign actions
                    st.markdown("### 🔧 Campaign Actions")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📊 View Stats", key=f"stats_btn_{campaign_prefix}"):
                            stats = api_client.get_campaign_stats(campaign_id)
                            if stats:
                                st.write("**📈 Campaign Statistics:**")
                                st.write(f"• Total Sent: {stats['total_sent']}")
                                st.write(f"• Delivered: {stats['delivered']}")
                                st.write(f"• Failed: {stats['failed']}")
                                st.write(f"• Delivery Rate: {stats['delivery_rate']:.1f}%")
                    
                    with col2:
                        if st.button(f"🔄 Duplicate", key=f"duplicate_btn_{campaign_prefix}"):
                            st.session_state.duplicate_campaign = campaign
                            st.info("💡 Switch to 'Create Campaign' tab to see the duplicated template.")
                    
                    with col3:
                        if st.button(f"📤 Export", key=f"export_btn_{campaign_prefix}"):
                            campaign_export_data = f"""Campaign Export
Name: {campaign['name']}
Status: {campaign['status']}
Audience Type: {campaign.get('audience_type', 'All')}
Audience Size: {campaign.get('audience_size', 0)}
Created: {created_date}
Created By: {campaign.get('created_by', 'Unknown')}

Message Template:
{campaign['message_template']}
"""
                            st.download_button(
                                label="💾 Download",
                                data=campaign_export_data,
                                file_name=f"{campaign['name']}_campaign.txt",
                                mime="text/plain",
                                key=f"download_btn_{campaign_prefix}"
                            )
                    
                    with col4:
                        if campaign['status'] == 'active':
                            if st.button(f"⏸️ Pause", key=f"pause_btn_{campaign_prefix}"):
                                update_data = {
                                    "name": campaign['name'],
                                    "message_template": campaign['message_template'],
                                    "audience_type": campaign.get('audience_type'),
                                    "status": "paused"
                                }
                                result = api_client.update_campaign(campaign_id, update_data)
                                if result:
                                    st.rerun()
                        elif campaign['status'] == 'paused':
                            if st.button(f"▶️ Resume", key=f"resume_btn_{campaign_prefix}"):
                                update_data = {
                                    "name": campaign['name'],
                                    "message_template": campaign['message_template'],
                                    "audience_type": campaign.get('audience_type'),
                                    "status": "active"
                                }
                                result = api_client.update_campaign(campaign_id, update_data)
                                if result:
                                    st.rerun()
                    
                    # Delete campaign confirmation
                    if st.session_state.get(f'delete_campaign_{campaign_prefix}', False):
                        st.markdown("---")
                        st.error(f"⚠️ **Confirm Deletion of '{campaign['name']}'**")
                        st.write("This will permanently delete this campaign. This action cannot be undone.")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(f"🗑️ Yes, Delete Campaign", key=f"confirm_delete_btn_{campaign_prefix}", type="primary"):
                                result = api_client.delete_campaign(campaign_id)
                                if result:
                                    st.session_state[f'delete_campaign_{campaign_prefix}'] = False
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"❌ Cancel", key=f"cancel_delete_btn_{campaign_prefix}"):
                                st.session_state[f'delete_campaign_{campaign_prefix}'] = False
                                st.rerun()
        
        else:
            st.info("📄 No campaigns found. Create your first campaign using the 'Create Campaign' tab.")
    
    except Exception as e:
        st.error(f"Failed to load campaigns: {str(e)}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** All campaigns are saved to the database with full edit/delete capabilities. Changes take effect immediately.")
