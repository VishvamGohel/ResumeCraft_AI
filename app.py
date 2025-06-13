# --- START OF FILE app.py (with Robust Paths) ---

import streamlit as st
import os
import json
from pathlib import Path  # Import the Pathlib library
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- NEW: Define robust file paths ---
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# --- Load API Keys and AI Client ---
load_dotenv("app.env")
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    # On Streamlit Cloud, keys are in secrets, not .env
    try:
        api_key = st.secrets["COHERE_API_KEY"]
    except:
        st.error("❌ COHERE_API_KEY not found.")
        st.stop()
try:
    co = cohere.Client(api_key)
except Exception as e:
    st.error(f"❌ Error configuring Cohere client: {e}")
    st.stop()

# --- Helper Function ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

# --- NEW: Templates Dictionary using robust paths ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", str(ASSETS_DIR / "corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", str(ASSETS_DIR / "modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", str(ASSETS_DIR / "aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", str(ASSETS_DIR / "classic.png"))
}

# --- UI: Sidebar ---
# ... (Your sidebar code remains unchanged) ...
with st.sidebar:
    st.title("📝 Your Information")
    st.markdown("Enter your details below to get started.")
    target_role = st.text_input("🎯 Target Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science...")
    skills_input = st.text_area("🛠️ Skills", placeholder="Python, Streamlit, Data Analysis...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Describe your projects...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience if any")

# --- CSS and Hero Section (No changes needed) ---
# ... (Your CSS and hero section markdown blocks remain the same) ...
st.markdown("""<style>...</style>""", unsafe_allow_html=True)
st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)


# --- Main App Body: The Template Selector ---
# ... (The rest of your app logic remains the same) ...
st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
st.title("🎨 Choose Your Resume Style")
st.markdown("Select a template below to generate your resume with that look and feel.")
# ... your st.columns and button logic ...
if 'button_clicked' in st.session_state and st.session_state.button_clicked:
    # ...
    st.rerun()
# ...
if 'generation_request' in st.session_state and st.session_state.generation_request:
    # ...
    st.session_state.generation_request = None
