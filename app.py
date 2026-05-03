import streamlit as st
import os
from groq import Groq
import json
import re
import string
from datetime import datetime

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

# ==================== BRIGHT PROFESSIONAL CSS ====================
st.markdown("""
    <style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    code {
        font-family: 'Fira Code', 'Courier New', monospace;
    }
    
    html, body {
        background: #f8fafc !important;
    }
    
    .stApp {
        background: #f8fafc !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background: #f8fafc !important;
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 50px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);
    }
    
    .main-header h1 {
        font-size: 2.8em;
        font-weight: 900;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header p {
        font-size: 1.1em;
        margin: 10px 0 0 0;
        opacity: 0.95;
    }
    
    .card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 30px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 1em !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-left: 5px solid #10b981;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #065f46;
        font-weight: 500;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 5px solid #ef4444;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #7f1d1d;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #78350f;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 5px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #1e40af;
        font-weight: 500;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin: 25px 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #93c5fd;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.2);
    }
    
    .stat-label {
        font-size: 0.85em;
        color: #475569;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .stat-value {
        font-size: 2.2em;
        font-weight: 900;
        color: #1e40af;
    }
    
    .bug-high {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 5px solid #ef4444;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #7f1d1d;
    }
    
    .bug-medium {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #78350f;
    }
    
    .bug-low {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-left: 5px solid #10b981;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: #065f46;
    }
    
    .code-display {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        overflow-x: auto;
        font-family: 'Fira Code', monospace;
        font-size: 0.9em;
        line-height: 1.6;
        color: #1e293b;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 12px 20px;
        border: 1px solid #e2e8f0;
        color: #475569;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-color: #93c5fd;
        color: #1e40af;
        font-weight: 600;
    }
    
    .stTextArea textarea {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.95em !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    .stCheckbox {
        color: #1e293b;
    }
    
    .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .stDivider {
        border-color: #e2e8f0 !important;
    }
    
    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== LOAD API KEY ====================
def get_api_key():
    # Try Streamlit secrets first (deployment)
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key.strip()
    except:
        pass
    # Fallback for local development
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
    st.session_state.api_key = api_key
    st.session_state.groq_client = None
    
    if api_key and api_key != "your_groq_api_key_here":
        try:
            st.session_state.groq_client = Groq(api_key=api_key)
        except Exception as e:
            st.session_state.groq_client = None

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

# ==================== ANALYZE FUNCTION (with JSON sanitisation) ====================
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
        
        # Sanitise JSON string to remove invalid control characters
        json_str = match.group()
        # Remove ASCII control characters except newline, tab, carriage return (they will be escaped later if needed)
        control_chars = ''.join(chr(c) for c in range(0, 32) if chr(c) not in '\n\t\r')
        json_str = re.sub(f'[{re.escape(control_chars)}]', '', json_str)
        
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError as je:
            # If still failing, return fallback
            return {
                "quality_score": 30,
                "bugs": [{
                    "issue": "JSON parsing error after sanitisation",
                    "severity": "HIGH",
                    "reason": f"Model returned malformed JSON: {str(je)[:100]}",
                    "fix": "Re-run analysis; the AI sometimes adds unescaped characters"
                }],
                "security_issues": [],
                "optimizations": [],
                "code_smells": [],
                "best_practices": [],
                "fixed_code": code,
                "time_complexity": "Unknown",
                "space_complexity": "Unknown"
            }

        # Ensure required fields exist
        analysis.setdefault("bugs", [])
        analysis.setdefault("security_issues", [])
        analysis.setdefault("optimizations", [])
        analysis.setdefault("code_smells", [])
        analysis.setdefault("best_practices", [])
        analysis.setdefault("quality_score", 50)
        analysis.setdefault("fixed_code", code)
        analysis.setdefault("time_complexity", "Unknown")
        analysis.setdefault("space_complexity", "Unknown")

        # Ensure bugs have required fields
        for bug in analysis["bugs"]:
            bug.setdefault("severity", "MEDIUM")
            bug.setdefault("reason", "No reason provided")
            bug.setdefault("fix", "No fix provided")
        
        # Ensure security_issues have required fields
        for issue in analysis["security_issues"]:
            if isinstance(issue, dict):
                issue.setdefault("reason", "No reason provided")
                issue.setdefault("fix", "No fix provided")
            else:
                # Convert string to dict
                issue = {"issue": str(issue), "reason": "No reason", "fix": "No fix"}
        
        # If no bugs found, add a placeholder
        if not analysis["bugs"]:
            analysis["bugs"] = [{
                "issue": "No explicit bugs detected",
                "severity": "LOW",
                "reason": "No clear syntax or logic errors, but hidden edge cases may exist.",
                "fix": "Add validation, test edge cases, and review logic"
            }]
        
        if not analysis["security_issues"]:
            analysis["security_issues"] = [{
                "issue": "No explicit security issues detected",
                "reason": "Model did not find direct vulnerabilities",
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

# Check API key
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

if not st.session_state.groq_client:
    st.markdown("""
    <div class="error-box">
    <strong>⚠️ API Connection Error</strong><br>
    Could not connect to Groq API. Please check:<br>
    • Your API key is correct<br>
    • Your internet connection is working<br>
    • Your API key is not expired
    </div>
    """, unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([2.2, 1.3], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    selected_language = st.selectbox("📌 Select Programming Language", LANGUAGES, index=0)
    code_input = st.text_area(
        "💻 Paste Your Code",
        height=380,
        placeholder="def hello():\n    print('Hello, World!')"
    )
    st.write("")
    opt_col1, opt_col2, opt_col3 = st.columns(3)
    with opt_col1:
        beginner_mode = st.checkbox("🎓 Beginner Mode", value=False)
    with opt_col2:
        show_comparison = st.checkbox("🔄 Show Fixed Code", value=False)
    with opt_col3:
        show_details = st.checkbox("📊 Show Details", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")
    analysis_depth = st.select_slider("Analysis Depth", options=["Quick", "Standard", "Deep"], value="Standard")
    st.write("")
    st.divider()
    st.write("")
    analyze_clicked = st.button("🚀 ANALYZE CODE", use_container_width=True, type="primary")
    if analyze_clicked:
        if not code_input.strip():
            st.markdown('<div class="warning-box"><strong>⚠️ Empty Code</strong><br>Please paste some code to analyze</div>', unsafe_allow_html=True)
        elif not st.session_state.groq_client:
            st.markdown('<div class="error-box"><strong>❌ API Not Connected</strong><br>Check your API key configuration</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 Analyzing your code..."):
                analysis = analyze_code_with_groq(code_input, selected_language)
                if analysis:
                    st.session_state.current_analysis = analysis
                    st.session_state.analysis_history.append({
                        'language': selected_language,
                        'timestamp': datetime.now(),
                        'score': analysis.get('quality_score', 0)
                    })
                    st.session_state.score_history.append(analysis.get('quality_score', 0))
                    st.rerun()
                else:
                    st.markdown('<div class="error-box"><strong>❌ Analysis Failed</strong><br>Could not analyze the code. Try with shorter code or check your API key.</div>', unsafe_allow_html=True)
    if st.button("🔄 RE-ANALYZE", use_container_width=True):
        if st.session_state.current_analysis:
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Results section
if st.session_state.current_analysis:
    analysis = st.session_state.current_analysis
    st.markdown('<div class="success-box"><strong>✅ Analysis Complete!</strong> Your code has been analyzed successfully.</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box"><div class="stat-label">Quality Score</div><div class="stat-value">{analysis.get('quality_score',0)}/100</div></div>
        <div class="stat-box"><div class="stat-label">Bugs Found</div><div class="stat-value">{len(analysis.get('bugs',[]))}</div></div>
        <div class="stat-box"><div class="stat-label">Security Issues</div><div class="stat-value">{len(analysis.get('security_issues',[]))}</div></div>
        <div class="stat-box"><div class="stat-label">Code Smells</div><div class="stat-value">{len(analysis.get('code_smells',[]))}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"🐛 Bugs ({len(analysis.get('bugs',[]))})",
        f"🔒 Security ({len(analysis.get('security_issues',[]))})",
        "💡 Optimization",
        "📊 Complexity",
        "✨ Best Practices"
    ])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        bugs = analysis.get('bugs', [])
        for i, bug in enumerate(bugs, 1):
            severity = bug.get('severity', 'MEDIUM').upper()
            emoji = {'HIGH':'🔴','MEDIUM':'🟡','LOW':'🟢'}.get(severity,'⚪')
            cls = f"bug-{severity.lower()}"
            st.markdown(f"""
            <div class="{cls}">
            <strong>{emoji} Bug #{i} - {severity}</strong><br><br>
            <b>❌ Issue:</b> {bug.get('issue','')}<br>
            <b>🧠 Why it happens:</b> {bug.get('reason','Not explained')}<br>
            <b>🔧 Fix:</b> {bug.get('fix','No fix provided')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec = analysis.get('security_issues', [])
        for i, issue in enumerate(sec, 1):
            if isinstance(issue, dict):
                txt = issue.get('issue', str(issue))
            else:
                txt = str(issue)
            st.markdown(f'<div class="error-box"><strong>🔒 Issue #{i}:</strong> {txt}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        opts = analysis.get('optimizations', [])
        for i, opt in enumerate(opts, 1):
            st.markdown(f'<div class="info-box"><strong>💡 Tip {i}:</strong> {opt}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("**⏱️ Time Complexity**")
            st.markdown(f'<div class="code-display"><pre>{analysis.get("time_complexity","Unknown")}</pre></div>', unsafe_allow_html=True)
        with col_c2:
            st.markdown("**💾 Space Complexity**")
            st.markdown(f'<div class="code-display"><pre>{analysis.get("space_complexity","Unknown")}</pre></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        practices = analysis.get('best_practices', [])
        for i, p in enumerate(practices, 1):
            st.markdown(f'<div class="success-box"><strong>✨ Practice {i}:</strong> {p}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    st.markdown("---")
    if show_comparison:
        col1a, col2a = st.columns(2)
        with col1a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📝 Original Code")
            st.markdown(f'<div class="code-display"><pre>{code_input}</pre></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### ✅ Improved Code")
            fixed = analysis.get('fixed_code', code_input)
            st.markdown(f'<div class="code-display"><pre>{fixed}</pre></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Your Code")
        st.markdown(f'<div class="code-display"><pre>{code_input}</pre></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="card"><h3>🚀 Model Information</h3><p><strong>Model:</strong> LLaMA 3.1 70B</p><p><strong>Provider:</strong> Groq</p><p><strong>Speed:</strong> ⚡ Ultra-Fast</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>✨ Features</h3><ul><li>Code Quality Analysis</li><li>Bug Detection & Severity</li><li>Security Vulnerability Scan</li><li>Performance Optimization Tips</li><li>Time & Space Complexity</li><li>Best Practices</li><li>Code Smell Detection</li></ul></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>📖 How to Use</h3><ol><li>Select your programming language</li><li>Paste your code in the editor</li><li>Click "Analyze Code" button</li><li>Review the detailed analysis</li><li>See improvements in fixed code</li></ol></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>🎓 Supported Languages</h3><p>Python • JavaScript • Java • C++ • Go • Rust • PHP • Ruby • TypeScript • C# • Swift • Kotlin • SQL • R • And 13+ more</p></div>', unsafe_allow_html=True)
    if st.session_state.score_history:
        st.markdown('<div class="card"><h3>📊 Recent Scores</h3></div>', unsafe_allow_html=True)
        for i, score in enumerate(st.session_state.score_history[-5:], 1):
            st.metric(f"Analysis {i}", f"{score}/100")

st.markdown("""
<div style="text-align: center; padding: 30px 20px; margin-top: 50px; border-top: 1px solid #e2e8f0; color: #64748b;">
    <p><strong>🔍 Code Analyzer Pro</strong> • Powered by Groq AI</p>
    <p style="font-size: 0.9em;">Professional code review in seconds • Built for developers</p>
</div>
""", unsafe_allow_html=True)
