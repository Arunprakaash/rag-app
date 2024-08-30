import os
from typing import Any, Optional

import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

from consts import CONFIG_PATH

API_URL = os.getenv("API_URL", "http://localhost:8000/api")


def load_config() -> Any:
    """Load the configuration file."""
    with open(CONFIG_PATH) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return add_tenants_to_config(config)


def add_tenants_to_config(config: dict) -> dict:
    """Add tenants to the configuration."""
    if 'credentials' not in config:
        config['credentials'] = {}
    if 'usernames' not in config['credentials']:
        config['credentials']['usernames'] = {}

    for user in get_tenants() or []:
        config['credentials']['usernames'][user['name']] = {
            'name': user['name'],
            'password': stauth.Hasher([user['name']]).generate()[0]
        }
    return config


def get_tenants() -> Optional[Any]:
    """Retrieve tenants from the API."""
    try:
        response = requests.get(f"{API_URL}/tenants")
        response.raise_for_status()
        return response.json() or []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tenants: {e}")
        return None


def get_tenant_id(tenant_name: str) -> Optional[Any]:
    """Get tenant ID using their name."""
    try:
        response = requests.post(f"{API_URL}/login", params={"username": tenant_name, "password": tenant_name})
        response.raise_for_status()
        return response.json().get('id')
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")
        return None


def query_knowledge_base(tenant_id: str, query: str) -> Any:
    """Query the knowledge base for a specific tenant."""
    try:
        response = requests.post(f"{API_URL}/query/{tenant_id}", json={"text": query, "k": 5})
        response.raise_for_status()
        return response.json().get("response", "No relevant information found.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying knowledge base: {e}")
        return {"error": str(e)}
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return {"error": str(e)}


def add_custom_css():
    """Add custom CSS to hide Streamlit header."""
    st.markdown("""
    <style>
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def footer(authenticator: Authenticate):
    """Display footer with logout button."""
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
    st.button(
        "Logout",
        on_click=lambda: authenticator.logout(location='unrendered'),
        help="Log out of the application",
        type='primary'
    )
