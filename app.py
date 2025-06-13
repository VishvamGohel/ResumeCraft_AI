# --- START OF FILE app.py (Final Corrected Version) ---

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
@st.cache_data
def load_api_key():
    try:
        return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found. Please check secrets or app.env file.")
    st.stop()

# --- Initialize AI Client ---
@st.cache_resource
def get_cohere_client():
    return cohere.Client(api_key)

co = get_cohere_client()

# --- Helper Functions ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

def load_image(filename):
    try:
        return Image.open(os.path.join(BASE_DIR, "assets", filename))
    except FileNotFoundError:
        st.error(f"Asset not found: Please ensure 'assets/{filename}' exists in your GitHub repository.")
        return Image.new('RGB', (400, 300), color='red')

# --- Load all images into memory ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", load_image("corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", load_image("modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", load_image("aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", load_image("classic.png"))
}

# --- Initialize Session State for UI Flow ---
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None

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

# --- CSS Injection ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Your existing CSS is fine here

# --- Main App Logic ---

# STATE 1: Show Template Selector by default
if not st.session_state.generation_output:
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume. Your details are on the left. 👈")
    st.divider()

    generation_request = None

    # This function now returns data when its button is clicked
    def create_template_card(col, template_name):
        with col:
            filename, color, image_object = templates[template_name]
            st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
            st.subheader(template_name)
            st.image(image_object, use_container_width=True)
            if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
                return {"template_filename": filename, "accent_color": color}
            st.markdown('</div>', unsafe_allow_html=True)
        return None

    # Create the grid and capture the result of each button click
    row1_col1, row1_col2 = st.columns(2)
    request1 = create_template_card(row1_col1, "Corporate")
    request2 = create_template_card(row1_col2, "Modern")
    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    request3 = create_template_card(row2_col1, "Aesthetic")
    request4 = create_template_card(row2_col2, "Classic")

    # The final request will be whichever one was clicked (or None)
    generation_request = request1 or request2 or request3 or request4

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
                    json_prompt = f"Generate a resume...DETAILS TO PARSE: {user_data}" # Truncated for brevity
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
                    json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
                    resume_data = json.loads(json_string)
                    env = Environment(loader=FileSystemLoader(BASE_DIR))
                    template = env.get_template(generation_request["template_filename"])
                    html_out = template.render(resume_data, accent_color=generation_request["accent_color"])
                    pdf_bytes = html_to_pdf(html_out)

                    if pdf_bytes:
                        # Store the result in session_state and rerun to show the results page
                        st.session_state.generation_output = {
                            "pdf": pdf_bytes,
                            "html": html_out,
                            "filename": f"{user_data['name'].replace(' ', '_')}_Resume.pdf"
                        }
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

# STATE 2: A result exists, so show the results page
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
        st.session_state.generation_output = None
        st.rerun()
