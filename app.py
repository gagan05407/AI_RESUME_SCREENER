import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from typing import List, Dict, Any

# Import modular pipeline functions
from resume_parser import parse_resume, extract_all_info
from jd_processing import parse_jd
from embeddings import get_embeddings_batch, USING_SBERT
from ranking import calculate_similarity, rank_candidates
from interview_generator import generate_questions_for_skills

# Set page config for a widescreen premium dashboard layout
st.set_page_config(
    page_title="AI Resume Screening & Candidate Ranking System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics (Glassmorphism headers, modern fonts, customized tags, and responsive cards)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Apply globally */
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Card Gradient styling */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(42, 82, 152, 0.25);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 0.5rem;
    }
    
    /* Styled Card Containers for Results */
    .candidate-card {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .candidate-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
        border-color: #2a5298;
    }
    
    /* Metric styling */
    .custom-metric-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
    }
    .custom-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3c72;
    }
    .custom-metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.2rem;
    }
    
    /* Skill tag badges */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .tag-matched {
        background-color: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .tag-missing {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }
    .tag-preferred {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    
    /* Leaderboard Badge style */
    .rank-badge {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: 700;
        color: white;
    }
    .rank-1 { background-color: #fbbf24; } /* Gold */
    .rank-2 { background-color: #9ca3af; } /* Silver */
    .rank-3 { background-color: #b45309; } /* Bronze */
    .rank-other { background-color: #3b82f6; } /* Blue */
</style>
""", unsafe_allow_html=True)

# Application Header Banner
st.markdown("""
<div class="header-container">
    <div class="header-title">💼 AI Resume Screener & Candidate Ranking System</div>
    <div class="header-subtitle">A state-of-the-art NLP and Semantic Search platform using Sentence-BERT (SBERT) and Information Extraction techniques.</div>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATIONS -----------------
st.sidebar.markdown("### ⚙️ System Settings")

# Model configuration
model_option = st.sidebar.selectbox(
    "Embedding Algorithm",
    ["Sentence-BERT (Semantic Match)", "TF-IDF (Keyword Match)"],
    index=0,
    help="Sentence-BERT matches context and synonyms. TF-IDF matches raw keywords."
)

# Minimum similarity score filter
min_match_score = st.sidebar.slider(
    "Minimum Match Threshold (%)",
    min_value=0,
    max_value=100,
    value=40,
    step=5,
    help="Exclude resumes that fall below this match percentage in final ranking."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Job Description Source")

# Job description input methods: paste text or upload file
jd_upload = st.sidebar.file_uploader(
    "Upload Job Description File", 
    type=["txt", "pdf", "docx"],
    help="Upload a TXT, PDF, or DOCX version of the JD."
)

jd_paste = st.sidebar.text_area(
    "Or Paste Job Description Text",
    height=200,
    placeholder="Paste roles, responsibilities, technical skills, and experience criteria here..."
)

# Parse Job Description Text
jd_text = ""
if jd_upload is not None:
    try:
        # Read file content and extract text using the parser
        file_bytes = jd_upload.read()
        jd_text = parse_resume(file_bytes, jd_upload.name)
    except Exception as e:
        st.sidebar.error(f"Error reading uploaded JD: {e}")
elif jd_paste.strip():
    jd_text = jd_paste

# Keep track of parsed JD details for sidebar visualization
jd_parsed_info = None
if jd_text:
    jd_parsed_info = parse_jd(jd_text)
    
    st.sidebar.success("Job Description Loaded!")
    
    # Sidebar quick info summary
    with st.sidebar.expander("🔍 JD Extraction Preview", expanded=False):
        st.markdown(f"**Required Experience:** {jd_parsed_info['experience']}")
        st.markdown(f"**Required Education:** {jd_parsed_info['education']}")
        st.markdown("**Required Skills Extracted:**")
        for skill in jd_parsed_info['required_skills']:
            st.markdown(f"- `{skill}`")

st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ *System automatically falls back to Scikit-Learn TF-IDF engine if HuggingFace server is unreachable or Sentence-BERT is not local.*")

# ----------------- MAIN LAYOUT -----------------

# Main resume uploader widget
st.markdown('<div class="section-title">📂 Candidate Resumes Uploader</div>', unsafe_allow_html=True)
uploaded_resumes = st.file_uploader(
    "Upload Candidate Resumes (Multiple PDFs or DOCXs allowed)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="Select and upload one or multiple resume files for processing."
)

if not jd_text or not uploaded_resumes:
    # Beautiful onboarding presentation when inputs are missing
    st.info("💡 **Getting Started:** Upload a Job Description in the sidebar, upload one or more Candidate Resumes above, and click 'Run Analytics' to generate matches.")
    
    st.markdown("### 🛠️ How it works under the hood")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        #### 1. Information Extraction
        The system parses PDFs/DOCXs, cleaning plain text. It runs rule-based entity extractors to isolate technical skills, education degrees, and compute years of experience from formatting.
        """)
    with col2:
        st.markdown("""
        #### 2. Semantic Embedding
        Using **Sentence-BERT (SBERT)** (`all-MiniLM-L6-v2`), we project both the resume and the job description into a high-dimensional semantic vector space.
        """)
    with col3:
        st.markdown("""
        #### 3. Candidate Ranking
        We run a Cosine Similarity search between the vector representations, map candidate skills against JD expectations, and output sorted rankings with tailored interview questions.
        """)
else:
    # Trigger matching pipeline button
    st.markdown("---")
    analyze_btn = st.button("🚀 Analyze & Rank Candidates", use_container_width=True, type="primary")
    
    if analyze_btn:
        with st.spinner("Executing parser, extracting entities, and computing semantic embeddings..."):
            try:
                # 1. Parse Job Description
                jd_info = parse_jd(jd_text)
                
                # 2. Parse all Resumes & Extract info
                candidates_data = []
                resume_texts = []
                
                for resume_file in uploaded_resumes:
                    file_bytes = resume_file.read()
                    # Reset stream pointer
                    resume_file.seek(0)
                    
                    # Extract plain text
                    raw_text = parse_resume(file_bytes, resume_file.name)
                    
                    if not raw_text.strip():
                        st.warning(f"Could not extract readable text from {resume_file.name}. Skipping.")
                        continue
                        
                    # Extract structured profile features
                    profile_info = extract_all_info(raw_text)
                    
                    # Calculate Skill Overlaps
                    jd_req_skills = set(jd_info["required_skills"])
                    jd_pref_skills = set(jd_info["preferred_skills"])
                    candidate_skills = set(profile_info["skills"])
                    
                    matched_skills = sorted(list(candidate_skills.intersection(jd_req_skills.union(jd_pref_skills))))
                    missing_skills = sorted(list(jd_req_skills.difference(candidate_skills)))
                    
                    candidates_data.append({
                        "name": resume_file.name,
                        "raw_text": raw_text,
                        "skills": profile_info["skills"],
                        "matched_skills": matched_skills,
                        "missing_skills": missing_skills,
                        "education": profile_info["education"],
                        "experience": profile_info["experience"],
                        "similarity_score": 0.0 # Placeholder, computed next
                    })
                    resume_texts.append(raw_text)
                    
                if not candidates_data:
                    st.error("No valid resumes were parsed. Please check file formatting.")
                else:
                    # 3. Generate Embeddings (Batch mode for vector alignment)
                    # We combine [JD text] + [Resume texts] to encode together.
                    batch_texts = [jd_text] + resume_texts
                    
                    # Temporarily force TF-IDF if user requested keyword match
                    import embeddings.bert_embeddings as embs
                    original_sbert_state = embs.USING_SBERT
                    if "TF-IDF" in model_option:
                        embs.USING_SBERT = False
                    else:
                        embs.USING_SBERT = True
                        
                    embeddings_list = get_embeddings_batch(batch_texts)
                    
                    # Restore global SBERT setting state
                    embs.USING_SBERT = original_sbert_state
                    
                    jd_embedding = embeddings_list[0]
                    resume_embeddings = embeddings_list[1:]
                    
                    # 4. Compute Cosine Similarities
                    for idx, candidate in enumerate(candidates_data):
                        score = calculate_similarity(resume_embeddings[idx], jd_embedding)
                        candidate["similarity_score"] = score
                        
                    # 5. Rank candidates
                    ranked_candidates = rank_candidates(candidates_data)
                    
                    # Filter candidates based on slider minimum score threshold
                    filtered_candidates = [c for c in ranked_candidates if c["similarity_score"] >= min_match_score]
                    excluded_count = len(ranked_candidates) - len(filtered_candidates)
                    
                    # ----------------- RENDER RESULTS -----------------
                    st.success("Analysis Complete!")
                    
                    # Key Summary Metrics
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    
                    top_score = ranked_candidates[0]["similarity_score"] if ranked_candidates else 0.0
                    avg_score = round(np.mean([c["similarity_score"] for c in ranked_candidates]), 2) if ranked_candidates else 0.0
                    model_badge = "SBERT (MiniLM)" if "Sentence-BERT" in model_option and embs.USING_SBERT else "TF-IDF (Sparse)"
                    
                    with col_m1:
                        st.markdown(f"""
                        <div class="custom-metric-card">
                            <div class="custom-metric-value">{len(uploaded_resumes)}</div>
                            <div class="custom-metric-label">Resumes Analyzed</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m2:
                        st.markdown(f"""
                        <div class="custom-metric-card">
                            <div class="custom-metric-value">{top_score}%</div>
                            <div class="custom-metric-label">Top Match Score</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m3:
                        st.markdown(f"""
                        <div class="custom-metric-card">
                            <div class="custom-metric-value">{avg_score}%</div>
                            <div class="custom-metric-label">Average Match</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m4:
                        st.markdown(f"""
                        <div class="custom-metric-card">
                            <div class="custom-metric-value" style="font-size:1.4rem; padding-top:0.3rem;">{model_badge}</div>
                            <div class="custom-metric-label">Active Engine</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.write("")
                    
                    # Warning about filtered candidates
                    if excluded_count > 0:
                        st.warning(f"⚠️ {excluded_count} candidate(s) were excluded because their match scores fell below the {min_match_score}% threshold.")
                    
                    if not filtered_candidates:
                        st.info("No candidates matched the minimum threshold score.")
                    else:
                        # 6. Leaderboard Table
                        st.markdown('<div class="section-title">🏆 Candidate Leaderboard</div>', unsafe_allow_html=True)
                        
                        leaderboard_rows = []
                        for c in filtered_candidates:
                            leaderboard_rows.append({
                                "Rank": c["rank"],
                                "Candidate Name": c["name"],
                                "Match Score": f"{c['similarity_score']}%",
                                "Extracted Experience": c["experience"],
                                "Extracted Education": c["education"],
                                "Skills Matched": len(c["matched_skills"])
                            })
                        
                        leaderboard_df = pd.DataFrame(leaderboard_rows)
                        st.dataframe(
                            leaderboard_df.set_index("Rank"),
                            use_container_width=True
                        )
                        
                        # 7. Detailed Candidate Profiles
                        st.markdown('<div class="section-title">🔍 Detailed Profiles & Interview Assistant</div>', unsafe_allow_html=True)
                        
                        for c in filtered_candidates:
                            # Construct beautiful card headers utilizing rank colors
                            rank_color_class = "rank-1" if c["rank"] == 1 else ("rank-2" if c["rank"] == 2 else ("rank-3" if c["rank"] == 3 else "rank-other"))
                            
                            header_label = f"Rank #{c['rank']} — {c['name']} ({c['similarity_score']}% Match)"
                            
                            with st.expander(header_label, expanded=(c["rank"] == 1)):
                                # Multi-column view for candidate meta details
                                meta_col1, meta_col2, meta_col3 = st.columns(3)
                                with meta_col1:
                                    st.write(f"📊 **Similarity Match Score:** `{c['similarity_score']}%`")
                                    st.write(f"🎓 **Education Level:** `{c['education']}`")
                                with meta_col2:
                                    st.write(f"⏳ **Parsed Experience:** `{c['experience']}`")
                                    # Show threshold comparison status
                                    st.write(f"✅ **Threshold Check:** Pass (>={min_match_score}%)")
                                with meta_col3:
                                    st.write(f"🔑 **Skills Coverage:** `{len(c['matched_skills'])}` matched / `{len(c['missing_skills'])}` missing")
                                
                                st.markdown("---")
                                
                                # Matched vs Missing Skills Badges
                                st.markdown("##### 📌 Skills Analysis")
                                
                                # Display matched skills as green badges
                                st.write("**Matched Skills:**")
                                if c["matched_skills"]:
                                    badges_html = "".join([f'<span class="tag tag-matched">{skill}</span>' for skill in c["matched_skills"]])
                                    st.markdown(badges_html, unsafe_allow_html=True)
                                else:
                                    st.write("*None*")
                                    
                                # Display missing skills as red badges
                                st.write("**Missing Required Skills:**")
                                if c["missing_skills"]:
                                    badges_html = "".join([f'<span class="tag tag-missing">{skill}</span>' for skill in c["missing_skills"]])
                                    st.markdown(badges_html, unsafe_allow_html=True)
                                else:
                                    st.write("*Perfect match! No missing skills.*")
                                    
                                st.markdown("---")
                                
                                # Interview Questions Tabs
                                st.markdown("##### ❓ Tailored Interview Questions")
                                
                                tab_matched, tab_missing = st.tabs([
                                    "Test Candidate Expertise (Matched Skills)", 
                                    "Evaluate Knowledge Gaps (Missing Skills)"
                                ])
                                
                                with tab_matched:
                                    matched_questions = generate_questions_for_skills(c["matched_skills"], max_questions_per_skill=2)
                                    if matched_questions:
                                        st.write("Use these questions to assess depth of experience in areas they have claimed:")
                                        for skill, questions in matched_questions.items():
                                            with st.container():
                                                st.markdown(f"**📚 Questions for {skill}:**")
                                                for q_idx, q in enumerate(questions):
                                                    st.markdown(f"{q_idx + 1}. *{q}*")
                                                st.write("")
                                    else:
                                        st.write("No matched questions found. Try adding key technologies like Python or SQL to the JD.")
                                        
                                with tab_missing:
                                    missing_questions = generate_questions_for_skills(c["missing_skills"], max_questions_per_skill=2)
                                    if missing_questions:
                                        st.write("Use these questions to evaluate if they have basic theoretical knowledge of core requirement gaps:")
                                        for skill, questions in missing_questions.items():
                                            with st.container():
                                                st.markdown(f"**⚠️ Questions for {skill} (Gap):**")
                                                for q_idx, q in enumerate(questions):
                                                    st.markdown(f"{q_idx + 1}. *{q}*")
                                                st.write("")
                                    else:
                                        st.write("No missing questions. The candidate possesses all required skills!")
                                        
                                st.markdown("---")
                                
                                # Parsed plain text snapshot
                                with st.expander("📄 View Extracted Resume Plain Text Snippet"):
                                    st.text_area(
                                        "Extracted Text",
                                        c["raw_text"][:2500] + "\n\n[TRUNCATED FOR VIEWING]",
                                        height=250,
                                        disabled=True
                                    )
                                    
            except Exception as e:
                st.error(f"An error occurred during pipeline execution: {e}")
                st.exception(e)
