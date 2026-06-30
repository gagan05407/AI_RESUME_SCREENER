import numpy as np

def calculate_similarity(resume_embedding: np.ndarray, jd_embedding: np.ndarray) -> float:
    """
    Calculates the cosine similarity between a resume embedding and a job description embedding.
    Converts the score to a percentage scale [0, 100].
    
    Args:
        resume_embedding: 1D numpy array representing the resume embedding.
        jd_embedding: 1D numpy array representing the JD embedding.
        
    Returns:
        Float value between 0.0 and 100.0.
    """
    # Safety checks for empty or invalid arrays
    if resume_embedding is None or jd_embedding is None:
        return 0.0
        
    # Handle dimensionality mismatch gracefully (e.g. from dynamic TF-IDF fitting)
    if resume_embedding.shape != jd_embedding.shape:
        min_dim = min(resume_embedding.shape[0], jd_embedding.shape[0])
        if min_dim == 0:
            return 0.0
        resume_embedding = resume_embedding[:min_dim]
        jd_embedding = jd_embedding[:min_dim]
        
    dot_product = np.dot(resume_embedding, jd_embedding)
    norm_resume = np.linalg.norm(resume_embedding)
    norm_jd = np.linalg.norm(jd_embedding)
    
    if norm_resume == 0.0 or norm_jd == 0.0:
        return 0.0
        
    cosine_similarity = dot_product / (norm_resume * norm_jd)
    
    # Clip cosine similarity to [0.0, 1.0] since negative correlation is irrelevant for matching
    percentage_score = float(np.clip(cosine_similarity, 0.0, 1.0) * 100.0)
    return round(percentage_score, 2)
