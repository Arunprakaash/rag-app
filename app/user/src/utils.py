import os
from typing import Text, Any
import requests
import streamlit as st

API_URL = os.getenv("API_URL")


def set_current_tenant(tenant_id: Text) -> None:
    st.session_state.current_tenant_id = tenant_id
    st.session_state.chat_history = []
    st.session_state.is_authenticated = True


def login(username, password):
    try:
        response = requests.post(f"{API_URL}/login", params={"username": username, "password": password})
        response_data = response.json()

        if response.status_code == 200:
            set_current_tenant(response_data["id"])
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")



def query_knowledge_base(tenant_id: Text, query: Text) -> Any:
    try:
        response = requests.post(f"{API_URL}/query/{tenant_id}", json={"text": query, "k": 5})
        response.raise_for_status()
        query_results = response.json()
        return query_results.get("response", "No relevant information found.")
    except requests.exceptions.RequestException as e:
        st.toast(f"Error querying knowledge base: {e}", icon="🚨")
        return "Error querying knowledge base."
    except Exception as e:
        st.toast(f"Unexpected error: {e}", icon="🚨")
        return "Unexpected error occurred."


def add_custom_css():
    st.markdown("""
            <style>
            /* Add your custom CSS here */
            </style>
        """, unsafe_allow_html=True)


def footer():
    st.caption("---------")
    st.markdown(
        """
        <div style="text-align: center;">
            <p>Questions, feature requests, or found a bug? Open an issue on
                <a href="https://github.com/Arunprakaash/rag-app/issues/new" target="_blank">GitHub</a>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
