# --- START OF FILE app.py (Final Corrected Version) ---, Syntactically Correct `app.py`**


import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PIL import Image

# --- GitHub** with this version. I have removed the `nonlocal` keyword and rewritten the UI logic to use a function `return` value. This code is correct and will not produce a `SyntaxError`.

```python
# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Define Base Directory ---
BASE_DIR = os.path.dirname(os START OF FILE app.py (No Homepage, SyntaxError Corrected) ---

import streamlit as st
import os
.path.abspath(__file__))

# --- Load API Key ---
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    exceptimport json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PIL import Image

# --- Configuration ---
st.set_page_ (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

api_key = loadconfig(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Define Base Directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found.")
    st.stop()

# --- Initialize AI Client ---
@st.cache_resource --- Load API Key ---
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        
def get_cohere_client():
    return cohere.Client(api_key)

co = get_cohere_client()

# --- Helper Functions ---
def html_to_pdf(html_stringload_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found.")
    st.stop):
    return HTML(string=html_string).write_pdf()

def load_image(filename):
    ()

# --- Initialize AI Client ---
@st.cache_resource
def get_cohere_client():try:
        return Image.open(os.path.join(BASE_DIR, "assets", filename))
    except FileNotFoundError:
        st.error(f"Asset not found: Please ensure 'assets/{filename}' exists.")
    return cohere.Client(api_key)

co = get_cohere_client()

# --- Helper Functions ---
def html_to_pdf(html_string):
    return HTML(string=html_string
        return Image.new('RGB', (400, 300), color='red')

).write_pdf()

def load_image(filename):
    try:
        return Image.open(os.path.join(BASE_DIR, "assets", filename))
    except FileNotFoundError:
        st.error(# --- Load all images ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", load_image("corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", load_image("modern.png")),
    "Aesthetic": ("template_f"Asset not found: Please ensure 'assets/{filename}' exists in your GitHub repository.")
        return Image.new('RGB', (400, 300), color='red')

# --- Load all images into memory ONCE at the start ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7aesthetic.html", "#bcaaa4", load_image("aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", load_image("classic.png"))
}

# --- UI: Sidebar ---
with st.sidebar:
    st.title("📝 Your Information")
    st.markdown("Enter your details below to get started.")
    target_role = st.text_input("🎯 Target853", load_image("corporate.png")),
    "Modern": ("template_twocol.html", "#3498db", load_image("modern.png")),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", load_image("aesthetic.png")),
    "Classic": ("template.html", "#2c3e50", load_image("classic.png"))
}

# --- UI: Sidebar ---
with st.sidebar:
    st.title("📝 Your Information")
    st. Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science...")
    skills_input = st.text_area("🛠️ Skills", placeholder="Python, Streamlit, Data Analysis...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Describe your projects...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience if any")

# --- CSS Injection ---
st.markdown("""<style>...</style>""", unsafe_markdown("Enter your details below to get started.")
    target_role = st.text_input("🎯 Target Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science...")
    skills_input = stallow_html=True) # Your existing CSS

# --- Initialize Session State ---
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None

# --- Main App Logic ---

# STATE 1: Show the template selector by default
if not st.session_state.generation_output:
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume. Your details are on the left. 👈")
    st.divider()

    generation_.text_area("🛠️ Skills", placeholder="Python, Streamlit, Data Analysis...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Describe your projects...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience if any")

# --- CSS Injection (Simplified) ---
st.markdown("""
<style>
@keyframes fadeIn { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
.fade-in-section { animation: fadeIn 1s ease-in-out; }
.template-card { border: 1px solid #erequest = None

    # --- THIS IS THE CORRECTED FUNCTION ---
    def create_template_card(col, template_name):
        with col:
            filename, color, image_object = templates[template_0e0e0; padding: 1rem; border-radius: 8px; transition: all 0.3s ease-in-out; text-align: center; }
.template-card:hover { transform: translateY(-5px); box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08); }
</style>
""", unsafe_allow_htmlname]
            st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
            st.subheader(template_name)
            st.image(image_object, use_container_width=True)
            if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
                # RETURN the request data if button is clicked
                return {"template_filename": filename, "accent_color": color}
            st.markdown=True)

# --- Initialize Session State ---
if "generation_output" not in st.session_state:('</div>', unsafe_allow_html=True)
        # RETURN None if button is not clicked
        return None

    # Create the grid and capture the return values
    row1_col1, row1_col2 = st.columns(2)
    request1 = create_template_card(row1_col1, "Corporate
    st.session_state.generation_output = None

# --- Main App Body Logic ---
if st.session_state.generation_output:
    # --- STATE 2: Show Results ---
    st.success("🎉 Your professional resume is ready!")
    st.balloons()
    st.subheader("📄 PDF Preview")
    st.components.v1.html(st.session_state.generation_output["html"], height=")
    request2 = create_template_card(row1_col2, "Modern")
    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    request3 = create_template_card(row2_col1, "Aesthetic")
    request4 = create_template_card(row2_col2, "800, scrolling=True)
    st.download_button(label="📥 Download PDF Resume", data=st.session_state.generation_output["pdf"], file_name=st.session_state.generation_outputClassic")

    # Determine which button was clicked
    generation_request = request1 or request2 or request3 or request4

    # --- Generation Logic ---
    if generation_request:
        if not all([name, email, education_input, skills_input, projects_input]):
            st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
        else:
            with st.spinner("AI is crafting your signature resume..."):
                try:
                    user_data = {
                        "target_["filename"], mime="application/pdf")
    if st.button("✨ Create a New Resume"):
        st.session_state.generation_output = None
        st.rerun()
else:
    # --- STATE 1: Show Template Selector (Default View) ---
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume. Your details are on the left. 👈")
    st.divider()

    generation_request = None

    # --- THIS IS THE CORRECTED FUNCTION ---
    def create_template_card(col, template_name):
        with col:
            filename, color, image_object = templates[template_name]
            st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
            st.subheader(template_name)
            st.image(image_object, use_container_width=True)
            if st.button(f"Generate with {template_name} Stylerole": target_role, "name": name, "email": email,
                        "education_input": education_input, "skills_input": skills_input,
                        "projects_input": projects_input, "experience_input": experience_input
                    }
                    json_prompt = f"Generate a resume...DETAILS TO PARSE: {user_data}"
                    response = co.chat(model='command-r', message=", key=f"gen_{template_name}", use_container_width=True):
                # Return the request data when the button is clicked
                return {"template_filename": filename, "accent_color": color}
            st.markdown('</div>', unsafe_allow_html=True)
        return None

    row1_col1, row1_col2 = st.columns(2)
    request1 = create_template_card(row1_col1, "Corporate")
    request2 = create_template_card(row1_col2, "Modern")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    row2_col1, row2_col2 = st.columns(2)
    request3 = create_template_card(row2_col1, "Aesthetic")
    request4 = create_template_card(row2_col2, "Classic")

    # Check which request was returned
    generation_requestjson_prompt, temperature=0.2)
                    json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
                    resume_data = json.loads(json_string)
                    env = Environment(loader=FileSystemLoader(BASE_DIR))
                    template = env.get_template(generation_request["template_filename"])
                    html_out = template.render(resume_data, accent_color=generation_request["accent_color"])
                    pdf_bytes = html_to_pdf(html_out)

                    if pdf_bytes:
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
     = request1 or request2 or request3 or request4

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
    if st.button("✨ Create a New Resume"):
        st.session_state.generation_output = None
        st.rerun()
