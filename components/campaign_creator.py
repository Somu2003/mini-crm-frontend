import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.api_client import APIClient
from components.segment_builder import SegmentBuilder
from components.auth_component import AuthComponent

class CampaignCreator:
    """Component for creating and managing campaigns"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.segment_builder = SegmentBuilder()
        self.auth_component = AuthComponent()
    
    def render_campaign_creator(self):
        """Render the complete campaign creation interface"""
        
        st.markdown("## 🚀 Create New Campaign")
        
        # Campaign basic information
        with st.expander("📝 Campaign Details", expanded=True):
            campaign_name = st.text_input(
                "Campaign Name *",
                placeholder="e.g., Black Friday Sale - High Value Customers",
                help="Give your campaign a descriptive name"
            )
            
            campaign_objective = st.text_input(
                "Campaign Objective",
                placeholder="e.g., Bring back inactive customers, Promote new products",
                help="Describe what you want to achieve (used for AI message generation)"
            )
        
        # Audience segmentation
        st.markdown("### 🎯 Target Audience")
        segment_rules = self.segment_builder.render_rule_builder()
        
        # Message creation section
        st.markdown("### 📱 Campaign Message")
        
        # AI message generation
        if campaign_objective:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Let AI suggest messages based on your objective:**")
            
            with col2:
                if st.button("🤖 Generate AI Messages", type="secondary"):
                    with st.spinner("🤖 Generating personalized messages..."):
                        ai_result = self.api_client.generate_ai_message(campaign_objective)
                        if ai_result and "messages" in ai_result:
                            st.session_state.ai_messages = ai_result["messages"]
                            st.success("✅ AI generated message options!")
        
        # Display AI generated messages
        if st.session_state.get("ai_messages"):
            st.markdown("**🤖 AI Message Suggestions:**")
            
            for i, message in enumerate(st.session_state.ai_messages):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.code(message, language=None)
                
                with col2:
                    if st.button(f"Use #{i+1}", key=f"use_msg_{i}"):
                        st.session_state.selected_message = message
                        st.success(f"✅ Selected message {i+1}")
        
        # Message template input
        default_message = st.session_state.get("selected_message", "Hi {name}, here's a special offer just for you! 🎉")
        
        message_template = st.text_area(
            "Message Template *",
            value=default_message,
            help="Use {name} as placeholder for customer name. Keep under 160 characters for SMS.",
            height=100
        )
        
        # Character counter
        char_count = len(message_template)
        if char_count > 160:
            st.warning(f"⚠️ Message is {char_count} characters (recommended: under 160 for SMS)")
        else:
            st.info(f"✅ Message length: {char_count} characters")
        
        # Preview section
        if message_template and "{name}" in message_template:
            st.markdown("**📱 Message Preview:**")
            preview_message = message_template.replace("{name}", "John Doe")
            st.success(f"📱 {preview_message}")
        
        # Campaign launch section
        st.markdown("---")
        st.markdown("### 🚀 Launch Campaign")
        
        # Validation
        can_launch = all([
            campaign_name.strip(),
            segment_rules.get("rules"),
            message_template.strip(),
            "{name}" in message_template
        ])
        
        if not can_launch:
            missing = []
            if not campaign_name.strip():
                missing.append("Campaign Name")
            if not segment_rules.get("rules"):
                missing.append("Target Audience Rules")
            if not message_template.strip():
                missing.append("Message Template")
            elif "{name}" not in message_template:
                missing.append("Message must include {name} placeholder")
            
            st.error(f"❌ Please complete: {', '.join(missing)}")
        
        # Launch button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            launch_btn = st.button(
                "🚀 Launch Campaign",
                type="primary",
                disabled=not can_launch,
                use_container_width=True
            )
        
        if launch_btn and can_launch:
            # Prepare campaign data
            campaign_data = {
                "name": campaign_name.strip(),
                "segment_rules": segment_rules,
                "message_template": message_template.strip(),
                "created_by": self.auth_component.get_user_email()
            }
            
            with st.spinner("🚀 Launching campaign..."):
                result = self.api_client.create_campaign(campaign_data)
                
                if result:
                    st.balloons()
                    st.success("🎉 Campaign launched successfully!")
                    
                    # Show campaign summary
                    st.markdown("### 📊 Campaign Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Campaign Name", campaign_name)
                        st.metric("Target Audience", f"{result.get('audience_size', 0)} customers")
                    
                    with col2:
                        st.metric("Message Template", f"{len(message_template)} chars")
                        st.metric("Status", "Active 🟢")
                    
                    # Clear form
                    if st.button("Create Another Campaign"):
                        st.session_state.segment_rules = []
                        if "ai_messages" in st.session_state:
                            del st.session_state.ai_messages
                        if "selected_message" in st.session_state:
                            del st.session_state.selected_message
                        st.rerun()
                else:
                    st.error("❌ Failed to launch campaign. Please try again.")

def create_campaign_creator():
    """Factory function to create campaign creator"""
    return CampaignCreator()
