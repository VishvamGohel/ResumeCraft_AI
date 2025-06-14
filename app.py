# --- START OF FILE app.py (with st.form for a better mobile UX) ---

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

# --- Initialize AI Client ---
@st.cache_resource
def get_cohere_client():
    return cohere.Client(api_key)
co = get_cohere_client()

# --- Helper Functions ---
def html_to_pdf(html_string): return HTML(string=html_string).write_pdf()
def extract_json_from_text(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match: return match.group(1)
    return None

# --- Templates Dictionary ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853"),
    "Modern": ("template_twocol.html", "#3498db"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4"),
    "Classic": ("template.html", "#2c3e50")
}

# --- CSS for Both Pages ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Your existing CSS block

# --- Main App Router ---
query_params = st.query_params
if query_params.get("page") == "builder":
    # --- BUILDER PAGE ---
    
    # --- THIS IS THE KEY CHANGE: Wrap the sidebar in a form ---
    with st.sidebar:
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

            # The form has its own submit button
            generate_button = st.form_submit_button("🚀 Generate Resume", use_container_width=True)

    # --- Generation Logic (remains outside the form) ---
    st.title("Your Generated Resume")
    st.markdown("Your resume will appear here once you click the generate button.")
    
    if generate_button:
        if not all([name, email, education_input, skills_input, projects_input]):
            st.warning("Please fill in all required fields in the sidebar.")
        else:
            with st.spinner("AI is crafting your signature resume..."):
                try:
                    user_data = { "target_role": target_role, "name": name, "email": email, "education_input": education_input, "skills_input": skills_input, "projects_input": projects_input, "experience_input": experience_input }
                    json_prompt = f"""
                    Generate a resume as a JSON object based on these details: {user_data}.
                    The JSON object MUST have keys: "name", "email", "profile_summary", "education", "skills", "projects", "experience".
                    If a section has no information, you MUST return an empty list [].
                    """
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.1)
                    json_string = extract_json_from_text(response.text)
                    if not json_string:
                        st.error("AI Parsing Error. Please try again.")
                        st.text_area("AI Raw Output", response.text)
                    else:
                        resume_data = json.loads(json_string)
                        template_filename = templates[template_name][0]
                        env = Environment(loader=FileSystemLoader(BASE_DIR))
                        template = env.get_template(template_filename)
                        html_out = template.render(resume_data, accent_color=accent_color)
                        pdf_bytes = html_to_pdf(html_out)
                        if pdf_bytes:
                            st.success("🎉 Your professional resume is ready!")
                            st.balloons()
                            st.subheader("📄 PDF Preview")
                            st.components.v1.html(html_out, height=800, scrolling=True)
                            st.download_button(label="📥 Download PDF Resume", data=pdf_bytes, file_name=f"{name.replace(' ', '_')}_Resume.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

else:
    # --- HOMEPAGE (Default View) ---
    # ... (Your homepage markdown remains unchanged) ...
    st.markdown("""<div class="hero-container fade-in-section">...</div>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="fade-in-section">...</div>', unsafe_allow_html=True)
