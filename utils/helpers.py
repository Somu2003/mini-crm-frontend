"""
Helper utility functions for the Mini CRM Platform frontend
"""

import streamlit as st
from datetime import datetime, timedelta
import re

def format_currency(amount):
    """Format amount as Indian Rupees"""
    if amount is None:
        return "₹0"
    return f"₹{amount:,.0f}"

def format_date(date_string):
    """Format ISO date string for display"""
    if not date_string:
        return "Never"
    
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%d %b %Y")
    except:
        return "Invalid Date"

def format_datetime(datetime_string):
    """Format ISO datetime string for display"""
    if not datetime_string:
        return "Never"
    
    try:
        dt_obj = datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return dt_obj.strftime("%d %b %Y, %I:%M %p")
    except:
        return "Invalid Date"

def calculate_days_ago(date_string):
    """Calculate days between date and now"""
    if not date_string:
        return None
    
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        days_diff = (datetime.now(date_obj.tzinfo) - date_obj).days
        return days_diff
    except:
        return None

def format_days_ago(date_string):
    """Format date as 'X days ago' or 'Today' etc."""
    days = calculate_days_ago(date_string)
    
    if days is None:
        return "Never"
    elif days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Should be 10 digits (Indian mobile) or 11 digits (with country code)
    return len(digits_only) in [10, 11]

def get_customer_status(customer):
    """Get customer status based on activity"""
    last_order_days = calculate_days_ago(customer.get('last_order_date'))
    total_spend = customer.get('total_spend', 0)
    total_orders = customer.get('total_orders', 0)
    
    if not last_order_days:
        return "New", "🆕", "#17a2b8"
    elif last_order_days <= 30:
        return "Active", "🟢", "#28a745"
    elif last_order_days <= 90:
        return "At Risk", "🟡", "#ffc107"
    else:
        return "Inactive", "🔴", "#dc3545"

def get_customer_tier(customer):
    """Get customer tier based on spend and orders"""
    total_spend = customer.get('total_spend', 0)
    total_orders = customer.get('total_orders', 0)
    
    if total_spend >= 50000 or total_orders >= 10:
        return "VIP", "💎", "#8e24aa"
    elif total_spend >= 20000 or total_orders >= 5:
        return "Premium", "⭐", "#ff9800"
    elif total_spend >= 5000 or total_orders >= 2:
        return "Regular", "👤", "#2196f3"
    else:
        return "New", "🆕", "#9e9e9e"

def show_success_message(message, duration=3):
    """Show animated success message"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Show formatted error message"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Show formatted warning message"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Show formatted info message"""
    st.info(f"ℹ️ {message}")

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def format_campaign_status(status):
    """Format campaign status with appropriate emoji and color"""
    status_map = {
        "active": ("🟢 Active", "#28a745"),
        "paused": ("⏸️ Paused", "#ffc107"),
        "completed": ("✅ Completed", "#17a2b8"),
        "draft": ("📝 Draft", "#6c757d")
    }
    
    return status_map.get(status.lower(), ("❓ Unknown", "#6c757d"))

def calculate_delivery_rate(delivered, total):
    """Calculate and format delivery rate"""
    if total == 0:
        return "N/A"
    
    rate = (delivered / total) * 100
    
    if rate >= 95:
        return f"🟢 {rate:.1f}%"
    elif rate >= 85:
        return f"🟡 {rate:.1f}%"
    else:
        return f"🔴 {rate:.1f}%"

def format_large_number(number):
    """Format large numbers with K, M suffixes"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(int(number))

def create_progress_bar(current, total, label="Progress"):
    """Create a styled progress bar"""
    if total == 0:
        percentage = 0
    else:
        percentage = min((current / total) * 100, 100)
    
    st.write(f"**{label}:** {current}/{total} ({percentage:.1f}%)")
    st.progress(percentage / 100)

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim underscores from ends
    sanitized = sanitized.strip('_')
    
    return sanitized or "untitled"

def truncate_text(text, max_length=50):
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

class SessionManager:
    """Manage Streamlit session state"""
    
    @staticmethod
    def get(key, default=None):
        """Get value from session state"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key, value):
        """Set value in session state"""
        st.session_state[key] = value
    
    @staticmethod
    def delete(key):
        """Delete key from session state"""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def clear_all():
        """Clear all session state"""
        st.session_state.clear()
    
    @staticmethod
    def has(key):
        """Check if key exists in session state"""
        return key in st.session_state

def render_data_table(data, columns=None, key=None):
    """Render data as a nice table without pandas dependency"""
    if not data:
        st.info("📄 No data to display")
        return
    
    # If data is a list of dictionaries, convert to table format
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Get column names
        if columns:
            cols = columns
        else:
            cols = list(data[0].keys())
        
        # Create table rows
        table_data = []
        for item in data:
            row = []
            for col in cols:
                value = item.get(col, "")
                # Format special fields
                if col.endswith('_date') or col.endswith('_at'):
                    value = format_date(str(value)) if value else "Never"
                elif col in ['total_spend', 'order_value'] and value:
                    value = format_currency(float(value))
                elif isinstance(value, float):
                    value = f"{value:.2f}"
                row.append(str(value))
            table_data.append(row)
        
        # Display table
        if table_data:
            # Create markdown table
            header = "| " + " | ".join(cols) + " |"
            separator = "| " + " | ".join(["---"] * len(cols)) + " |"
            
            table_md = [header, separator]
            for row in table_data:
                row_md = "| " + " | ".join(row) + " |"
                table_md.append(row_md)
            
            st.markdown("\n".join(table_md))
    else:
        st.write(data)

# Export commonly used functions
__all__ = [
    'format_currency', 'format_date', 'format_datetime',
    'calculate_days_ago', 'format_days_ago',
    'validate_email', 'validate_phone',
    'get_customer_status', 'get_customer_tier',
    'show_success_message', 'show_error_message', 'show_warning_message', 'show_info_message',
    'create_metric_card', 'format_campaign_status', 'calculate_delivery_rate',
    'format_large_number', 'create_progress_bar',
    'truncate_text', 'SessionManager', 'render_data_table'
]
