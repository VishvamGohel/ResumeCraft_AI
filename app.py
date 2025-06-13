# --- START OF FILE app.py (Final "Simple Path" Attempt) ---

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

# --- Load API Key ---
def load_api_key():
    try:
        return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv("app.env")
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found.")
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

# --- NEW: Helper function to safely load images ---
# This version uses the simplest possible path.
def load_image(image_path):
    try:
        return Image.open(image_path)
    except FileNotFoundError:
        # If an image is missing, we'll now display the error path directly.
        st.error(f"CRITICAL ERROR: Could not find image at path: '{os.path.abspath(image_path)}'. Please check GitHub repo structure.")
        return Image.new('RGB', (400, 300), color='red')

# --- Using simple, hard-coded relative paths ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", load_image("assets/corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", load_image("assets/modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", load_image("assets/aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", load_image("assets/classic.png"))
}

# --- UI: Sidebar ---
# ... (Sidebar code is unchanged) ...
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

# --- CSS & Hero Section (No changes) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 
st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)

# --- Main App Body: The Template Selector ---
st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
st.title("🎨 Choose Your Resume Style")
st.markdown("Select a template to generate your resume with that look and feel.")
st.write("") 

def create_template_card(template_name):
    filename, color, image_object = templates[template_name]
    st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
    st.subheader(template_name)
    st.image(image_object, use_container_width=True)
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
            json_prompt = f"Generate a resume...DETAILS TO PARSE: {user_data}"
            response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
            json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
            resume_data = json.loads(json_string)
            # Use the simplest template loader path
            env = Environment(loader=FileSystemLoader('.')) 
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
    st.session_state.generation_request = None
