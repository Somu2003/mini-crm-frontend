# Mini CRM - Frontend (Streamlit)

## 🚀 Overview
This is the **Frontend** for the Mini CRM system, built with **Streamlit**.  
It provides an interface for users to manage customers, create campaigns, view analytics, and track orders.

---

## 🛠️ Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mini-crm-frontend.git
   cd mini-crm-frontend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate    # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open in browser:
   ```
   http://localhost:8501
   ```

---
## Architecture Diagram

<img width="237" height="892" alt="image" src="https://github.com/user-attachments/assets/1a9822b7-9dd3-480d-ac60-20aeab11cec1" />

## ☁️ Deployment on Render

1. Push your code to GitHub.

2. Go to [Render.com](https://render.com).

3. Create a new **Web Service**:
   - Select your **frontend repo**.
   - Runtime: **Python 3.9+**
   - Build Command:  
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:  
     ```bash
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
     ```

4. Configure environment variables if needed.

5. Deploy 🚀

6. Access frontend at:
   ```
   https://your-frontend.onrender.com
   ```
