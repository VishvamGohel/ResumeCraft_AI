# --- START OF FILE app.py (Final Version with Styled Feedback) ---

import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
import cohere
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import copy
from datetime import datetime

# --- Correct imports for gspread ---
import gspread
from google.oauth2.service_account import Credentials

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="ResumeCraft AI", page_icon="✨", layout="wide")

# --- Helper Functions ---
@st.cache_data
def load_api_key():
    try: return st.secrets["COHERE_API_KEY"]
    except (KeyError, FileNotFoundError):
        load_dotenv(os.path.join(BASE_DIR, "app.env"))
        return os.getenv("COHERE_API_KEY")

@st.cache_resource
def get_cohere_client(_api_key): return cohere.Client(_api_key)

def html_to_pdf(html_string): return HTML(string=html_string).write_pdf()

def extract_json_from_text(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match: return match.group(1)
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match: return match.group(1)
    st.warning("Could not find a JSON block in the AI's response. Displaying raw text.")
    st.code(text)
    return None

# --- UI Components (Header, Footer, Feedback) ---
def show_persistent_header():
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
            .custom-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .custom-header a {
                font-family: 'Montserrat', sans-serif;
                font-size: 2.5rem;
                font-weight: 700;
                text-decoration: none;
            }
            body.theme-light .custom-header a { color: #262730; }
            body.theme-dark .custom-header a { color: #FAFAFA; }
        </style>
        <div class="custom-header">
            <a href="/?page=home" target="_self">ResumeCraft AI</a>
        </div>
    """, unsafe_allow_html=True)

# --- REVISED: display_feedback_dialog function with custom styling ---
def display_feedback_dialog():
    @st.dialog("Share Your Feedback")
    def feedback_form():
        # --- NEW: Inject CSS for our custom question labels ---
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            .feedback-question-label {
                font-family: 'Poppins', sans-serif; /* Use the new font */
                font-weight: 600; /* Bolder weight */
                font-size: 1.1rem; /* Slightly larger size */
                margin-bottom: 0.5rem; /* Add some space below the question */
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.write("Your resume is ready! Please take a moment to help us improve.")
        st.divider()

        # --- NEW: Use st.markdown with our custom class for the label ---
        st.markdown('<p class="feedback-question-label">How clear were the instructions and steps?</p>', unsafe_allow_html=True)
        clarity_rating = st.slider(
            "How clear were the instructions and steps?", # This label is now hidden
            min_value=1, max_value=5, value=4,
            help="1 = Very Confusing, 5 = Very Clear",
            label_visibility="collapsed" # --- THIS HIDES THE DEFAULT LABEL ---
        )
        
        st.markdown('<p class="feedback-question-label">How happy are you with your final resume PDF?</p>', unsafe_allow_html=True)
        satisfaction_rating = st.slider(
            "How happy are you with your final resume PDF?",
            min_value=1, max_value=5, value=4,
            help="1 = Very Unhappy, 5 = Very Happy",
            label_visibility="collapsed"
        )

        st.markdown('<p class="feedback-question-label">What was your favorite feature?</p>', unsafe_allow_html=True)
        favorite_feature = st.selectbox(
            "What was your favorite feature?",
            options=[
                "The AI-powered content enhancement",
                "The 'Tailor to Job Description' option",
                "The selection of templates",
                "The overall speed and ease-of-use",
                "Other"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown('<p class="feedback-question-label">Would you recommend ResumeCraft AI to a friend?</p>', unsafe_allow_html=True)
        would_recommend = st.radio(
            "Would you recommend ResumeCraft AI to a friend?",
            options=["Yes", "No"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown('<p class="feedback-question-label">What is one thing we could improve? (optional)</p>', unsafe_allow_html=True)
        improvement_suggestion = st.text_area(
            "What is one thing we could improve? (optional)",
            label_visibility="collapsed"
            )

        st.markdown("<br>", unsafe_allow_html=True) # Add some space before the button

        if st.button("Submit Feedback", use_container_width=True, type="primary"):
            try:
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_info(
                    st.secrets["gspread_credentials"], scopes=scopes
                )
                client = gspread.authorize(creds)
                
                sheet = client.open("ResumeCraft-Feedback").worksheet("Sheet1") # Remember to use your real sheet name
                
                new_row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    clarity_rating,
                    satisfaction_rating,
                    favorite_feature,
                    would_recommend,
                    improvement_suggestion
                ]
                
                sheet.append_row(new_row)
                st.toast("Thank you!", icon="🎉")
                
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("Feedback system error: The Google Sheet was not found. Please check the sheet name.")
            except gspread.exceptions.APIError:
                st.error("Feedback system error: A Google API error occurred. Likely a permissions issue.")
            except Exception as e:
                st.error(f"Could not submit feedback. Error: {e}")
            
            st.rerun()

    feedback_form()


def show_footer():
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 1rem; color: #666; font-size: 0.9rem;">
        <p>
            <b>ResumeCraft AI</b> created by Vishvam — a B.Tech student passionate about AI and Web Development.
            <br>
            Connect with me on
            <a href="mailto:your.email@gmail.com" style="color: #3498db; text-decoration: none; font-weight: bold;">Email</a> |
            <a href="https://github.com/your-github-username" target="_blank" style="color: #3498db; text-decoration: none; font-weight: bold;">GitHub</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- App Initialization ---
api_key = load_api_key()
if not api_key:
    st.error("❌ COHERE_API_KEY not found. Please set it in your environment or Streamlit secrets.")
    st.stop()
co = get_cohere_client(api_key)

show_persistent_header()

# --- Data Dictionaries, State, and Routing ---
templates = {
    "Corporate": ("template_oldmoney.html", "#8c7853"), "Modern": ("template_twocol.html", "#3498db"),
    "Aesthetic": ("template_aesthetic.html", "#bcaaa4"), "Classic": ("template.html", "#2c3e50")
}
sample_data = {
    "name": "Alex Taylor", "email": "alex.taylor@email.com",
    "profile_summary": "Innovative Computer Science graduate passionate about developing scalable web applications and working with cutting-edge AI technologies.",
    "education": [{"degree": "B.S. in Computer Science", "institution": "University of Technology", "year": "2024"}],
    "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "AWS", "Machine Learning"],
    "projects": [{"name": "AI-Powered Task Manager", "details": ["Developed a full-stack web app that uses natural language processing to categorize and prioritize tasks.", "Built a RESTful API with Node.js and Express for data handling."]}],
    "experience": [{"title": "Software Development Intern", "company": "Innovatech Solutions", "duration": "Summer 2023", "details": ["Contributed to the development of a client-facing analytics dashboard, increasing user engagement by 15%."]}]
}

if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'resume_data' not in st.session_state: st.session_state.resume_data = {}
if 'feedback_triggered' not in st.session_state: st.session_state.feedback_triggered = False

page = st.query_params.get("page", "home")

# --- Page Rendering Logic ---
if page == "builder":
    st.markdown("### **Step 1:** Your Details")
    st.caption("Fill in your information below. The AI will automatically enhance and structure it for you.")
    st.divider()

    form_col, _ = st.columns([2, 1])
    with form_col:
        ud = st.session_state.user_data
        target_role = st.text_input("🎯 **Target Job Role** (e.g., 'Software Engineer')", ud.get("target_role", ""))
        name = st.text_input("👤 Full Name", ud.get("name", ""))
        email = st.text_input("📧 Email", ud.get("email", ""))

        with st.expander("🔗 **Tailor to a Job Description (Recommended)**"):
            job_description = st.text_area("Paste the job description here...", ud.get("job_description", ""), height=150)

        st.subheader("Your Content")
        education_input = st.text_area("🎓 Education (e.g., 'B.S. in Computer Science - University of Tech - 2024')", ud.get("education_input", ""), height=100)
        skills_input = st.text_area("🛠️ Skills (Comma-separated, e.g., 'Python, JavaScript, React')", ud.get("skills_input", ""), height=100)
        projects_input = st.text_area("💼 Projects / Internships", ud.get("projects_input", ""), height=150)

        with st.expander("🧾 Work Experience (Optional)"):
            experience_input = st.text_area("Work experience details", ud.get("experience_input", ""))

        st.divider()
        if st.button("Next: Generate & Review →", use_container_width=True, type="primary"):
            if not all([name, email, education_input, skills_input, projects_input]):
                st.warning("Please fill in all required fields.")
            else:
                st.session_state.user_data = {
                    "target_role": target_role, "name": name, "email": email,
                    "job_description": job_description, "education_input": education_input,
                    "skills_input": skills_input, "projects_input": projects_input,
                    "experience_input": experience_input
                }
                with st.spinner("AI is crafting and enhancing your resume..."):
                    try:
                        user_details_str = json.dumps(st.session_state.user_data, indent=2)
                        json_prompt = f"""
                        Based on the user's details, generate a resume in a clean JSON format.

                        **Instructions:**
                        1.  Create a concise, professional `profile_summary` (2-3 sentences) tailored to the `target_role` and `job_description` if provided.
                        2.  For the `projects` and `experience` sections, first **enhance** the user-provided bullet points in the `details` field. Rewrite them to be more professional using strong action verbs and quantifying results.
                        3.  After enhancing, parse the content into the specified JSON structure.
                        4.  Parse `education_input` into a list of objects, each with `degree`, `institution`, and `year`.
                        5.  Parse `skills_input` into a simple list of strings.
                        6.  IMPORTANT: The order of entries in the 'projects' and 'experience' arrays MUST be preserved from the user's input. Do not reorder them.
                        7.  The final output MUST be a single JSON object enclosed in ```json ... ```.

                        **JSON Schema to follow:**
                        {{"name": "string", "email": "string", "profile_summary": "string", "education": [{{"degree": "string", "institution": "string", "year": "string"}}], "skills": ["string", "string", ...], "projects": [{{"name": "string", "details": ["string", "string", ...]}}], "experience": [{{"title": "string", "company": "string", "duration": "string", "details": ["string", ...]}}]}}

                        **User's Details:**
                        {user_details_str}
                        """
                        response = co.chat(model='command-r', message=json_prompt, temperature=0.2)
                        json_string = extract_json_from_text(response.text)

                        if not json_string:
                            st.error("AI failed to generate valid JSON. Please try adjusting your input.")
                        else:
                            st.session_state.resume_data = json.loads(json_string)
                            st.query_params["page"] = "review"
                            st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred during AI generation: {e}")
    show_footer()

elif page == "review":
    st.markdown("### **Step 2:** Review & Edit")
    st.caption("Your data has been enhanced by AI. Review and edit below as needed.")
    st.link_button("← Back to Edit Details", "?page=builder")
    st.divider()

    if 'resume_data' not in st.session_state or not st.session_state.resume_data:
        st.warning("No resume data found. Please go back to the builder page.")
        st.link_button("Go to Builder", "?page=builder")
    else:
        edited_data = copy.deepcopy(st.session_state.resume_data)
        edited_data['name'] = st.text_input("Full Name", value=edited_data.get('name', ''))
        edited_data['email'] = st.text_input("Email", value=edited_data.get('email', ''))
        edited_data['profile_summary'] = st.text_area("Profile Summary", value=edited_data.get('profile_summary', ''), height=120)
        st.subheader("Skills")
        skills_string = "\n".join(edited_data.get('skills', []))
        edited_skills_string = st.text_area("Skills (one skill per line)", value=skills_string, height=150)
        st.subheader("Education")
        for i, edu in enumerate(edited_data.get('education', [])):
            with st.container(border=True):
                edu['degree'] = st.text_input(f"Degree {i+1}", value=edu.get('degree', ''), key=f"edu_deg_{i}")
                edu['institution'] = st.text_input(f"Institution {i+1}", value=edu.get('institution', ''), key=f"edu_inst_{i}")
                edu['year'] = st.text_input(f"Year {i+1}", value=edu.get('year', ''), key=f"edu_year_{i}")
        st.subheader("Projects")
        for i, proj in enumerate(edited_data.get('projects', [])):
            with st.container(border=True):
                proj['name'] = st.text_input(f"Project Name {i+1}", value=proj.get('name', ''), key=f"proj_name_{i}")
                details_string = "\n".join(proj.get('details', []))
                edited_details_string = st.text_area(f"Project Details (one bullet point per line)", value=details_string, key=f"proj_details_{i}")
                proj['details'] = edited_details_string
        st.subheader("Experience")
        for i, exp in enumerate(edited_data.get('experience', [])):
             with st.container(border=True):
                exp['title'] = st.text_input(f"Job Title {i+1}", value=exp.get('title', ''), key=f"exp_title_{i}")
                exp['company'] = st.text_input(f"Company {i+1}", value=exp.get('company', ''), key=f"exp_comp_{i}")
                exp['duration'] = st.text_input(f"Duration {i+1}", value=exp.get('duration', ''), key=f"exp_dur_{i}")
                exp_details_string = "\n".join(exp.get('details', []))
                edited_exp_details_string = st.text_area(f"Job Details (one bullet point per line)", value=exp_details_string, key=f"exp_details_{i}")
                exp['details'] = edited_exp_details_string
        if st.button("Save & Choose Template →", use_container_width=True, type="primary"):
            edited_data['skills'] = [s.strip() for s in edited_skills_string.split('\n') if s.strip()]
            for proj in edited_data.get('projects', []):
                proj['details'] = [line.strip() for line in proj['details'].split('\n') if line.strip()]
            for exp in edited_data.get('experience', []):
                exp['details'] = [line.strip() for line in exp['details'].split('\n') if line.strip()]
            st.session_state.resume_data = edited_data
            st.query_params["page"] = "templates"
            st.rerun()

elif page == "templates":
    if st.session_state.get('feedback_triggered'):
        display_feedback_dialog()
        st.session_state.feedback_triggered = False

    if 'resume_data' not in st.session_state or not st.session_state.resume_data:
        st.warning("Please generate your resume data first!")
        st.link_button("Click here to go back to the form", "?page=builder")
    else:
        st.markdown(f"### **Step 3:** Choose Your Style & Download")
        st.caption(f"Great, **{st.session_state.resume_data.get('name', '')}**! Now pick a template and get your PDF.")
        st.link_button("← Back to Review Data", "?page=review")
        st.divider()
        form_col, preview_col = st.columns([1, 2])
        with form_col:
            template_name = st.selectbox("Select a template:", templates.keys(), key="template_select")
            default_color = templates[template_name][1]
            accent_color = st.color_picker("Select an accent color:", default_color, key="color_picker")
            try:
                template_filename = templates[template_name][0]
                env = Environment(loader=FileSystemLoader(BASE_DIR))
                template = env.get_template(template_filename)
                html_out = template.render(st.session_state.resume_data, accent_color=accent_color)
                pdf_bytes = html_to_pdf(html_out)
                
                if st.download_button(
                    label="📥 Download PDF", data=pdf_bytes,
                    file_name=f"{st.session_state.resume_data.get('name', 'resume').replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf", use_container_width=True,
                    on_click=lambda: st.session_state.update(feedback_triggered=True)
                ):
                    pass
                    
            except Exception as e:
                st.error(f"❌ An error occurred during PDF generation: {e}")
                html_out = f"<h3>Error rendering template:</h3><p>{e}</p>"
        with preview_col:
            st.subheader("📄 Preview")
            if 'html_out' in locals() and html_out:
                styled_preview = f'<div style="background-color:white; border-radius: 8px; padding: 25px; border: 1px solid #ddd;">{html_out}</div>'
                st.components.v1.html(styled_preview, height=800, scrolling=True)
    show_footer()

elif page == "demo":
    st.markdown("### Template Showcase")
    st.caption("Explore our professionally designed templates below.")
    st.divider()
    def render_demo_card(col, template_name):
        with col:
            filename, color = templates[template_name]
            st.subheader(f"'{template_name}' Style")
            env = Environment(loader=FileSystemLoader(BASE_DIR))
            template = env.get_template(filename)
            html_out = template.render(sample_data, accent_color=color)
            styled_demo = f'<div style="background-color:white; border-radius: 8px; padding: 25px; border: 1px solid #ddd;">{html_out}</div>'
            st.components.v1.html(styled_demo, height=450, scrolling=True)
            st.link_button(f"Create with this Style →", f"?page=builder", use_container_width=True)
    row1_col1, row1_col2 = st.columns(2)
    render_demo_card(row1_col1, "Corporate"); render_demo_card(row1_col2, "Modern")
    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)
    render_demo_card(row2_col1, "Aesthetic"); render_demo_card(row2_col2, "Classic")
    st.divider()
    st.header("Ready to build yours?")
    st.link_button("Create My Resume Now →", "?page=builder", use_container_width=True)
    show_footer()

else: # Default page is "home"
    st.markdown("""
    <style>
        .hero-container {
            padding: 4rem 2rem;
            text-align: center;
            background: linear-gradient(45deg, #1a2a6c, #b21f1f, #fdbb2d);
            border-radius: 16px;
            color: white;
            animation: fadeIn 1s ease-in-out;
        }
        .hero-container h1 { font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem; }
        .hero-container p { font-size: 1.2rem; max-width: 600px; margin: 0 auto 2rem auto; color: rgba(255, 255, 255, 0.9); }
    </style>
    <div class="hero-container">
        <h1>The AI-Powered Resume Builder</h1>
        <p>Go from draft to dream job. Create a professional, tailored resume in minutes with the help of AI.</p>
        <div style="display: flex; justify-content: center; gap: 1rem;">
             <a href="?page=builder" target="_self" style="background-color: white; color: #1a2a6c; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1rem;">Create My Resume</a>
             <a href="?page=demo" target="_self" style="background-color: transparent; border: 2px solid white; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.1rem;">View Templates</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="animation: fadeIn 1s ease-in-out;">
    <h2 style="text-align: center; font-weight: 600; margin-top: 3rem;">How It Works</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem;">
        <div style="text-align: center; padding: 1.5rem; background-color: #f8f9fa; border-radius: 12px; border: 1px solid #eee;">
            <h3 style="font-size: 4rem; margin-bottom: 0.5rem; color: #3498db;">1.</h3>
            <h4>Enter Your Details</h4>
            <p style="color: #555;">Fill in your basic information, skills, projects, and experience. Paste a job description to tailor your resume for a specific role.</p>
        </div>
        <div style="text-align: center; padding: 1.5rem; background-color: #f8f9fa; border-radius: 12px; border: 1px solid #eee;">
            <h3 style="font-size: 4rem; margin-bottom: 0.5rem; color: #3498db;">2.</h3>
            <h4>Generate & Enhance</h4>
            <p style="color: #555;">Our AI instantly structures your data, enhances your descriptions for impact, and crafts a professional summary for you.</p>
        </div>
        <div style="text-align: center; padding: 1.5rem; background-color: #f8f9fa; border-radius: 12px; border: 1px solid #eee;">
            <h3 style="font-size: 4rem; margin-bottom: 0.5rem; color: #3498db;">3.</h3>
            <h4>Review & Download</h4>
            <p style="color: #555;">Fine-tune the AI-generated content, pick a stylish template, and download your perfect, job-winning resume as a PDF.</p>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
    show_footer()
