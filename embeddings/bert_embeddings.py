import numpy as np
from typing import List, Union

# Global state to track model availability
USING_SBERT = True
SBERT_MODEL = None

def load_model():
    """
    Loads the Sentence-BERT model ('all-MiniLM-L6-v2').
    Includes caching for Streamlit if available, and falls back to CPU/GPU.
    If downloading/loading fails, sets USING_SBERT to False.
    
    Returns:
        SentenceTransformer model or None if unavailable.
    """
    global SBERT_MODEL, USING_SBERT
    
    if not USING_SBERT:
        return None
        
    if SBERT_MODEL is not None:
        return SBERT_MODEL
        
    try:
        from sentence_transformers import SentenceTransformer
        
        # Try to use Streamlit's cache_resource to keep the model in memory across runs
        try:
            import streamlit as st
            
            @st.cache_resource(show_spinner="Loading Sentence-BERT model ('all-MiniLM-L6-v2')...")
            def get_cached_model():
                return SentenceTransformer('all-MiniLM-L6-v2')
                
            SBERT_MODEL = get_cached_model()
        except Exception:
            # Fallback for scripts or if Streamlit is not active
            SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            
        return SBERT_MODEL
    except Exception as e:
        print(f"Error loading Sentence-BERT model: {e}. Falling back to TF-IDF Vectorization.")
        USING_SBERT = False
        return None

def get_embedding(text: str) -> np.ndarray:
    """
    Generates a semantic embedding vector for a single string.
    
    Args:
        text: Input string.
        
    Returns:
        1D numpy array representing the text embedding.
    """
    global USING_SBERT
    
    if USING_SBERT:
        model = load_model()
        if model is not None:
            try:
                # Handle empty strings
                if not text.strip():
                    return np.zeros(384)  # 384 is the embedding size of all-MiniLM-L6-v2
                return model.encode(text)
            except Exception as e:
                print(f"SBERT single encoding failed: {e}. Switching to TF-IDF.")
                USING_SBERT = False
                
    # Fallback: Fit a simple TF-IDF representation of the single text (not recommended for search,
    # but satisfies the function signature). Use `get_embeddings_batch` for comparing multiple texts.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        matrix = vectorizer.fit_transform([text if text.strip() else " "])
        return np.array(matrix.toarray()[0])
    except Exception:
        return np.zeros(100)

def get_embeddings_batch(texts: List[str]) -> List[np.ndarray]:
    """
    Generates embeddings for a list of strings in batch.
    If Sentence-BERT is active, encodes them semantically.
    If TF-IDF fallback is active, fits a TF-IDF vectorizer across the batch 
    to output aligned feature vectors.
    
    Args:
        texts: List of strings.
        
    Returns:
        List of numpy arrays representing the embeddings.
    """
    global USING_SBERT
    
    # Attempt SBERT encoding
    if USING_SBERT:
        model = load_model()
        if model is not None:
            try:
                cleaned_texts = [t if t.strip() else " " for t in texts]
                embeddings = model.encode(cleaned_texts)
                return [np.array(emb) for emb in embeddings]
            except Exception as e:
                print(f"SBERT batch encoding failed: {e}. Switching to TF-IDF.")
                USING_SBERT = False
                
    # Fallback to TF-IDF Vectorization
    print("Generating embeddings using TF-IDF Vectorizer.")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        return [np.array(vec) for vec in tfidf_matrix.toarray()]
    except Exception as e:
        print(f"TF-IDF batch vectorization failed: {e}.")
        # Absolute fallback: return zero arrays
        return [np.zeros(100) for _ in texts]
