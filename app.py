# --- START OF FILE app.py (Stacked 2x2 Grid Layout) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Load API Keys and AI Client ---
load_dotenv("app.env")
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    st.error("❌ COHERE_API_KEY not found.")
    st.stop()
try:
    co = cohere.Client(api_key)
except Exception as e:
    st.error(f"❌ Error configuring Cohere client: {e}")
    st.stop()

# --- Helper Function ---
def html_to_pdf(html_string):
    return HTML(string=html_string).write_pdf()

# --- Templates Dictionary ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "assets/corporate.png"),
    "Modern": ("template_twocol.html", "#3498db", "assets/modern.png"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "assets/aesthetic.png"),
    "Classic": ("template.html", "#2c3e50", "assets/classic.png")
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

# --- CSS Injection ---
st.markdown("""
<style>
/* ... (Your existing CSS block remains unchanged here) ... */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');
@keyframes fadeIn { 0% { opacity: 0; transform: translateY(30px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%, 20%, 50%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-20px); } 60% { transform: translateY(-10px); } }
.fade-in-section { animation: fadeIn 1s ease-in-out; }
.hero-section { padding: 4rem 2rem; text-align: center; color: white; background: linear-gradient(45deg, #2c3e50, #4ca1af); border-radius: 16px; margin-bottom: 3rem; }
.brand-name { font-family: 'Poppins', sans-serif; font-size: 4.5rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: 1px; }
.brand-name span { font-style: italic; font-weight: 400; color: rgba(255, 255, 255, 0.8); margin-left: -8px; }
.hero-section p { font-family: 'Inter', sans-serif; font-size: 1.25rem; max-width: 600px; margin: 0 auto 2rem auto; color: rgba(255, 255, 255, 0.9); }
.scroll-arrow { font-size: 2rem; animation: bounce 2s infinite; }
.template-card { padding: 1rem; border-radius: 8px; transition: all 0.3s ease-in-out; }
.template-card:hover { transform: translateY(-5px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- Homepage / Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1 class="brand-name">ResumeCraft <span>AI</span></h1>
    <p>Your Career, Intelligently Designed.</p>
    <div class="scroll-arrow">↓</div>
</div>
""", unsafe_allow_html=True)

# --- Main App Body: The Template Selector ---
st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)

st.title("🎨 Choose Your Resume Style")
st.markdown("Select a template to generate your resume with that look and feel.")
st.write("") # Adds a little extra space

# --- Helper function to create a single template card ---
def create_template_card(template_name):
    filename, color, image_path = templates[template_name]
    st.markdown(f'<div class="template-card">', unsafe_allow_html=True)
    st.subheader(template_name)
    st.image(image_path, use_container_width=True)
    if st.button(f"Generate with {template_name} Style", key=f"gen_{template_name}", use_container_width=True):
        st.session_state.button_clicked = {"template_filename": filename, "accent_color": color}
    st.markdown('</div>', unsafe_allow_html=True)

# --- Create the 2x2 stacked grid ---
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    create_template_card("Corporate")
with row1_col2:
    create_template_card("Modern")

st.markdown("<br>", unsafe_allow_html=True) # Vertical spacer

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    create_template_card("Aesthetic")
with row2_col2:
    create_template_card("Classic")

st.markdown('</div>', unsafe_allow_html=True) # Close fade-in div

# --- Handle Button Clicks and Trigger Generation ---
if 'button_clicked' in st.session_state and st.session_state.button_clicked:
    if not all([name, email, education_input, skills_input, projects_input]):
        st.toast("Hey! Please fill out your details in the sidebar first. 👈", icon="⚠️")
    else:
        # All good, store the full request and rerun to show spinner and generate
        st.session_state.generation_request = st.session_state.button_clicked
        st.session_state.generation_request['user_data'] = {
            "target_role": target_role, "name": name, "email": email,
            "education_input": education_input, "skills_input": skills_input,
            "projects_input": projects_input, "experience_input": experience_input
        }
        st.rerun()
    # Clear the button click state
    st.session_state.button_clicked = None


# --- Generation Logic ---
if 'generation_request' in st.session_state and st.session_state.generation_request:
    request = st.session_state.generation_request
    with st.spinner("AI is crafting your signature resume..."):
        try:
            # ... (The rest of the generation logic is exactly the same as before) ...
            user_data = request['user_data']
            json_prompt = f"Generate a resume in structured JSON format for a person applying for the role of '{user_data['target_role'] if user_data['target_role'] else 'a student/entry-level position'}'. Tailor the descriptions. The JSON must have keys: 'name', 'email', 'education', 'skills', 'projects', 'experience', and 'target_role'. DETAILS TO PARSE: {user_data}"
            response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
            json_string = response.text[response.text.find('{'):response.text.rfind('}')+1]
            resume_data = json.loads(json_string)
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template(request["template_filename"])
            html_out = template.render(resume_data, accent_color=request["accent_color"])
            pdf_bytes = html_to_pdf(html_out)
            if pdf_bytes:
                st.success("🎉 Your professional resume is ready!")
                st.balloons()
                st.subheader("📄 PDF Preview")
                st.components.v1.html(html_out, height=800, scrolling=True)
                st.download_button(label="📥 Download PDF Resume", data=pdf_bytes, file_name=f"{user_data['name'].replace(' ', '_')}_Resume.pdf", mime="application/pdf")
        except json.JSONDecodeError:
            st.error("❌ AI Parsing Error: The AI returned an invalid format. Please try again.")
            st.text_area("AI Raw Output (for debugging)", response.text)
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
    # Clear the generation request so it doesn't run again on the next interaction
    st.session_state.generation_request = None