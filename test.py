import google.generativeai as genai
from pydantic import BaseModel
import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. Schema Definition ---
class InvoiceData(BaseModel):
    vendor_name: str
    total_amount: float
    issue_date: str
    due_date: str
    items: list[str]


def extract_document(file_bytes, mime_type):
    
    return {'vendor_name': "DEMO - Sliced Invoices", 
            'total_amount': 93.5, 
            'due_date': "2016-01-31", 
            'issue_date': "2016-01-25",
            'items': ["Web Design"]
            }

# --- 3. Streamlit UI ---
st.set_page_config(page_title="AI Document Orchestrator", page_icon="📑")
st.title("📑 AI Invoice Document Orchestrator")
st.markdown("### Intelligent Invoice Processing & Automation")

uploaded_file = st.file_uploader("Upload Invoice (PDF, PNG, JPG)", type=['pdf', 'png', 'jpg'])

if uploaded_file:
    # Determine mime type
    mime_type = "application/pdf" if uploaded_file.type == "application/pdf" else "image/jpeg"
    
    # Session state to persist data between clicks
    if 'extracted_data' not in st.session_state:
        with st.spinner("Gemini AI is extracting data..."):
            try:
                st.session_state.extracted_data = extract_document(uploaded_file.getvalue(), mime_type)
            except Exception as e:
                st.error(f"Extraction failed: {e}")

    if 'extracted_data' in st.session_state:
        data = st.session_state.extracted_data
        
        # Display Data in a clean way
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Vendor:**", data['vendor_name'])
            st.metric("**Total Amount:**", f"${data['total_amount']:.2f}")
        with col2:
            st.write("**Due Date:**", data['due_date'])
            st.write("**Issue Date:**", data['issue_date'])
            st.write("**Items:**", ", ".join(data['items']))

        st.divider()
        
        min_amount = st.slider(
            "**Min Amount**", 
            min_value=0, 
            max_value=1000, 
            value=40, 
            step=10, 
            label_visibility="visible"
            )
        
        max_due_days = st.slider(
            "**Max Due Days**", 
            min_value=1, 
            max_value=100, 
            value=16, 
            step=1, 
            label_visibility="visible"
            )

        # 4. Trigger Automation (n8n)
        if st.button("🚀 Send to Automatic Handler"):
            # Use your production/tunnel URL if not running n8n locally
            n8n_url = st.secrets["N8N_TEST_URL"]
            
            data['min_amount'] = min_amount
            data['max_due_days'] = max_due_days
            
            issue_date = datetime.strptime(data['issue_date'], "%Y-%m-%d")
            due_date = datetime.strptime(data['due_date'], "%Y-%m-%d")
            remaining_due_days = (due_date - issue_date).days
            
            data['remaining_due_days'] = remaining_due_days
            
            with st.spinner("Triggering workflow..."):
                try:
                    res = requests.post(n8n_url, json=data)
                    if res.status_code == 200:
                        st.success("✅ Workflow triggered! Document Handled!")
                    else:
                        st.error(f"n8n returned error: {res.status_code}")
                except Exception as e:
                    st.error(f"Connection failed: Ensure n8n is running and the webhook is active.")