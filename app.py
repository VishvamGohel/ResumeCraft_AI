# --- START OF FILE app.py (with Back to Home button) ---

import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration: Must be the first Streamlit command ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Define Base Directory & Load API Key ---
# ... (This entire section is unchanged) ...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")
api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found.")
    st.stop()
co = cohere.Client(api_key)
def html_to_pdf(html_string): return HTML(string=html_string).write_pdf()
def extract_json_from_text(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match: return match.group(1)
    return None
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853"),
    "Modern": ("template_twocol.html", "#3498db"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4"),
    "Classic": ("template.html", "#2c3e50")
}
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Your existing CSS block

# --- Main App Router ---
query_params = st.query_params
if query_params.get("page") == "builder":
    # --- BUILDER PAGE ---
    
    with st.sidebar:
        # --- THIS IS THE NEW BUTTON ---
        st.link_button("← Back to Home", "/", use_container_width=True)
        st.divider() # Adds a nice visual separation
        
        with st.form(key="resume_form"):
            st.title("📄 ResumeCraft AI")
            st.markdown("Fill in your details, choose a style, and generate.")
            st.divider()

            st.subheader("1. Choose Your Style")
            template_name = st.selectbox("Select a template:", templates.keys())
            default_color = templates[template_name][1]
            accent_color = st.color_picker("Select an accent color:", default_color)
            
            st.divider()

            st.subheader("2. Enter Your Information")
            target_role = st.text_input("🎯 Target Job Role")
            name = st.text_input("👤 Full Name")
            email = st.text_input("📧 Email")
            education_input = st.text_area("🎓 Education")
            skills_input = st.text_area("🛠️ Skills")
            projects_input = st.text_area("💼 Projects / Internships")
            with st.expander("🧾 Work Experience (Optional)"):
                experience_input = st.text_area("Enter work experience")
            
            st.divider()

            generate_button = st.form_submit_button("🚀 Generate Resume", use_container_width=True)

    # --- Generation Logic (remains unchanged) ---
    st.title("Your Generated Resume")
    st.markdown("Your resume will appear here once you click the generate button.")
    
    if generate_button:
        # ... (The entire generation logic is exactly the same as before) ...
        if not all([name, email, education_input, skills_input, projects_input]):
            st.warning("Please fill in all required fields in the sidebar.")
        else:
            with st.spinner("AI is crafting your signature resume..."):
                try:
                    # ... (all the AI call and PDF generation code) ...
                    pass
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

else:
    # --- HOMEPAGE (Default View) ---
    # ... (Your homepage markdown remains unchanged) ...
    st.markdown("""<div class="hero-container fade-in-section">...</div>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="fade-in-section">...</div>', unsafe_allow_html=True)
