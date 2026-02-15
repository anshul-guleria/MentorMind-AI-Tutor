import requests
import streamlit as st

API_BASE = "http://localhost:8000"

def api_call(endpoint, method="GET", payload=None, files=None):
    token = st.session_state.get("token")
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                # Do not set Content-Type header manually for files, requests does it
                response = requests.post(url, headers={"Authorization": f"Bearer {token}"} if token else {}, files=files, data=payload)
            else:
                response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.clear()
            st.rerun()
            return None
            
        if response.status_code >= 400:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
            
        return response.json()
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None