import os
import json
from google import genai
from google.genai import types

def get_client(api_key: str):
    return genai.Client(api_key=api_key)

def run_agent(client, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_prompt,
        config=config,
    )
    return response.text

# AGENT 1: Skill & Career Gap Analyzer
def skill_gap_agent(client, profile: dict) -> dict:
    sys_prompt = """You are the Skill & Career Gap Agent. Analyze the learner's existing skills, certifications, projects, and target role.
    Return ONLY valid JSON with keys:
    - "match_percentage": integer (0-100)
    - "strengths": list of strings
    - "missing_skills": list of objects {"skill": str, "priority": "High"|"Medium"|"Low", "reason": str}
    - "agent_note": short summary of your analysis for the Curriculum Agent."""
    
    result = run_agent(client, sys_prompt, json.dumps(profile))
    return json.loads(result)

# AGENT 2: Curriculum & Resource Architect
def curriculum_architect_agent(client, profile: dict, gap_analysis: dict, mentor_feedback: str = "") -> dict:
    sys_prompt = """You are the Curriculum Architect Agent. Using the Skill Gap Agent's analysis and any AI Mentor recalibration notes, build a personalized step-by-step learning path.
    Return ONLY valid JSON with keys:
    - "roadmap": list of objects {"step": int, "skill": str, "duration": str, "course_topic": str, "tutorial_idea": str, "hands_on_project": str}
    - "agent_note": short handoff message to the Assessment & Mentor agents."""
    
    payload = {"profile": profile, "gap_analysis": gap_analysis, "mentor_recalibration": mentor_feedback}
    result = run_agent(client, sys_prompt, json.dumps(payload))
    return json.loads(result)

# AGENT 3: Adaptive Assessment Agent (Quiz Generator)
def assessment_generator_agent(client, target_role: str, missing_skills: list) -> dict:
    sys_prompt = """You are the Assessment Agent. Generate a targeted 3-question multiple-choice diagnostic quiz testing the learner's highest-priority missing skills.
    Return ONLY valid JSON with key:
    - "questions": list of 3 objects {"id": int, "skill": str, "question": str, "options": list of 4 strings, "answer": exact matching option string}"""
    
    payload = {"target_role": target_role, "missing_skills": missing_skills}
    result = run_agent(client, sys_prompt, json.dumps(payload))
    return json.loads(result)

# AGENT 4: AI Mentor & Recalibration Agent
def ai_mentor_agent(client, profile: dict, quiz_results: dict, current_roadmap: dict) -> dict:
    sys_prompt = """You are the AI Mentor Agent. Evaluate the learner's assessment score and progress. If they scored below 70% or changed goals, explicitly adjust their learning path to reinforce weak concepts before advancing.
    Return ONLY valid JSON with keys:
    - "status": "On Track" | "Needs Reinforcement" | "Accelerated"
    - "mentor_guidance": empathetic, actionable coaching advice (3-4 sentences)
    - "recalibration_directive": specific instructions to update the roadmap based on weak skills."""
    
    payload = {"profile": profile, "quiz_results": quiz_results, "current_roadmap": current_roadmap}
    result = run_agent(client, sys_prompt, json.dumps(payload))
    return json.loads(result)