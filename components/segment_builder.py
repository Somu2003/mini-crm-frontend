import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.api_client import APIClient

class SegmentBuilder:
    def __init__(self):
        self.api_client = APIClient()
        
        # Initialize session state for segment rules
        if "segment_rules" not in st.session_state:
            st.session_state.segment_rules = []
        if "logic_operator" not in st.session_state:
            st.session_state.logic_operator = "AND"
    
    def render_rule_builder(self):
        st.markdown("## 🎯 Build Your Audience Segment")
        
        # Tabs for different building methods
        tab1, tab2 = st.tabs(["🤖 AI Assistant", "🔧 Manual Builder"])
        
        with tab1:
            self._render_ai_segment_builder()
        
        with tab2:
            self._render_manual_segment_builder()
        
        # Display current rules and preview
        self._render_current_rules()
        self._render_audience_preview()
        
        return {
            "logic": st.session_state.logic_operator,
            "rules": st.session_state.segment_rules
        }
    
    def _render_ai_segment_builder(self):
        st.markdown("### 🤖 Describe Your Target Audience")
        
        natural_text = st.text_area(
            "Describe your audience:",
            placeholder="Examples:\n• People who spent more than ₹10,000\n• Customers with less than 3 orders\n• Inactive customers who haven't ordered in 90 days",
            height=100
        )
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            generate_btn = st.button("🔮 Generate Rules", type="primary", disabled=not natural_text.strip())
        
        if generate_btn and natural_text.strip():
            with st.spinner("🤖 AI is analyzing your description..."):
                result = self.api_client.parse_segment_text(natural_text.strip())
                
                if result and "rules" in result:
                    parsed_rules = result["rules"]
                    
                    if "rules" in parsed_rules and parsed_rules["rules"]:
                        st.session_state.segment_rules = parsed_rules["rules"]
                        st.session_state.logic_operator = parsed_rules.get("logic", "AND")
                        st.success("✅ AI successfully converted your description into rules!")
                        st.rerun()
                    else:
                        st.warning("⚠️ AI couldn't understand your description. Please try being more specific.")
        
        # AI suggestions
        st.markdown("### 💡 AI Suggestions")
        suggestions = [
            "High-value customers: spent over ₹25,000",
            "At-risk customers: haven't ordered in 120 days",
            "New customers: less than 3 orders",
            "VIP customers: more than 10 orders"
        ]
        
        for suggestion in suggestions:
            if st.button(f"💡 {suggestion}", key=f"suggestion_{suggestion}"):
                with st.spinner("Generating rules..."):
                    result = self.api_client.parse_segment_text(suggestion)
                    if result and "rules" in result:
                        parsed_rules = result["rules"]
                        st.session_state.segment_rules = parsed_rules["rules"]
                        st.session_state.logic_operator = parsed_rules.get("logic", "AND")
                        st.rerun()
    
    def _render_manual_segment_builder(self):
        st.markdown("### 🔧 Manual Rule Builder")
        
        # Logic operator selection
        st.session_state.logic_operator = st.selectbox(
            "Combine rules with:",
            ["AND", "OR"],
            index=0 if st.session_state.logic_operator == "AND" else 1
        )
        
        # Add new rule section
        st.markdown("#### ➕ Add New Rule")
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            field = st.selectbox("Field:", ["total_spend", "total_orders", "days_since_last_order"])
        
        with col2:
            operator = st.selectbox("Condition:", [">", ">=", "<", "<=", "="])
        
        with col3:
            if field == "total_spend":
                value = st.number_input("Amount (₹):", min_value=0.0, value=1000.0, step=100.0)
            elif field == "total_orders":
                value = st.number_input("Count:", min_value=0, value=1, step=1)
            else:  # days_since_last_order
                value = st.number_input("Days:", min_value=0, value=30, step=1)
        
        with col4:
            st.markdown("&nbsp;")
            add_rule_btn = st.button("➕", type="primary")
        
        if add_rule_btn:
            new_rule = {"field": field, "operator": operator, "value": value}
            st.session_state.segment_rules.append(new_rule)
            st.success(f"✅ Added rule!")
            st.rerun()
    
    def _render_current_rules(self):
        if st.session_state.segment_rules:
            st.markdown("### 📋 Current Segment Rules")
            
            for i, rule in enumerate(st.session_state.segment_rules):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    field_name = rule["field"].replace("_", " ").title()
                    st.markdown(f"**{i+1}.** {field_name} {rule['operator']} {rule['value']}")
                
                with col2:
                    if st.button("❌", key=f"delete_rule_{i}"):
                        st.session_state.segment_rules.pop(i)
                        st.rerun()
            
            if st.button("🗑️ Clear All Rules"):
                st.session_state.segment_rules = []
                st.rerun()
        else:
            st.info("📝 No rules defined yet. Use the AI assistant or manual builder above.")
    
    def _render_audience_preview(self):
        if st.session_state.segment_rules:
            st.markdown("### 👀 Audience Preview")
            
            if st.button("🔍 Preview Audience", type="primary"):
                rules_data = {
                    "logic": st.session_state.logic_operator,
                    "rules": st.session_state.segment_rules
                }
                
                with st.spinner("🔄 Calculating audience size..."):
                    preview = self.api_client.preview_segment(rules_data)
                    
                    if preview:
                        audience_size = preview.get("audience_size", 0)
                        st.success(f"🎯 **Audience Size: {audience_size} customers**")
                        
                        sample_customers = preview.get("sample_customers", [])
                        if sample_customers:
                            st.markdown("#### 👥 Sample Customers")
                            for customer in sample_customers:
                                st.write(f"👤 {customer['name']} - ₹{customer.get('total_spend', 0):,.0f}")
                    else:
                        st.warning("⚠️ No customers match your criteria.")
