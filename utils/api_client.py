import requests
import streamlit as st

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method, endpoint, data=None, params=None, success_message=None):
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            
            if response.status_code == 200:
                if success_message:
                    st.success(success_message)
                return response.json()
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else f"HTTP {response.status_code}"
                st.error(f"❌ API Error: {error_detail}")
                return None
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to server. Please ensure backend is running on http://localhost:8000")
            return None
        except Exception as e:
            st.error(f"❌ Request failed: {str(e)}")
            return None
    
    # ================================
    # CUSTOMER CRUD METHODS
    # ================================
    
    def get_customers(self, search=None):
        params = {'search': search} if search else None
        return self._make_request('GET', '/customers', params=params) or []
    
    def get_customer(self, customer_id):
        return self._make_request('GET', f'/customers/{customer_id}')
    
    def create_customer(self, customer_data):
        return self._make_request('POST', '/customers', data=customer_data, success_message="✅ Customer created!")
    
    def update_customer(self, customer_id, customer_data):
        return self._make_request('PUT', f'/customers/{customer_id}', data=customer_data, success_message="✅ Customer updated!")
    
    def delete_customer(self, customer_id):
        return self._make_request('DELETE', f'/customers/{customer_id}', success_message="🗑️ Customer deleted!")
    
    # ================================
    # ORDER CRUD METHODS
    # ================================
    
    def get_orders(self, customer_id=None):
        params = {'customer_id': customer_id} if customer_id else None
        return self._make_request('GET', '/orders', params=params) or []
    
    def get_order(self, order_id):
        return self._make_request('GET', f'/orders/{order_id}')
    
    def create_order(self, order_data):
        return self._make_request('POST', '/orders', data=order_data, success_message="✅ Order created!")
    
    def update_order(self, order_id, order_data):
        return self._make_request('PUT', f'/orders/{order_id}', data=order_data, success_message="✅ Order updated!")
    
    def delete_order(self, order_id):
        return self._make_request('DELETE', f'/orders/{order_id}', success_message="🗑️ Order deleted!")
    
    # ================================
    # CAMPAIGN CRUD METHODS
    # ================================
    
    def get_campaigns(self):
        return self._make_request('GET', '/campaigns') or []
    
    def get_campaign(self, campaign_id):
        return self._make_request('GET', f'/campaigns/{campaign_id}')
    
    def create_campaign(self, campaign_data):
        return self._make_request('POST', '/campaigns', data=campaign_data, success_message="🚀 Campaign launched!")
    
    def update_campaign(self, campaign_id, campaign_data):
        return self._make_request('PUT', f'/campaigns/{campaign_id}', data=campaign_data, success_message="✅ Campaign updated!")
    
    def delete_campaign(self, campaign_id):
        return self._make_request('DELETE', f'/campaigns/{campaign_id}', success_message="🗑️ Campaign deleted!")
    
    def get_campaign_stats(self, campaign_id):
        return self._make_request('GET', f'/campaigns/{campaign_id}/stats')
    
    # ================================
    # AI & ANALYTICS METHODS
    # ================================
    
    def generate_ai_message(self, objective):
        return self._make_request('GET', '/ai/generate-message', params={'objective': objective})
    
    def get_dashboard_stats(self):
        return self._make_request('GET', '/analytics/dashboard')
    
    def get_customer_segments(self):
        return self._make_request('GET', '/analytics/customer-segments')
    
    def preview_segment(self, rules):
        return self._make_request('POST', '/segments/preview', data=rules)
