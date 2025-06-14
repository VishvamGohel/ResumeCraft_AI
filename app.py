# --- START OF FILE app.py (Stable Sidebar Version) ---

import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="centered")
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

def extract_json_from_text(text):
    # This regex finds a JSON object within ```json ... ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match: return match.group(1)
    # Fallback to find any JSON object
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

# --- UI: Sidebar for All Inputs ---
with st.sidebar:
    st.title("📄 ResumeCraft AI")
    st.markdown("Fill in your details, choose a style, and generate your resume.")
    st.divider()

    # --- Step 1: Choose Style ---
    st.subheader("1. Choose Your Style")
    template_name = st.selectbox(
        "Select a template:",
        templates.keys()
    )
    
    # Intelligently get the default color for the chosen template
    default_color = templates[template_name][1]
    accent_color = st.color_picker("Select an accent color:", default_color)

    st.divider()

    # --- Step 2: Enter Information ---
    st.subheader("2. Enter Your Information")
    target_role = st.text_input("🎯 Target Job Role", placeholder="e.g., 'Data Analyst'")
    name = st.text_input("👤 Full Name")
    email = st.text_input("📧 Email")
    education_input = st.text_area("🎓 Education", placeholder="B.S. in Computer Science, Stanford, 2024")
    skills_input = st.text_area("🛠️ Skills", placeholder="Python, SQL, Data Visualization...")
    projects_input = st.text_area("💼 Projects / Internships", placeholder="Developed a sentiment analysis tool...")
    with st.expander("🧾 Work Experience (Optional)"):
        experience_input = st.text_area("Enter work experience")

    st.divider()

    # --- Step 3: Generate ---
    generate_button = st.button("🚀 Generate Resume", use_container_width=True)


# --- Main App Body ---
st.title("Your Generated Resume")
st.markdown("Your resume will appear here once you click the generate button in the sidebar.")

if generate_button:
    if not all([name, email, education_input, skills_input, projects_input]):
        st.warning("Please fill in all required fields in the sidebar.")
    else:
        with st.spinner("AI is crafting your signature resume..."):
            try:
                # Get the chosen template's filename
                template_filename = templates[template_name][0]
                
                user_data = {
                    "target_role": target_role, "name": name, "email": email,
                    "education_input": education_input, "skills_input": skills_input,
                    "projects_input": projects_input, "experience_input": experience_input
                }

                # --- A very robust prompt to get the correct data structure ---
                json_prompt = f"""
                Generate a resume as a JSON object based on these details: {user_data}.
                The JSON object MUST have these top-level keys: "name", "email", "profile_summary", "education", "skills", "projects", "experience".
                - "profile_summary": A 1-2 sentence professional summary tailored to the target role.
                - "education": ALWAYS a list of objects. Each object MUST have "degree", "institution", and "year".
                - "skills": ALWAYS a list of strings.
                - "projects": ALWAYS a list of objects. Each object MUST have "name" and "details" (a list of strings).
                - "experience": ALWAYS a list of objects. Each object MUST have "title", "company", "duration", and "details" (a list of strings).
                If a section has no information, you MUST return an empty list [], for example: "experience": []. Do not omit any keys.
                Wrap the entire response in a single ```json ... ``` block.
                """
                
                response = co.chat(model='command-r', message=json_prompt, temperature=0.1)
                
                json_string = extract_json_from_text(response.text)
                
                if not json_string:
                    st.error("AI Parsing Error: The AI did not return a parsable JSON object. Please try again.")
                    st.text_area("AI Raw Output", response.text)
                else:
                    resume_data = json.loads(json_string)
                    
                    # Simple check to ensure data is not empty before rendering
                    if not resume_data.get("name"):
                        st.error("AI Data Error: The generated data is empty. The AI might be having trouble. Please try again.")
                        st.json(resume_data)
                    else:
                        env = Environment(loader=FileSystemLoader(BASE_DIR))
                        template = env.get_template(template_filename)
                        
                        # Pass the accent color to the template
                        html_out = template.render(resume_data, accent_color=accent_color)
                        
                        pdf_bytes = html_to_pdf(html_out)

                        if pdf_bytes:
                            st.success("🎉 Your professional resume is ready!")
                            st.balloons()
                            
                            st.subheader("📄 PDF Preview")
                            st.components.v1.html(html_out, height=800, scrolling=True)

                            st.download_button(
                                label="📥 Download PDF Resume",
                                data=pdf_bytes,
                                file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                                mime="application/pdf"
                            )

            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {e}")
                if 'response' in locals():
                    st.text_area("AI Raw Output for Debugging", response.text, key="error_debug_final")
