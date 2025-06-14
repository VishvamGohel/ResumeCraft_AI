# --- START OF FILE app.py (Final Version with Smart JSON Extraction) ---

import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Load API Key ---
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

# --- Initialize AI Client ---
@st.cache_resource
def get_cohere_client():
    return cohere.Client(api_key)

co = get_cohere_client()

# --- Helper Functions ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

# --- NEW: Smart JSON Extraction Function ---
def extract_json_from_text(text):
    """
    Finds and extracts a JSON object from a string that might be wrapped
    in markdown code blocks (```json ... ```).
    """
    # Regex to find JSON block wrapped in ```json
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Fallback for JSON not in a markdown block
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match:
        return match.group(1)
        
    return None # Return None if no JSON object is found

# --- Embedded Image Data ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_CORPORATE_BASE64"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_MODERN_BASE64"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_AESTHETIC_BASE64"),
    "Classic": ("template.html", "#2c3e50", "PASTE_CLASSIC_BASE64")
}

# --- Session State ---
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None

# --- UI: Sidebar ---
with st.sidebar:
    st.title("📝 Your Information")
    st.markdown("Enter your details below.")
    target_role = st.text_input("🎯 Target Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science...")
    skills_input = st.text_area("🛠️ Skills", placeholder="Python, Streamlit...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Describe your projects...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience")

# --- CSS & Homepage ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

if st.session_state.generation_output:
    # --- Results Page ---
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
else:
    # --- Main Homepage ---
    st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume.")
    st.write("") 

    generation_request = None

    def create_template_card(col, template_name):
        filename, color, image_data = templates[template_name]
        with col:
            st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
            st.subheader(template_name)
            st.markdown(f'<img src="{image_data}" alt="{template_name} preview" style="width:100%; border-radius: 8px;">', unsafe_allow_html=True)
            if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
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
    generation_request = request1 or request2 or request3 or request4

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
                    json_prompt = f"""
                    Generate a resume in a structured JSON format based on these details.
                    The JSON must have keys: "name", "email", "education", "skills", "projects", "experience".
                    Ensure the entire output is a single JSON object wrapped in ```json ... ```.
                    DETAILS TO PARSE: {user_data}
                    """
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
                    
                    # --- USE THE NEW, SMART EXTRACTION METHOD ---
                    json_string = extract_json_from_text(response.text)
                    
                    if not json_string:
                        st.error("❌ AI Parsing Error: The AI did not return a valid JSON structure. Please try again.")
                        st.text_area("AI Raw Output for Debugging", response.text)
                    else:
                        resume_data = json.loads(json_string)
                        env = Environment(loader=FileSystemLoader(BASE_DIR))
                        template = env.get_template(generation_request["template_filename"])
                        html_out = template.render(resume_data, accent_color=generation_request["accent_color"])
                        pdf_bytes = html_to_pdf(html_out)

                        if pdf_bytes:
                            st.session_state.generation_output = {
                                "pdf": pdf_bytes, "html": html_out,
                                "filename": f"{user_data['name'].replace(' ', '_')}_Resume.pdf"
                            }
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")
