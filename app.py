# --- START OF FILE app.py (Final, Fully Corrected Version) ---

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

def validate_and_correct_data(data):
    """
    Checks the AI's output and robustly fixes common structural mistakes,
    ensuring the data perfectly matches the template's expectations.
    """
    # Ensure all top-level keys exist and default to empty lists if appropriate
    for key in ['education', 'skills', 'projects', 'experience']:
        if key not in data or not isinstance(data.get(key), list):
            data[key] = []

    # Safely check and correct the 'projects' structure
    if data['projects'] and isinstance(data['projects'][0], str):
        data['projects'] = [{"name": f"Project {i+1}", "details": [item]} for i, item in enumerate(data['projects'])]

    # Safely check and correct the 'education' structure
    if data['education'] and isinstance(data['education'][0], str):
        corrected_education = []
        for item in data['education']:
            parts = [p.strip() for p in item.split(',')]
            degree = parts[0] if len(parts) > 0 else "Degree"
            institution = parts[1] if len(parts) > 1 else "Institution"
            year = parts[2] if len(parts) > 2 else "Year"
            corrected_education.append({"degree": degree, "institution": institution, "year": year})
        data['education'] = corrected_education
        
    return data

# --- Find this function in your app.py ---

# --- CORRECTED: Function to display the footer with centered text ---
def show_footer():
    st.markdown("---") # Visual separator
    # The only change is adding a styled div around the <p> tag
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; color: #666; font-size: 0.9rem;">
        <p>
            <b>ResumeCraft AI</b> created by Vishvam — a B.Tech student passionate about AI and Web Development.
            <br>
            Connect with me on 
            <a href="mailto:vishvamgohel2007@gmail.com" style="color: #3498db; text-decoration: none; font-weight: bold;">Email</a> | 
            <a href="https://github.com/VishvamGohel" target="_blank" style="color: #3498db; text-decoration: none; font-weight: bold;">GitHub</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- Templates Dictionary ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853"),
    "Modern": ("template_twocol.html", "#3498db"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4"),
    "Classic": ("template.html", "#2c3e50")
}

# --- CSS for Both Pages ---
st.markdown("""
<style>
/* General Animation */
@keyframes fadeIn { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
.fade-in-section { animation: fadeIn 1s ease-in-out; }

/* Homepage Hero Section */
.hero-container {
    padding: 5rem 2rem;
    text-align: center;
    background: linear-gradient(45deg, #1a2a6c, #b21f1f, #fdbb2d);
    border-radius: 16px;
    color: white;
}
.hero-container h1 { font-size: 3.8rem; font-weight: 700; margin-bottom: 1rem; }
.hero-container p { font-size: 1.3rem; max-width: 600px; margin: 0 auto 2.5rem auto; color: rgba(255, 255, 255, 0.9); }
</style>
""", unsafe_allow_html=True)


# --- Main App Router ---
query_params = st.query_params
if query_params.get("page") == "builder":
    # --- BUILDER PAGE ---
    with st.sidebar:
        st.link_button("← Back to Home", "/", use_container_width=True)
        st.divider()
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
            generate_button = st.form_submit_button("🚀 Generate Resume", use_container_width=True)
    
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
                    - "education" MUST be a list of objects, each with "degree", "institution", and "year".
                    - "skills" MUST be a list of strings.
                    - "projects" MUST be a list of objects, each with "name" key (e.g., "Project Title") and "details" key (a list of strings).
                    - "experience" MUST be a list of objects.
                    If a section has no information, you MUST return an empty list [].
                    """
                    response = co.chat(model='command-r', message=json_prompt, temperature=0.1)
                    json_string = extract_json_from_text(response.text)
                    if not json_string:
                        st.error("AI Parsing Error. Please try again.")
                        st.text_area("AI Raw Output", response.text)
                    else:
                        resume_data = json.loads(json_string)
                        
                        # Use the robust validation function
                        corrected_data = validate_and_correct_data(resume_data)

                        template_filename = templates[template_name][0]
                        env = Environment(loader=FileSystemLoader(BASE_DIR))
                        template = env.get_template(template_filename)
                        html_out = template.render(corrected_data, accent_color=accent_color)
                        pdf_bytes = html_to_pdf(html_out)
                        if pdf_bytes:
                            st.success("🎉 Your professional resume is ready!")
                            st.balloons()
                            st.subheader("📄 PDF Preview")
                            st.components.v1.html(html_out, height=800, scrolling=True)
                            st.download_button(label="📥 Download PDF Resume", data=pdf_bytes, file_name=f"{name.replace(' ', '_')}_Resume.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")
                    if 'response' in locals():
                        st.text_area("AI Raw Output for Debugging", response.text)
    show_footer()     

else:
    # --- HOMEPAGE (Default View) ---
    st.markdown("""
    <div class="hero-container fade-in-section">
        <h1>The Only Resume Builder You'll Ever Need</h1>
        <p>Powered by AI, designed by experts. Create a resume that gets you hired, in minutes.</p>
        <a href="?page=builder" target="_self" style="display: inline-block; padding: 14px 32px; font-size: 1.1rem; font-weight: bold; color: #333; background-color: white; border-radius: 50px; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            Create My Resume
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    st.markdown('<div class="fade-in-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("✅ AI-Powered Content")
        st.write("Our AI writes professional, tailored content based on your input and target job.")
    with col2:
        st.subheader("🎨 Stunning Templates")
        st.write("Choose from a range of expert-designed templates proven to impress recruiters.")
    with col3:
        st.subheader("📥 Instant Download")
        st.write("Generate and download your resume as a pixel-perfect PDF, ready to send.")
    st.markdown('</div>', unsafe_allow_html=True)

    show_footer()
