# --- START OF FILE app.py (Final Homepage Fix) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import base64

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Initialize Session State: This is the key to our UI flow ---
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None

# --- Load API Key ---
@st.cache_data
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
@st.cache_resource
def get_cohere_client():
    return cohere.Client(api_key)

co = get_cohere_client()

# --- Helper Function ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

# --- Embedded Image Data ---
# Paste your actual Base64 strings here. I've used placeholders for brevity.
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_YOUR_CORPORATE_BASE64_STRING_HERE"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_YOUR_MODERN_BASE64_STRING_HERE"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_YOUR_AESTHETIC_BASE64_STRING_HERE"),
    "Classic": ("template.html", "#2c3e50", "PASTE_YOUR_CLASSIC_BASE64_STRING_HERE")
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

# --- CSS Injection (No changes needed) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

# --- Main App Logic: Two-State Display ---

# STATE 1: Show the homepage and template selectors by default
if not st.session_state.show_result:
    
    # Homepage / Hero Section
    st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)
    
    # Template Selector
    st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume with that look and feel.")
    st.write("") 

    generation_request = None

    # Create the 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    template_names = list(templates.keys())

    with row1_col1:
        template_name = template_names[0]
        filename, color, image_data = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        st.image(image_data, use_container_width=True)
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            generation_request = {"template_filename": filename, "accent_color": color}
        st.markdown('</div>', unsafe_allow_html=True)

    with row1_col2:
        template_name = template_names[1]
        filename, color, image_data = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        st.image(image_data, use_container_width=True)
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            generation_request = {"template_filename": filename, "accent_color": color}
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        template_name = template_names[2]
        filename, color, image_data = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        st.image(image_data, use_container_width=True)
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            generation_request = {"template_filename": filename, "accent_color": color}
        st.markdown('</div>', unsafe_allow_html=True)

    with row2_col2:
        template_name = template_names[3]
        filename, color, image_data = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        st.image(image_data, use_container_width=True)
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            generation_request = {"template_filename": filename, "accent_color": color}
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Generation Logic is triggered if a button was clicked
    if generation_request:
        if not all([name, email, education_input, skills_input, projects_input]):
            st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
        else:
            with st.spinner("AI is crafting your signature resume..."):
                try:
                    user_data = {
                        "target_role": target_role, "name": name, "email": email,
                        "education_input": education_input, "skills_input": skills_input,
                        "projects_input": projects_input, "experience_input": experience_input
                    }
                    json_prompt = f"Generate a resume...DETAILS TO PARSE: {user_data}"
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
                    json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
                    resume_data = json.loads(json_string)
                    env = Environment(loader=FileSystemLoader(os.getcwd()))
                    template = env.get_template(generation_request["template_filename"])
                    html_out = template.render(resume_data, accent_color=generation_request["accent_color"])
                    pdf_bytes = html_to_pdf(html_out)

                    if pdf_bytes:
                        # Store the results and switch state
                        st.session_state.generation_output = {
                            "pdf": pdf_bytes,
                            "html": html_out,
                            "filename": f"{user_data['name'].replace(' ', '_')}_Resume.pdf"
                        }
                        st.session_state.show_result = True
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

# STATE 2: A resume has been generated, so we show the results page
else:
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
        # Reset the state to go back to the homepage
        st.session_state.show_result = False
        st.session_state.generation_output = None
        st.rerun()
