# --- START OF FILE app.py (Simple & Stable Version) ---

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
    except:
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
    if match:
        return match.group(1)
    # Fallback to find any JSON object if the markdown is missing
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match:
        return match.group(1)
    return None

# --- Sidebar UI ---
with st.sidebar:
    st.title("📝 ResumeCraft AI")
    st.markdown("Enter your details below.")
    target_role = st.text_input("🎯 Target Job Role", value="Software Engineer")
    name = st.text_input("👤 Full Name", value="Jane Doe")
    email = st.text_input("📧 Email", value="jane.doe@example.com")
    education_input = st.text_area("🎓 Education", value="M.S. in Computer Science, Stanford University, 2024")
    skills_input = st.text_area("🛠️ Skills", value="Python, Java, Cloud Computing, System Design")
    projects_input = st.text_area("💼 Projects", value="Developed a full-stack web application for task management using React and Node.js.")
    experience_input = st.text_area("🧾 Work Experience (Optional)", value="Software Engineering Intern at Tech Corp (Summer 2023) - Worked on the backend services for the main product.")

    generate_button = st.button("🚀 Generate Resume", use_container_width=True)

# --- Main App Body ---
st.title("Your Generated Resume")
st.markdown("Your resume will appear here once you click the generate button.")

if generate_button:
    if not all([name, email, education_input, skills_input, projects_input]):
        st.warning("Please fill in all required fields in the sidebar.")
    else:
        with st.spinner("AI is crafting your resume..."):
            try:
                user_data = {
                    "target_role": target_role, "name": name, "email": email,
                    "education_input": education_input, "skills_input": skills_input,
                    "projects_input": projects_input, "experience_input": experience_input
                }
                
                # A very direct and structured prompt
                json_prompt = f"""
                Create a resume as a JSON object. The JSON object must have keys: "name", "email", "profile_summary", "education", "skills", "projects", "experience".
                - The value for "education" must be a list of objects, each with "degree", "institution", and "year".
                - The value for "skills" must be a list of strings.
                - The value for "projects" must be a list of objects, each with "name" and "details" (which is a list of strings).
                - The value for "experience" must be a list of objects, each with "title", "company", "duration", and "details" (a list of strings).
                If a section is empty, provide an empty list [].
                Based on these details: {user_data}
                """
                
                response = co.chat(model='command-r', message=json_prompt, temperature=0.1)
                
                json_string = extract_json_from_text(response.text)
                
                if not json_string:
                    st.error("AI Parsing Error: The AI did not return a parsable JSON object. Please try again.")
                    st.text_area("AI Raw Output", response.text)
                else:
                    resume_data = json.loads(json_string)
                    
                    # Ensure all keys exist before passing to template
                    for key in ['name', 'email', 'profile_summary', 'education', 'skills', 'projects', 'experience']:
                        if key not in resume_data:
                            resume_data[key] = [] if isinstance(resume_data.get(key), list) else ""

                    env = Environment(loader=FileSystemLoader(BASE_DIR))
                    template = env.get_template("template_oldmoney.html") # Using the most stable template
                    
                    html_out = template.render(resume_data, accent_color="#8c7853")
                    
                    pdf_bytes = html_to_pdf(html_out)

                    if pdf_bytes:
                        st.success("🎉 Your resume is ready!")
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
                    st.text_area("AI Raw Output for Debugging", response.text, key="error_debug_2")
