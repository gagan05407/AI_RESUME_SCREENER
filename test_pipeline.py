import os
import sys

def main():
    print("=== Testing AI Resume Screener Pipeline CLI ===")
    
    # Verify imports
    try:
        from resume_parser import parse_resume, extract_all_info
        from jd_processing import parse_jd
        from embeddings import get_embeddings_batch, USING_SBERT
        from ranking import calculate_similarity, rank_candidates
        from interview_generator import generate_questions_for_skills
        print("[SUCCESS] Imports successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)
        
    # Check data files
    jd_file = "data/job_descriptions/ml_engineer_jd.txt"
    resume_file = "data/resumes/john_doe_ml_engineer.docx"
    
    if not os.path.exists(jd_file) or not os.path.exists(resume_file):
        print("[ERROR] Sample data files not found. Run generate_sample_data.py first.")
        sys.exit(1)
        
    print("[SUCCESS] Sample data files found!")
    
    # 1. Parse JD
    print("\n1. Parsing Job Description...")
    with open(jd_file, "r", encoding="utf-8") as f:
        jd_raw = f.read()
    jd_info = parse_jd(jd_raw)
    print(f"   Required Skills: {jd_info['required_skills']}")
    print(f"   Preferred Skills: {jd_info['preferred_skills']}")
    print(f"   Experience Required: {jd_info['experience']}")
    print(f"   Education Required: {jd_info['education']}")
    
    # 2. Parse Resume
    print("\n2. Parsing Candidate Resume...")
    resume_raw = parse_resume(resume_file)
    resume_info = extract_all_info(resume_raw)
    print(f"   Extracted Candidate Skills: {resume_info['skills']}")
    print(f"   Extracted Candidate Experience: {resume_info['experience']}")
    print(f"   Extracted Candidate Education: {resume_info['education']}")
    
    # Calculate overlaps
    jd_req = set(jd_info["required_skills"])
    jd_pref = set(jd_info["preferred_skills"])
    cand_skills = set(resume_info["skills"])
    
    matched = sorted(list(cand_skills.intersection(jd_req.union(jd_pref))))
    missing = sorted(list(jd_req.difference(cand_skills)))
    
    print(f"   Matched Skills: {matched}")
    print(f"   Missing Required Skills: {missing}")
    
    # 3. Generate Embeddings & Similarity
    print("\n3. Generating Embeddings & Similarity Score...")
    # Standardize to batch encoding
    batch = [jd_raw, resume_raw]
    
    try:
        embs = get_embeddings_batch(batch)
        score = calculate_similarity(embs[1], embs[0])
        print(f"   Similarity Match Score: {score}%")
    except Exception as e:
        print(f"[ERROR] Embedding computation failed: {e}")
        sys.exit(1)
        
    # 4. Generate Interview Questions
    print("\n4. Generating Interview Questions...")
    questions = generate_questions_for_skills(matched, max_questions_per_skill=2)
    for skill, q_list in questions.items():
        print(f"   Questions for {skill}:")
        for q in q_list:
            # Strip non-ASCII characters if any in questions
            q_clean = q.encode('ascii', 'ignore').decode('ascii')
            print(f"     - {q_clean}")
            
    print("\n=== CLI Pipeline Test Completed Successfully! ===")

if __name__ == "__main__":
    main()
