import os
import streamlit as st
from agents import (
    get_client,
    skill_gap_agent,
    curriculum_architect_agent,
    assessment_generator_agent,
    ai_mentor_agent,
)

st.set_page_config(page_title="SkillForge Multi-Agent AI", page_icon="🧠", layout="wide")

# Custom Dark/Modern Styling
st.markdown("""
<style>
    .agent-box {
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #4F8BF9;
        background-color: rgba(79, 139, 249, 0.1);
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 SkillForge AI — Adaptive Multi-Agent Career & Learning Platform")
st.caption("Powered by 4 Collaborating AI Agents: Skill Analyzer • Curriculum Architect • Assessment Engine • AI Mentor")

# Sidebar: API Key & Learner Profile
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password")

    st.divider()
    st.header("👤 Learner Profile")
    name = st.text_input("Full Name", value="Alex Rivera")
    target_role = st.selectbox(
        "🎯 Target Career Goal (Change anytime to trigger re-analysis)",
        ["Full Stack Developer", "AI / Machine Learning Engineer", "Cloud & DevOps Engineer", "Cybersecurity Analyst"]
    )
    existing_skills = st.text_area("Current Skills (comma-separated)", value="Python, SQL, basic HTML")
    certifications = st.text_input("Certifications", value="Python Essentials")
    projects = st.text_area("Completed Projects", value="Student Attendance CLI in Python, Basic Portfolio Page")

    run_btn = st.button("🚀 Run Multi-Agent Pipeline", type="primary", use_container_width=True)

# Initialize Session State
for key in ["gap_data", "roadmap_data", "quiz_data", "mentor_data", "agent_logs", "completed_steps"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["agent_logs", "completed_steps"] else []

def execute_pipeline(mentor_directive=""):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar (or set GEMINI_API_KEY env var).")
        return

    client = get_client(api_key)
    profile = {
        "name": name,
        "target_role": target_role,
        "existing_skills": [s.strip() for s in existing_skills.split(",") if s.strip()],
        "certifications": certifications,
        "projects": projects,
    }
    st.session_state.agent_logs = []

    with st.status("🤖 Multi-Agent Collaboration in Progress...", expanded=True) as status:
        st.write("🔍 **Agent 1 (Skill & Career Gap Agent):** Auditing profile against target role requirements...")
        gap = skill_gap_agent(client, profile)
        st.session_state.gap_data = gap
        st.session_state.agent_logs.append(f"**[Skill Gap Agent → Curriculum Agent]:** {gap.get('agent_note')}")

        st.write("🗺️ **Agent 2 (Curriculum Architect Agent):** Designing personalized learning roadmap & hands-on labs...")
        roadmap = curriculum_architect_agent(client, profile, gap, mentor_directive)
        st.session_state.roadmap_data = roadmap
        st.session_state.agent_logs.append(f"**[Curriculum Agent → Assessment Agent]:** {roadmap.get('agent_note')}")

        st.write("📝 **Agent 3 (Assessment Agent):** Generating adaptive diagnostic quiz for missing skills...")
        quiz = assessment_generator_agent(client, target_role, gap.get("missing_skills", []))
        st.session_state.quiz_data = quiz
        st.session_state.agent_logs.append(f"**[Assessment Agent]:** Generated 3 targeted diagnostic questions for `{target_role}`.")

        status.update(label="✅ Multi-Agent Analysis Complete!", state="complete", expanded=False)

if run_btn:
    st.session_state.mentor_data = None
    st.session_state.completed_steps = []
    execute_pipeline()

# Main Dashboard
if st.session_state.gap_data and st.session_state.roadmap_data:
    # Live Agent Collaboration Feed
    with st.expander("📡 Live Inter-Agent Communication Log (Click to inspect agent handoffs)", expanded=True):
        for log in st.session_state.agent_logs:
            st.markdown(f'<div class="agent-box">{log}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 1. Skill & Career Match",
        "🗺️ 2. Personalized Roadmap",
        "📝 3. Adaptive Assessment",
        "🧑‍🏫 4. AI Mentor & Progress"
    ])

    # TAB 1: Skill Analysis & Career Matching
    with tab1:
        gap = st.session_state.gap_data
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label=f"Role Readiness: {target_role}", value=f"{gap['match_percentage']}%")
            st.progress(gap["match_percentage"] / 100)
            st.subheader("✅ Verified Strengths")
            for s in gap["strengths"]:
                st.success(s)
        with col2:
            st.subheader("⚠️ Identified Skill Gaps")
            for item in gap["missing_skills"]:
                badge = "🔴" if item["priority"] == "High" else "🟡"
                st.warning(f"{badge} **{item['skill']}** ({item['priority']} Priority) — {item['reason']}")

    # TAB 2: Learning Recommendations & Progress Tracking
    with tab2:
        st.subheader(f"🎯 Tailored Learning Path for {target_role}")
        steps = st.session_state.roadmap_data.get("roadmap", [])
        completed_count = 0
        for idx, step in enumerate(steps):
            checked = st.checkbox(
                f"Step {step['step']}: Master **{step['skill']}** ({step['duration']})",
                key=f"step_chk_{idx}_{target_role}"
            )
            if checked:
                completed_count += 1
            with st.container(border=True):
                st.markdown(f"- **📚 Recommended Course:** {step['course_topic']}")
                st.markdown(f"- **🛠️ Practical Tutorial:** {step['tutorial_idea']}")
                st.markdown(f"- **💻 Capstone Mini-Project:** {step['hands_on_project']}")

        if steps:
            prog = int((completed_count / len(steps)) * 100)
            st.divider()
            st.write(f"**Overall Module Completion:** {prog}%")
            st.progress(prog / 100)

    # TAB 3: Adaptive Assessment
    with tab3:
        st.subheader("🧪 Skill Gap