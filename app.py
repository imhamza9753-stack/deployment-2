import streamlit as st
import os
from groq import Groq
import json
import time
from datetime import datetime
import re

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Code Analyzer Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== HIDE STREAMLIT DEFAULT UI ====================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# ==================== BRIGHT PROFESSIONAL CSS (keep as is – omitted for brevity) ====================
# (Your existing CSS – I'm not repeating it to save space, but you must keep it)

# ==================== LOAD API KEY (Cloud + Local fallback) ====================
def get_api_key():
    # First try Streamlit secrets (deployment)
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key.strip()
    except:
        pass
    # Fallback for local development: read from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key.strip()
    except:
        pass
    return None

# ==================== SESSION STATE ====================
if 'groq_client' not in st.session_state:
    api_key = get_api_key()
    st.session_state.groq_client = None
    st.session_state.api_key = api_key
    
    if api_key and api_key != "your_groq_api_key_here":
        try:
            st.session_state.groq_client = Groq(api_key=api_key)
        except Exception as e:
            st.session_state.groq_client = None
            st.error(f"Groq client init error: {type(e).__name__}: {str(e)}")

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

if 'score_history' not in st.session_state:
    st.session_state.score_history = []

# ==================== CONSTANTS ====================
LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go", "Rust",
    "PHP", "Ruby", "Swift", "Kotlin", "SQL", "R", "MATLAB", "Julia", "Scala",
    "Perl", "Shell/Bash", "Groovy", "Lua", "Haskell", "Clojure", "Elixir",
    "F#", "VB.NET", "ObjectiveC"
]

# ==================== FUNCTIONS ====================
def analyze_code_with_groq(code, language):
    try:
        code = code[:4000]

        prompt = f"""
You are a SENIOR SOFTWARE ENGINEER + DEBUGGING EXPERT.

Analyze this {language} code.

⚠️ RULES:
- Find REAL bugs only
- Explain WHY the bug happens (ROOT CAUSE)
- Give SIMPLE FIX
- If something is uncertain, explain it in "reason"
- NEVER return empty fields
- Return ONLY valid JSON

FORMAT:
{{
    "quality_score": 0,
    "bugs": [
        {{
            "issue": "What is wrong",
            "severity": "HIGH|MEDIUM|LOW",
            "reason": "Why this bug happens (root cause)",
            "fix": "How to fix it"
        }}
    ],
    "security_issues": [
        {{
            "issue": "",
            "reason": "",
            "fix": ""
        }}
    ],
    "optimizations": [],
    "code_smells": [],
    "best_practices": [],
    "fixed_code": "",
    "time_complexity": "",
    "space_complexity": ""
}}

CODE:
{code}
"""

        response = st.session_state.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "")

        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if not match:
            return {
                "quality_score": 40,
                "bugs": [{
                    "issue": "AI failed to generate structured analysis",
                    "severity": "MEDIUM",
                    "reason": "Model response was not valid JSON. This usually happens due to long code or formatting confusion.",
                    "fix": "Try reducing code size or re-run analysis"
                }],
                "security_issues": [],
                "optimizations": [],
                "code_smells": [],
                "best_practices": [],
                "fixed_code": code,
                "time_complexity": "Unknown",
                "space_complexity": "Unknown"
            }

        analysis = json.loads(match.group())

        # SAFE DEFAULTS
        analysis.setdefault("bugs", [])
        analysis.setdefault("security_issues", [])
        analysis.setdefault("optimizations", [])
        analysis.setdefault("code_smells", [])
        analysis.setdefault("best_practices", [])

        if not analysis["bugs"]:
            analysis["bugs"] = [{
                "issue": "No explicit bug detected",
                "severity": "LOW",
                "reason": "Model did not detect a clear syntax or logic error, but hidden edge cases may exist.",
                "fix": "Add validation, test edge cases, and review logic flow"
            }]

        if not analysis["security_issues"]:
            analysis["security_issues"] = [{
                "issue": "No explicit security issue detected",
                "reason": "Model did not find direct vulnerability patterns",
                "fix": "Still review input validation, authentication, and data handling"
            }]

        return analysis

    except Exception as e:
        return {
            "quality_score": 0,
            "bugs": [{
                "issue": "Analysis crashed",
                "severity": "HIGH",
                "reason": str(e),
                "fix": "Check API key or model response format"
            }],
            "security_issues": [],
            "optimizations": [],
            "code_smells": [],
            "best_practices": [],
            "fixed_code": code,
            "time_complexity": "Unknown",
            "space_complexity": "Unknown"
        }

# ==================== MAIN PAGE ====================

st.markdown("""
<div class="main-header">
    <h1>🔍 Code Analyzer Pro</h1>
    <p>Professional Code Review • Instant Analysis • Expert Insights</p>
</div>
""", unsafe_allow_html=True)

# Show error if API key is missing or client not initialized
if not st.session_state.api_key:
    st.markdown("""
    <div class="error-box">
    <strong>❌ API Key Not Found</strong><br><br>
    <strong>For deployment on Streamlit Cloud:</strong><br>
    Go to your app → Settings → Secrets and add:<br>
    <code>GROQ_API_KEY = "your_groq_key_here"</code><br><br>
    <strong>For local development:</strong><br>
    Create a <code>.env</code> file with <code>GROQ_API_KEY=your_key</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
elif not st.session_state.groq_client:
    st.markdown("""
    <div class="error-box">
    <strong>⚠️ API Connection Error</strong><br>
    Could not connect to Groq API. Please check:<br>
    • Your API key is correct<br>
    • Your internet connection is working<br>
    • Your API key is not expired
    </div>
    """, unsafe_allow_html=True)

# Main Layout (same as before – keep your existing layout code)
col1, col2 = st.columns([2.2, 1.3], gap="large")
# ... (keep all the UI code exactly as you had it, only the top part changed)

# The rest of your UI, results, sidebar, footer remains unchanged.
