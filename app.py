# --- START OF FILE app.py (Robust JSON Parsing) ---

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Configuration & Setup (No changes needed here) ---
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ... (rest of setup and helper functions are the same)
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except:
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")
api_key = load_api_key()
# ... (rest of setup is fine)
co = cohere.Client(api_key)
def html_to_pdf(html_string): return HTML(string=html_string).write_pdf()

templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_CORPORATE_BASE64"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_MODERN_BASE64"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_AESTHETIC_BASE64"),
    "Classic": ("template.html", "#2c3e50", "PASTE_CLASSIC_BASE64")
}

if "generation_output" not in st.session_state:
    st.session_state.generation_output = None

# --- UI: Sidebar (No changes needed) ---
# ... (your sidebar code is fine)
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

# --- CSS & Homepage (No changes needed) ---
# ... (your CSS and homepage display logic is fine)
st.markdown("""<style>...</style>""", unsafe_allow_html=True)
if not st.session_state.generation_output:
    st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True)
    st.title("🎨 Choose Your Resume Style")
    # ... (rest of your card layout code is fine)
else:
    # ... (your results display code is fine)


# --- THIS IS THE KEY CHANGE: THE GENERATION LOGIC ---

# The following code should replace the "Generation Logic" block in your app
if 'generation_request' not in st.session_state:
    st.session_state.generation_request = None

# This part of the code that creates the cards and sets the request is fine
# We will just show the final, correct version of the whole file at the end

# Let's focus on the part that runs *after* a button is clicked
# Here is the complete, final app.py for clarity and correctness.

# --- START OF FULL CORRECTED APP.PY ---
# (Re-pasting the whole thing to ensure no confusion)

import streamlit as st
import os
import json
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

api_key = load_api_key()
if not api_key: st.error("❌ COHERE_API_KEY not found."); st.stop()

@st.cache_resource
def get_cohere_client(): return cohere.Client(api_key)
co = get_cohere_client()

def html_to_pdf(html_string): return HTML(string=html_string).write_pdf()

templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853", "PASTE_CORPORATE_BASE64"),
    "Modern": ("template_twocol.html", "#3498db", "PASTE_MODERN_BASE64"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4", "PASTE_AESTHETIC_BASE64"),
    "Classic": ("template.html", "#2c3e50", "PASTE_CLASSIC_BASE64")
}

if "generation_output" not in st.session_state: st.session_state.generation_output = None

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

st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Your CSS here

if st.session_state.generation_output:
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
    st.markdown("""<div class="hero-section">...</div>""", unsafe_allow_html=True) # Your hero HTML here
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
                    
                    # --- NEW: Define the structure for the AI ---
                    tool_parameters = {
                        "name": {"type": "string", "description": "Full name of the person."},
                        "email": {"type": "string", "description": "Email address."},
                        "education": {
                            "type": "list", "description": "List of educational qualifications.",
                            "items": {"type": "object", "properties": {
                                "degree": {"type": "string"}, "institution": {"type": "string"}, "year": {"type": "string"}
                            }}
                        },
                        "skills": {"type": "list", "items": {"type": "string"}},
                        "projects": {
                            "type": "list", "items": {"type": "object", "properties": {
                                "name": {"type": "string"}, "details": {"type": "list", "items": {"type": "string"}}
                            }}
                        },
                        "experience": {
                            "type": "list", "items": {"type": "object", "properties": {
                                "title": {"type": "string"}, "company": {"type": "string"},
                                "duration": {"type": "string"}, "details": {"type": "list", "items": {"type": "string"}}
                            }}
                        },
                        "target_role": {"type": "string"},
                        "profile_summary": {"type": "string", "description": "A 1-2 sentence professional summary."}
                    }
                    
                    # --- NEW: Use Tool Use mode for reliable JSON ---
                    response = co.chat(
                        model='command-r',
                        message=f"Generate a resume based on these details: {user_data}",
                        tools=[{"name": "json_output", "description": "Function to output structured resume data.", "parameter_definitions": tool_parameters}],
                        tool_results=[{}] # Force the model to use the tool
                    )

                    # --- NEW: Robustly extract the JSON data ---
                    resume_data = None
                    if response.tool_calls and response.tool_calls[0].name == "json_output":
                        resume_data = response.tool_calls[0].parameters

                    if not resume_data:
                        raise ValueError("AI failed to generate valid JSON data.")

                    # --- The rest of the logic is the same ---
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
                    # Also show the raw AI response if it exists, for debugging
                    if 'response' in locals():
                        st.text_area("AI Raw Output (for debugging)", response.text)
