# --- START OF FILE app.py (SyntaxError Corrected) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PIL import Image

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Define Base Directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load API Key ---
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found. Please check secrets/env.")
    st.stop()

# --- Initialize AI Client ---
try:
    co = cohere.Client(api_key)
except Exception as e:
    st.error(f"❌ Error configuring Cohere client: {e}")
    st.stop()

# --- Helper Functions ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

def get_image_path(filename):
    return os.path.join(BASE_DIR, "assets", filename)

# --- Templates Dictionary ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", get_image_path("corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", get_image_path("modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", get_image_path("aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", get_image_path("classic.png"))
}

# --- Initialize Session State ---
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None
if "generation_request" not in st.session_state:
    st.session_state.generation_request = None

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

# --- CSS Injection (No changes) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

# --- UI LOGIC ---

# If a result exists, show it and a "start over" button
if st.session_state.generation_output:
    st.success("🎉 Your professional resume is ready!")
    st.balloons()
    st.subheader("📄 PDF Preview")
    st.components.v1.html(st.session_state.generation_output["html"], height=800, scrolling=True)
    st.download_button(
        label="📥 Download PDF Resume",
        data=st.session_state.generation_output["pdf"],
        file_name=st.session_state.generation_output["filename"],
        mime="application/pdf"
    )
    if st.button("✨ Create a New Resume"):
        st.session_state.generation_output = None
        st.session_state.generation_request = None
        st.rerun()

# Otherwise, if a generation is pending, run it
elif st.session_state.generation_request:
    request = st.session_state.generation_request
    with st.spinner("AI is crafting your signature resume..."):
        try:
            user_data = request['user_data']
            json_prompt = f"Generate a resume...DETAILS TO PARSE: {user_data}"
            response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
            json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
            resume_data = json.loads(json_string)
            env = Environment(loader=FileSystemLoader(BASE_DIR))
            template = env.get_template(request["template_filename"])
            html_out = template.render(resume_data, accent_color=request["accent_color"])
            pdf_bytes = html_to_pdf(html_out)
            if pdf_bytes:
                st.session_state.generation_output = {
                    "pdf": pdf_bytes, "html": html_out,
                    "filename": f"{user_data['name'].replace(' ', '_')}_Resume.pdf"
                }
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
            st.session_state.generation_output = None # Ensure we can retry
    
    st.session_state.generation_request = None # Clear request after attempting
    st.rerun()

# Default state: show the homepage
else:
    st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)
    st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume with that look and feel.")
    st.write("") 

    def create_template_card(template_name):
        filename, color, image_path = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        try:
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        except FileNotFoundError:
            st.error(f"Asset not found: '{image_path}'")
        
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            if not all([name, email, education_input, skills_input, projects_input]):
                st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
            else:
                # Set the request in session_state and rerun
                st.session_state.generation_request = {
                    "template_filename": filename,
                    "accent_color": color,
                    "user_data": {
                        "target_role": target_role, "name": name, "email": email,
                        "education_input": education_input, "skills_input": skills_input,
                        "projects_input": projects_input, "experience_input": experience_input
                    }
                }
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1: create_template_card("Corporate")
    with row1_col2: create_template_card("Modern")
    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1: create_template_card("Aesthetic")
    with row2_col2: create_template_card("Classic")
    st.markdown('</div>', unsafe_allow_html=True)
