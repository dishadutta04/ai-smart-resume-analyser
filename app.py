import streamlit as st
import time
from utils.pdf_parser import extract_text_from_pdf
from utils.ai_analyzer import analyze_resume, improve_resume
import io

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer - ATS Scorer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SUPER AWESOME CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main container glassmorphism */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Hero header with animation */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5);
        animation: slideDown 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Score card with 3D effect */
    .score-card {
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        font-size: 4rem;
        font-weight: 800;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: scaleIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .score-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .score-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    .score-good {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    .score-medium {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .score-bad {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    
    /* Feature cards with hover effect */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease-out;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Suggestion box with icon */
    .suggestion-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e6f0ff 100%);
        padding: 1.5rem;
        border-left: 5px solid #667eea;
        border-radius: 10px;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .suggestion-box:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    .suggestion-box strong {
        color: #667eea;
        font-size: 1.1rem;
    }
    
    /* Progress bar animation */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        animation: progressPulse 2s ease-in-out infinite;
    }
    
    @keyframes progressPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Strength/Weakness badges */
    .strength-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0.5rem 0.5rem 0;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(17, 153, 142, 0.3);
        animation: bounceIn 0.6s ease;
    }
    
    .weakness-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.5rem 0.5rem 0.5rem 0;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
        animation: bounceIn 0.6s ease;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            transform: scale(1);
        }
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        margin: 1rem 0;
    }
    
    .info-box h4 {
        margin-top: 0;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
        border-radius: 10px 10px 0 0;
        background: linear-gradient(135deg, #f0f4ff 0%, #e6f0ff 100%);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Metric cards */
    .metric-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    .metric-card p {
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(102, 126, 234, 0.3);
        border-top: 5px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Floating elements */
    .floating {
        animation: floating 3s ease-in-out infinite;
    }
    
    @keyframes floating {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
</style>
""", unsafe_allow_html=True)

# Hero Header with Animation
st.markdown("""
<div class="hero-header">
    <h1>📄 AI Resume Analyzer</h1>
    <p>Get instant ATS score + AI-powered improvement suggestions</p>
    <p style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.8;">🚀 Beat the ATS • 💡 Get Hired Faster • ✨ AI-Powered Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with Beautiful Design
with st.sidebar:
    st.markdown("## 🔑 API Configuration")
    
    ai_provider = st.selectbox(
        "Choose AI Provider",
        ["OpenAI", "Google Gemini"],
        help="Select your preferred AI service"
    )
    
    api_key = st.text_input(
        f"{ai_provider} API Key",
        type="password",
        placeholder="sk-..." if ai_provider == "OpenAI" else "AIza...",
        help="Your API key is never stored"
    )
    
    if ai_provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4.1-mini"])
    else:
        model = st.selectbox("Model", ["gemini-2.5-pro", "gemini-2.5-flash"])
    
    if api_key and len(api_key) > 20:
        st.success("✅ API Key Loaded!")
    else:
        st.warning("⚠️ Enter API Key")
    
    st.markdown("---")
    
    st.markdown("### 📊 What You Get")
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
        <p>📈 <strong>ATS Score (0-100)</strong></p>
        <p>🔍 <strong>Keyword Analysis</strong></p>
        <p>✨ <strong>AI Suggestions</strong></p>
        <p>📝 <strong>Resume Rewrite</strong></p>
        <p>📥 <strong>Export Results</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; font-size: 0.9rem;">
        • Use PDF format for best results<br>
        • Include job description for targeted analysis<br>
        • Update resume section by section<br>
        • Test multiple versions
    </div>
    """, unsafe_allow_html=True)

# Main content with tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "📊 Analysis Results", "✨ Improved Resume"])

with tab1:
    st.markdown('<p class="section-header">Upload Your Resume</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drop your PDF here or click to browse",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        job_description = st.text_area(
            "🎯 Target Job Description (Optional but Recommended)",
            placeholder="Paste the job description here for more accurate keyword matching and tailored suggestions...",
            height=200
        )
    
    with col2:
        st.markdown("""
        <div class="info-box floating">
            <h4>🎯 For Best Results:</h4>
            <ul style="list-style: none; padding-left: 0;">
                <li>✓ Use PDF format</li>
                <li>✓ Clear section headings</li>
                <li>✓ Include relevant keywords</li>
                <li>✓ Add job description</li>
                <li>✓ Keep formatting simple</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if uploaded_file and api_key:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🚀 Analyze My Resume Now", type="primary", use_container_width=True):
                # Create loading animation
                st.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <h3>🤖 AI is analyzing your resume...</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Extract text
                    status_text.markdown("### 📄 Extracting text from PDF...")
                    progress_bar.progress(20)
                    time.sleep(0.8)
                    
                    resume_text = extract_text_from_pdf(uploaded_file)
                    st.session_state['resume_text'] = resume_text
                    st.session_state['job_description'] = job_description
                    
                    # AI Analysis
                    status_text.markdown("### 🤖 Running AI analysis...")
                    progress_bar.progress(50)
                    time.sleep(1)
                    
                    analysis = analyze_resume(
                        resume_text, 
                        job_description,
                        api_key,
                        ai_provider,
                        model
                    )
                    
                    status_text.markdown("### ✨ Generating insights...")
                    progress_bar.progress(80)
                    time.sleep(0.8)
                    
                    st.session_state['analysis'] = analysis
                    
                    progress_bar.progress(100)
                    status_text.markdown("### ✅ Analysis Complete!")
                    time.sleep(0.5)
                    
                    st.balloons()
                    st.success("🎉 Analysis complete! Check the 'Analysis Results' tab.")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif not api_key:
        st.warning("👈 Please enter your API key in the sidebar first")
    else:
        st.info("👆 Upload your resume PDF to get started")

with tab2:
    st.markdown('<p class="section-header">📊 Resume Analysis Results</p>', unsafe_allow_html=True)
    
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        # BEAUTIFUL SCORE CARD
        score = analysis.get('ats_score', 0)
        if score >= 85:
            score_class = "score-excellent"
            emoji = "🎉"
            message = "Excellent!"
        elif score >= 70:
            score_class = "score-good"
            emoji = "👍"
            message = "Good"
        elif score >= 50:
            score_class = "score-medium"
            emoji = "⚠️"
            message = "Needs Work"
        else:
            score_class = "score-bad"
            emoji = "❌"
            message = "Critical"
        
        st.markdown(f"""
        <div class="score-card {score_class}">
            {emoji} {score}/100
            <div style="font-size: 1.5rem; margin-top: 1rem;">{message}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Executive Summary")
        st.write(analysis.get('summary', ''))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Strengths & Weaknesses in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### ✅ Strengths")
            for strength in analysis.get('strengths', []):
                st.markdown(f'<div class="strength-badge">✓ {strength}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### ⚠️ Areas to Improve")
            for weakness in analysis.get('weaknesses', []):
                st.markdown(f'<div class="weakness-badge">! {weakness}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed Suggestions
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Actionable Suggestions")
        for i, suggestion in enumerate(analysis.get('suggestions', []), 1):
            st.markdown(f"""
            <div class="suggestion-box">
                <strong>{i}. {suggestion.get('title', 'Suggestion')}</strong>
                <p style="margin-top: 0.5rem; color: #555;">{suggestion.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Keyword Analysis
        if 'keywords' in analysis:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### 🔑 Keyword Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Found Keywords:**")
                found = analysis['keywords'].get('found', [])
                if found:
                    for kw in found[:10]:
                        st.markdown(f'<span class="strength-badge">{kw}</span>', unsafe_allow_html=True)
                else:
                    st.write("No specific keywords identified")
            
            with col2:
                st.markdown("**⚠️ Missing Important Keywords:**")
                missing = analysis['keywords'].get('missing', [])
                if missing:
                    for kw in missing[:10]:
                        st.markdown(f'<span class="weakness-badge">{kw}</span>', unsafe_allow_html=True)
                else:
                    st.write("No missing keywords identified")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="info-box">
            <h3>👈 Get Started</h3>
            <p>Upload and analyze your resume in the <strong>Upload Resume</strong> tab to see detailed results here!</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown('<p class="section-header">✨ AI-Improved Resume</p>', unsafe_allow_html=True)
    
    if 'analysis' in st.session_state and 'resume_text' in st.session_state:
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🎨 Generate Improved Version", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is rewriting your resume..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    improved = improve_resume(
                        st.session_state['resume_text'],
                        st.session_state['analysis'],
                        st.session_state.get('job_description', ''),
                        api_key,
                        ai_provider,
                        model
                    )
                    
                    st.session_state['improved_resume'] = improved
                    st.success("✅ Improved resume generated!")
        
        if 'improved_resume' in st.session_state:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### 📄 Your Improved Resume")
            
            improved_text = st.text_area(
                "Review and edit your improved resume:",
                st.session_state['improved_resume'],
                height=400,
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=improved_text,
                    file_name="improved_resume.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="📄 Download as Markdown",
                    data=improved_text,
                    file_name="improved_resume.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div class="info-box">
            <h3>👈 Analyze First</h3>
            <p>Please analyze your resume in the <strong>Upload Resume</strong> tab before generating improvements!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; opacity: 0.8;">
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Made with ❤️ using Streamlit & AI</p>
    <p style="font-size: 0.9rem; color: #667eea;">Made By Disha | 🔒 Your data is never stored • 🚀 Powered by Advanced AI • ⚡ Instant Results</p>
</div>
""", unsafe_allow_html=True)
