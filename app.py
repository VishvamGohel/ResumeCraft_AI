# --- START OF DIAGNOSTIC app.py ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Basic Setup (Same as before) ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except:
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")
api_key = load_api_key()
if not api_key: st.error("❌ COHERE_API_KEY not found."); st.stop()
@st.cache_resource
def get_cohere_client(): return cohere.Client(api_key)
co = get_cohere_client()
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_CORPORATE_BASE64"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_MODERN_BASE64"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_AESTHETIC_BASE64"),
    "Classic": ("template.html", "#2c3e50", "PASTE_CLASSIC_BASE64")
}
with st.sidebar:
    st.title("📝 Your Information")
    target_role = st.text_input("🎯 Target Job Role", value="Data Analyst")
    name = st.text_input("👤 Full Name", value="John Doe")
    email = st.text_input("📧 Email", value="john.doe@email.com")
    education_input = st.text_area("🎓 Education", value="B.S. in Data Science, Tech University, 2024")
    skills_input = st.text_area("🛠️ Skills", value="Python, SQL, Tableau, Scikit-learn")
    projects_input = st.text_area("💼 Projects / Internships", value="Analyzed sales data to identify trends.")
    experience_input = st.text_area("🧾 Work Experience (Optional)")

# --- Main App Body ---
st.title("🎨 Choose Your Resume Style")
generation_request = None
row1_col1, row1_col2 = st.columns(2)
template_names = list(templates.keys())
def create_template_card(col, template_name):
    filename, color, image_data = templates[template_name]
    with col:
        st.subheader(template_name)
        st.markdown(f'<img src="{image_data}" ...>', unsafe_allow_html=True) # Truncated
        if st.button(f"Generate with {template_name}", key=f"gen_{template_name}"):
            return {"template_filename": filename, "accent_color": color}
    return None
request1 = create_template_card(row1_col1, template_names[0])
request2 = create_template_card(row1_col2, template_names[1])
generation_request = request1 or request2 # Simplified for brevity

# --- Generation Logic with Debugging ---
if generation_request:
    if not all([name, email, education_input, skills_input, projects_input]):
        st.toast("Please fill out your details.", icon="⚠️")
    else:
        with st.spinner("AI is thinking..."):
            user_data = {
                "target_role": target_role, "name": name, "email": email,
                "education_input": education_input, "skills_input": skills_input,
                "projects_input": projects_input, "experience_input": experience_input
            }
            # Use the original, simpler prompt for this test
            json_prompt = f"""
            Generate a resume in a structured JSON format based on these details.
            The JSON must have keys: "name", "email", "education", "skills", "projects", "experience".
            DETAILS TO PARSE: {user_data}
            """
            
            st.info("Sending the following prompt to the AI:")
            st.code(json_prompt, language="text")

            try:
                # Make the API call
                response = co.chat(
                    model='command-r',
                    message=json_prompt,
                    temperature=0.2
                )

                # --- THIS IS THE CRITICAL DEBUGGING STEP ---
                st.divider()
                st.subheader("🚨 AI Raw Response Received")
                st.write("Below is the exact text the AI sent back. We need to see why it's not valid JSON.")
                
                # We display the full response object and the raw text
                st.write("Full Response Object:")
                st.write(response)

                st.write("Raw `.text` attribute:")
                st.code(response.text, language='text')
                
                # Now we attempt to parse it, which will likely fail, but that's okay.
                st.divider()
                st.subheader("Attempting to Parse JSON...")
                try:
                    json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
                    if not json_string:
                        st.error("Parsing Failed: The AI response contained no '{' or '}' characters.")
                    else:
                        resume_data = json.loads(json_string)
                        st.success("✅ JSON Parsing Successful!")
                        st.json(resume_data)
                except Exception as e:
                    st.error(f"Parsing Failed with error: {e}")


            except Exception as e:
                st.error(f"❌ An error occurred during the API call itself: {e}")
