import re
from typing import Dict, List, Any
from resume_parser.skill_extractor import extract_skills, extract_experience, extract_education

def extract_experience_requirement(text: str) -> str:
    """
    Extracts the years of experience requirement from the Job Description text.
    
    Args:
        text: Raw job description text.
        
    Returns:
        Formatted experience requirement.
    """
    # Patterns for experience requirements in JD (e.g. "at least 3 years", "5+ years required")
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:professional|relevant|work|direct)?\s+experience\s+(?:required|needed|desired|preferred|mandatory)",
        r"(?:minimum|at least|require|prefer|need|expect)\s+(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:professional|relevant|work|direct)?\s+experience"
    ]
    
    found_years = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if 0.5 <= val < 30:  # Sanity check for experience requirement
                    found_years.append(val)
            except ValueError:
                continue
                
    if found_years:
        min_val = min(found_years)  # Usually the minimum required is the lowest number mentioned in requirements
        if min_val.is_integer():
            return f"{int(min_val)} Years"
        return f"{min_val} Years"
        
    # Check general experience parsing fallback
    general_exp = extract_experience(text)
    if general_exp != "0 Years" and general_exp != "Not Specified":
        return general_exp
        
    return "0 Years (Entry Level)"

def parse_jd(text: str) -> Dict[str, Any]:
    """
    Parses Job Description text and categorizes requirements:
    - Required skills
    - Preferred skills
    - Experience requirements
    - Education requirements
    
    Args:
        text: Raw job description text.
        
    Returns:
        Structured dictionary.
    """
    all_skills = extract_skills(text)
    
    # Section keywords to split required vs preferred skills
    preferred_keywords = [
        r"\bpreferred\b", r"\bdesired\b", r"\bnice to have\b", 
        r"\bplus\b", r"\boptional\b", r"\badvantages?\b", r"\bassets?\b"
    ]
    
    required_skills = []
    preferred_skills = []
    
    # Perform section parsing by scanning line-by-line
    lines = text.split("\n")
    current_section = "required"  # Default section
    
    for line in lines:
        line_lower = line.lower()
        
        # Check transition to preferred section
        is_pref_header = any(re.search(kw, line_lower) for kw in preferred_keywords)
        # Check transition to required section
        is_req_header = any(kw in line_lower for kw in ["required", "requirements", "must have", "qualifications", "education", "experience", "essential"])
        
        if is_pref_header and not is_req_header:
            current_section = "preferred"
        elif is_req_header:
            current_section = "required"
            
        line_skills = extract_skills(line)
        for s in line_skills:
            if current_section == "preferred":
                preferred_skills.append(s)
            else:
                required_skills.append(s)
                
    # Deduplicate and sort
    required_skills = sorted(list(set(required_skills)))
    preferred_skills = sorted(list(set(preferred_skills)))
    
    # A skill cannot be both, prioritize required
    preferred_skills = [s for s in preferred_skills if s not in required_skills]
    
    # If required_skills is empty but we extracted general skills, default them to required
    if not required_skills and all_skills:
        required_skills = all_skills
        preferred_skills = []
        
    experience_req = extract_experience_requirement(text)
    education_req = extract_education(text)
    
    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience": experience_req,
        "education": education_req
    }
