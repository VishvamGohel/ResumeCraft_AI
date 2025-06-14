# --- START OF FILE app.py (FINAL, CORRECTED DATA VALIDATION) ---

import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration & Setup (No changes) ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
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

@st.cache_resource
def get_cohere_client():
    return cohere.Client(api_key)

co = get_cohere_client()

def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

def extract_json_from_text(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match: return match.group(1)
    return None

# --- THIS IS THE CORRECTED, ROBUST VALIDATION FUNCTION ---
def validate_and_correct_data(data):
    # Ensure keys exist and are lists
    for key in ['education', 'skills', 'projects', 'experience']:
        if key not in data or not isinstance(data[key], list):
            data[key] = [] # If missing or wrong type, default to an empty list

    # If education is a list of strings, convert to list of objects
    if data['education'] and isinstance(data['education'][0], str):
        data['education'] = [{"degree": edu, "institution": "", "year": ""} for edu in data['education']]

    # If projects is a list of strings, convert to list of objects
    if data['projects'] and isinstance(data['projects'][0], str):
        data['projects'] = [{"name": proj, "details": []} for proj in data['projects']]
        
    # Add a default profile summary if missing
    if 'profile_summary' not in data:
        data['profile_summary'] = "A highly motivated professional seeking a new opportunity."
        
    return data

# --- Templates Dictionary & Session State Init (No changes) ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853"),
    # ... add your other templates here ...
}
if "generation_output" not in st.session_state:
    st.session_state.generation_output = None


# --- Sidebar UI (No changes) ---
with st.sidebar:
    st.title("📝 Your Information")
    # ... (all your st.text_input fields) ...
    target_role = st.text_input("🎯 Target Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science...")
    skills_input = st.text_area("🛠️ Skills", placeholder="Python, Streamlit...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Describe your projects...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience")

# --- Main App Body ---
if st.session_state.generation_output:
    # --- Results Page ---
    st.success("🎉 Your professional resume is ready!")
    st.balloons()
    st.subheader("📄 PDF Preview")
    st.components.v1.html(st.session_state.generation_output["html"], height=800, scrolling=True)
    st.download_button(label="📥 Download PDF Resume", data=st.session_state.generation_output["pdf"], file_name=st.session_state.generation_output["filename"], mime="application/pdf")
    if st.button("✨ Create a New Resume"):
        st.session_state.generation_output = None
        st.rerun()
else:
    # --- Homepage ---
    st.title("🎨 Choose Your Resume Style")
    st.markdown("Select a template to generate your resume.")
    
    generation_request = None
    
    # We only have one template for this test, but you can add the others back
    template_name = "Corporate"
    filename, color = templates[template_name]
    if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
        generation_request = {"template_filename": filename, "accent_color": color}
            
    if generation_request:
        if not all([name, email, education_input, skills_input, projects_input]):
            st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
        else:
            with st.spinner("AI is crafting your signature resume..."):
                try:
                    user_data = { "target_role": target_role, "name": name, "email": email, "education_input": education_input, "skills_input": skills_input, "projects_input": projects_input, "experience_input": experience_input }
                    
                    # --- NEW: A MUCH MORE ROBUST PROMPT ---
                    json_prompt = f"""
                    Generate a resume in a structured JSON format based on these details.
                    The JSON object MUST have these top-level keys: "name", "email", "profile_summary", "education", "skills", "projects", "experience".
                    - "education": ALWAYS a list of objects. Each object MUST have "degree", "institution", and "year" keys.
                    - "skills": ALWAYS a list of strings.
                    - "projects": ALWAYS a list of objects. Each object MUST have a "name" key and a "details" key (which is a list of strings).
                    - "experience": ALWAYS a list of objects. Each object MUST have "title", "company", "duration", and "details" (a list of strings).
                    If a section has no information, return an empty list, for example: "experience": [].
                    Do not omit any keys.
                    Wrap the entire response in a single ```json ... ``` block.
                    DETAILS TO PARSE: {user_data}
                    """
                    
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.1)
                    json_string = extract_json_from_text(response.text)
                    
                    if not json_string:
                        st.error("❌ AI Parsing Error: The AI did not return a valid JSON structure.")
                        st.text_area("AI Raw Output for Debugging", response.text)
                    else:
                        resume_data = json.loads(json_string)
                        
                        # --- USE THE CORRECTED VALIDATION FUNCTION ---
                        corrected_data = validate_and_correct_data(resume_data)
                        
                        env = Environment(loader=FileSystemLoader(BASE_DIR))
                        template = env.get_template(generation_request["template_filename"])
                        html_out = template.render(corrected_data)
                        
                        pdf_bytes = html_to_pdf(html_out)

                        if pdf_bytes:
                            st.session_state.generation_output = { "pdf": pdf_bytes, "html": html_out, "filename": f"{user_data['name'].replace(' ', '_')}_Resume.pdf" }
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")
                    # Include the raw response in the error message for debugging
                    if 'response' in locals():
                        st.text_area("AI Raw Output for Debugging", response.text, key="error_debug")
