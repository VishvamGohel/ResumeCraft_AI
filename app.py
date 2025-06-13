# --- START OF FILE app.py (Final Version with Robust Pathing) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Define Base Directory using an OS-agnostic method ---
# This gets the directory where the app.py script itself is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load API Key (Handles both local .env and Streamlit Secrets) ---
def load_api_key():
    try:
        return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Construct path to .env file for local development
        dotenv_path = os.path.join(BASE_DIR, "app.env")
        load_dotenv(dotenv_path=dotenv_path)
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found. Please set it in your app.env file or in Streamlit Cloud secrets.")
    st.stop()

# --- Initialize AI Client ---
try:
    co = cohere.Client(api_key)
except Exception as e:
    st.error(f"❌ Error configuring Cohere client: {e}")
    st.stop()

# --- Helper Function ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

# --- Templates Dictionary using os.path.join for absolute reliability ---
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", os.path.join(ASSETS_DIR, "corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", os.path.join(ASSETS_DIR, "modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", os.path.join(ASSETS_DIR, "aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", os.path.join(ASSETS_DIR, "classic.png"))
}

# --- UI: Sidebar ---
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

# --- CSS Injection & Hero Section ---
# (No changes needed here, this part is fine)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 
st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)

# --- Main App Body: The Template Selector ---
st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
st.title("🎨 Choose Your Resume Style")
st.markdown("Select a template to generate your resume with that look and feel.")
st.write("") 

def create_template_card(template_name):
    filename, color, image_path = templates[template_name]
    st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
    st.subheader(template_name)
    st.image(image_path, use_container_width=True)
    if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
        st.session_state.button_clicked = {"template_filename": filename, "accent_color": color}
    st.markdown('</div>', unsafe_allow_html=True)

# Grid creation logic
row1_col1, row1_col2 = st.columns(2)
with row1_col1: create_template_card("Corporate")
with row1_col2: create_template_card("Modern")
st.markdown("<br>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)
with row2_col1: create_template_card("Aesthetic")
with row2_col2: create_template_card("Classic")
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Button Clicks and Trigger Generation ---
if 'button_clicked' in st.session_state and st.session_state.button_clicked:
    if not all([name, email, education_input, skills_input, projects_input]):
        st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
    else:
        st.session_state.generation_request = st.session_state.button_clicked
        st.session_state.generation_request['user_data'] = {
            "target_role": target_role, "name": name, "email": email,
            "education_input": education_input, "skills_input": skills_input,
            "projects_input": projects_input, "experience_input": experience_input
        }
        st.rerun()
    st.session_state.button_clicked = None

# --- Generation Logic ---
if 'generation_request' in st.session_state and st.session_state.generation_request:
    request = st.session_state.generation_request
    with st.spinner("AI is crafting your signature resume..."):
        try:
            user_data = request['user_data']
            json_prompt = f"Generate a resume in structured JSON format...DETAILS TO PARSE: {user_data}" # Truncated for brevity
            response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
            json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
            resume_data = json.loads(json_string)
            # Use the robust BASE_DIR for the template loader
            env = Environment(loader=FileSystemLoader(BASE_DIR)) 
            template = env.get_template(request["template_filename"])
            html_out = template.render(resume_data, accent_color=request["accent_color"])
            pdf_bytes = html_to_pdf(html_out)
            if pdf_bytes:
                st.success("🎉 Your professional resume is ready!")
                st.balloons()
                st.subheader("📄 PDF Preview")
                st.components.v1.html(html_out, height=800, scrolling=True)
                st.download_button(label="📥 Download PDF Resume", data=pdf_bytes, file_name=f"{user_data['name'].replace(' ', '_')}_Resume.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
            # Add more specific error handling if needed
    st.session_state.generation_request = None
