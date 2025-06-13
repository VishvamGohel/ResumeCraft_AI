# --- START OF FILE app.py (Final Corrected Version) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load API Key ---
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
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
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_CORPORATE_BASE64"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_MODERN_BASE64"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_AESTHETIC_BASE64"),
    "Classic": ("template.html", "#2c3e50", "PASTE_CLASSIC_BASE64")
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

# --- CSS Injection (No changes) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

# --- Homepage / Hero Section ---
st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)

# --- Template Selector ---
st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
st.title("🎨 Choose Your Resume Style")
st.markdown("Select a template to generate your resume with that look and feel.")
st.write("") 

generation_request = None # Initialize to None on each run

# --- THIS IS THE CORRECTED FUNCTION ---
def create_template_card(col, template_name):
    with col:
        filename, color, image_data = templates[template_name]
        st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
        st.subheader(template_name)
        st.image(image_data, use_container_width=True)
        if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
            # If button is clicked, RETURN the request data
            return {"template_filename": filename, "accent_color": color}
        st.markdown('</div>', unsafe_allow_html=True)
    # If button is not clicked, return None
    return None

# --- Create the 2x2 grid and capture the return value ---
row1_col1, row1_col2 = st.columns(2)
# We check if any of the function calls return a request
request1 = create_template_card(row1_col1, "Corporate")
request2 = create_template_card(row1_col2, "Modern")
st.markdown("<br>", unsafe_allow_html=True)
row2_col1, row2_col2 = st.columns(2)
request3 = create_template_card(row2_col1, "Aesthetic")
request4 = create_template_card(row2_col2, "Classic")

# The final request is whichever one is not None
generation_request = request1 or request2 or request3 or request4

st.markdown('</div>', unsafe_allow_html=True)

# --- Generation Logic ---
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
                # Corrected the Jinja2 loader path to be robust
                env = Environment(loader=FileSystemLoader(os.getcwd()))
                template = env.get_template(generation_request["template_filename"])
                html_out = template.render(resume_data, accent_color=generation_request["accent_color"])
                pdf_bytes = html_to_pdf(html_out)

                if pdf_bytes:
                    st.divider()
                    st.success("🎉 Your professional resume is ready!")
                    st.balloons()
                    st.subheader("📄 PDF Preview")
                    st.components.v1.html(html_out, height=800, scrolling=True)
                    st.download_button(
                        label="📥 Download PDF Resume",
                        data=pdf_bytes,
                        file_name=f"{user_data['name'].replace(' ', '_')}_Resume.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {e}")
