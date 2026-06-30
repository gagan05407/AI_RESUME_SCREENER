import re
from typing import Dict, List, Any

# Extensive skill database with alias mappings to normalize extraction
SKILLS_DB = {
    "Python": [r"\bpython\d?\b"],
    "Java": [r"\bjava\b(?!script)"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b", r"\bsqlite\b", r"\boracle sql\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b", r"\bpredictive modeling\b"],
    "Deep Learning": [r"\bdeep learning\b", r"\bdl\b", r"\bneural networks\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "PyTorch": [r"\bpytorch\b"],
    "Docker": [r"\bdocker\b", r"\bcontainerization\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b", r"\bgoogle cloud platform\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft azure\b"],
    "Flask": [r"\bflask\b"],
    "Streamlit": [r"\bstreamlit\b"],
    "React": [r"\breact\b", r"\breact\.js\b", r"\breactjs\b"],
    "Node.js": [r"\bnode\.?js\b", r"\bnode\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "HTML": [r"\bhtml\d?\b"],
    "CSS": [r"\bcss\d?\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Django": [r"\bdjango\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Scikit-Learn": [r"\bscikit-learn\b", r"\bsklearn\b"],
    "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
    "BERT": [r"\bbert\b"],
    "LLM": [r"\bllm\b", r"\blarge language models?\b"],
    "LangChain": [r"\blangchain\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"]
}

# Case-sensitive patterns for skills that are short words to prevent false positives (e.g. "Go" or "R")
CASE_SENSITIVE_SKILLS = {
    "Go": [r"\bGo\b", r"\bgolang\b"],
    "R": [r"\bR\b"]
}

def extract_skills(text: str) -> List[str]:
    """
    Extracts standardized skills from the resume or job description text.
    
    Args:
        text: Normalized text source.
        
    Returns:
        List of matching skill names.
    """
    matched_skills = set()
    text_lower = text.lower()
    
    # Check case-insensitive patterns
    for skill, patterns in SKILLS_DB.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matched_skills.add(skill)
                break
                
    # Check case-sensitive patterns
    for skill, patterns in CASE_SENSITIVE_SKILLS.items():
        for pattern in patterns:
            # If the pattern contains uppercase letters, run it directly without lowercasing
            if re.search(pattern, text):
                matched_skills.add(skill)
                break
                
    return sorted(list(matched_skills))

def extract_education(text: str) -> str:
    """
    Extracts educational degrees from the resume text.
    
    Args:
        text: Raw resume text.
        
    Returns:
        String representing the highest degree extracted.
    """
    education_hierarchy = [
        (r"\b(?:Ph\.?D\.?|Doctor of Philosophy)\b", "Ph.D."),
        (r"\b(?:M\.?Tech|M\.?E\.?|M\.?S\.?|Master of Science|Master of Technology|M\.?C\.?A\.?|M\.?B\.?A\.?|M\.?Sc)\b", "Master's Degree"),
        (r"\b(?:B\.?Tech|B\.?E\.?|B\.?S\.?|Bachelor of Science|Bachelor of Technology|B\.?C\.?A\.?|B\.?B\.?A\.?|B\.?Sc)\b", "Bachelor's Degree"),
        (r"\b(?:Diploma|Associate's? Degree)\b", "Associate/Diploma")
    ]
    
    # Search in order of hierarchy (highest first)
    for pattern, degree_label in education_hierarchy:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Let's get specific if possible
            match_str = matches[0].upper().replace(".", "").strip()
            if "PHD" in match_str or "PHILOSOPHY" in match_str:
                return "Ph.D."
            elif "MTECH" in match_str:
                return "M.Tech"
            elif "BTECH" in match_str:
                return "B.Tech"
            elif "MCA" in match_str:
                return "MCA"
            elif "MBA" in match_str:
                return "MBA"
            elif "MSC" in match_str:
                return "M.Sc"
            elif "BSC" in match_str:
                return "B.Sc"
            elif "BCA" in match_str:
                return "BCA"
            elif "MS" in match_str:
                return "M.S."
            elif "BS" in match_str:
                return "B.S."
            else:
                return degree_label
                
    return "Not Specified"

def extract_experience(text: str) -> str:
    """
    Extracts years of professional experience from the resume text.
    Uses pattern matching for experience declarations and checks date intervals.
    
    Args:
        text: Raw resume text.
        
    Returns:
        Formatted experience string (e.g. "3 Years").
    """
    # 1. Pattern matching for phrases like "3+ years of experience"
    phrase_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:professional|relevant|work|direct)?\s+experience",
        r"experience\s*:\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\s+in\b",
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\s+(?:working|active|professional)"
    ]
    
    found_years = []
    for pattern in phrase_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if 0.5 <= val < 40:  # Sanity bounds check
                    found_years.append(val)
            except ValueError:
                continue
                
    if found_years:
        max_val = max(found_years)
        if max_val.is_integer():
            return f"{int(max_val)} Years"
        return f"{max_val} Years"
        
    # 2. Date intervals fallback (e.g., 2018 - 2023, 2021 - Present)
    date_matches = re.findall(r"\b(20\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)\b", text, re.IGNORECASE)
    total_duration = 0.0
    current_year = 2026 # Local time metadata anchor
    
    for start, end in date_matches:
        try:
            start_yr = int(start)
            if end.lower() in ["present", "current", "now"]:
                end_yr = current_year
            else:
                end_yr = int(end)
                
            duration = end_yr - start_yr
            if 0 < duration <= 15:
                total_duration += duration
        except ValueError:
            continue
            
    if total_duration > 0:
        if total_duration.is_integer():
            return f"{int(total_duration)} Years"
        return f"{total_duration} Years"
        
    return "0 Years"

def extract_all_info(text: str) -> Dict[str, Any]:
    """
    Performs complete extraction of skills, education, and experience.
    
    Args:
        text: Raw resume text.
        
    Returns:
        Structured dictionary.
    """
    return {
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text)
    }
