from typing import List, Dict

# Complete Interview Question Bank with high-quality conceptual and practical questions
QUESTION_BANK = {
    "Python": [
        "What is the difference between a list and a tuple? When would you use one over the other for memory or execution optimization?",
        "Explain Python's memory management mechanism, specifically reference counting and the garbage collector.",
        "What are decorators in Python, and how would you construct a custom decorator that accepts arguments?",
        "How do generators work? Explain the 'yield' keyword and how it contributes to writing memory-efficient applications.",
        "Compare shallow copy and deep copy in Python. When does a shallow copy cause unexpected side effects?"
    ],
    "SQL": [
        "Explain the differences between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN, including NULL handling behavior.",
        "What is database normalization? Describe the requirements of 1NF, 2NF, and 3NF with a brief conceptual database design.",
        "How do database indexes (e.g., B-Trees) speed up queries, and what are the overhead costs of excessive indexing?",
        "What is SQL Injection, and what strategies (such as parameterized queries or ORMs) should be used to protect a Python backend?",
        "Compare the 'WHERE' clause and the 'HAVING' clause in terms of SQL query execution order."
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff. How does overfitting affect model generalization, and how can regularization address it?",
        "How does a Random Forest model work? Explain bagging, feature bootstrap sampling, and out-of-bag evaluation.",
        "What evaluation metrics are appropriate for a binary classifier where classes are extremely imbalanced (e.g., 99% negative, 1% positive)?",
        "Describe the mathematical intuition behind Gradient Descent and the role of the learning rate. What happens if the learning rate is too large or too small?",
        "What is feature scaling (e.g., standardization vs. normalization)? Explain why scaling is critical for distance-based models but optional for tree-based models."
    ],
    "Deep Learning": [
        "What is the vanishing/exploding gradient problem in deep neural networks? Explain how activation functions like ReLU and ResNet skip connections mitigate it.",
        "Compare Convolutional Neural Networks (CNNs) and Recurrent Neural Networks (RNNs) in terms of architectural design, spatial/temporal processing, and common use cases.",
        "Explain Dropout and Batch Normalization. How do their behaviors differ during model training versus model evaluation (inference)?",
        "Compare SGD, RMSprop, and Adam optimizers. What are the advantages of using adaptive learning rate algorithms?",
        "Describe the self-attention mechanism in the Transformer architecture. Why does it scale better for parallelization than sequential models?"
    ],
    "Docker": [
        "What is the fundamental difference between a virtual machine (VM) and a Docker container in terms of resource allocation and kernel sharing?",
        "Explain how multi-stage builds work in a Dockerfile and how they help in optimizing the size of production images.",
        "What are Docker volumes, and how do they differ from bind mounts? How do you achieve data persistence in stateless containers?",
        "What is Docker Compose, and how does it configure and orchestrate multi-container microservice applications?",
        "Explain the difference between a Docker image layer and a running container. How does copy-on-write work?"
    ],
    "AWS": [
        "Compare Amazon EC2, AWS Lambda, and Amazon Elastic Container Service (ECS) in terms of server management, cost structure, and scaling behavior.",
        "What is AWS IAM? Explain the 'Principle of Least Privilege' and how IAM Roles differ from IAM Users.",
        "What is Amazon S3? How do storage tiers (e.g., Standard, Glacier) help manage cloud storage costs, and how do you secure S3 buckets?",
        "Explain the key architectural components of an AWS VPC (Virtual Private Cloud), including Subnets, Route Tables, Internet Gateways, and Security Groups.",
        "How do Security Groups differ from Network Access Control Lists (NACLs) in AWS network security?"
    ],
    "Flask": [
        "Explain the request lifecycle in a Flask application. What is the role of request context and application context?",
        "What are Flask Blueprints, and how do they assist in structuring and scaling a medium-to-large web application codebase?",
        "How do you implement database migration in a Flask app, and what is the role of libraries like Flask-SQLAlchemy and Alembic?",
        "Describe how to secure REST endpoints in a Flask application. How would you handle session management vs. token-based auth (JWT)?",
        "Explain how CORS (Cross-Origin Resource Sharing) issues arise in a Flask backend connected to a frontend like React, and how to resolve them."
    ],
    "Streamlit": [
        "How does Streamlit's execution model work? What happens to the script variables when a user clicks a button or interacts with a slider?",
        "Explain the difference between `st.cache_data` and `st.cache_resource` in Streamlit. In what scenarios would you use each?",
        "How do you manage application state across different user interaction cycles in Streamlit? Provide an example utilizing `st.session_state`.",
        "How can you customize the layout and look-and-feel of a Streamlit app beyond standard widgets (e.g., layout configurations, custom CSS)?",
        "What are the best practices for scaling and deploying a Streamlit application to handle concurrent user sessions?"
    ],
    "React": [
        "What is the Virtual DOM, and how does React use the reconciliation algorithm to optimize UI rendering?",
        "Describe the rules of React Hooks. Explain the difference between state updates in `useState` and side-effects in `useEffect`.",
        "How do you manage global state in React? Compare the Context API, Redux Toolkit, and lightweight state managers like Zustand."
    ],
    "Node.js": [
        "Explain the event-driven, non-blocking I/O model in Node.js. How does the event loop execute asynchronous code?",
        "What are Node.js Streams, and why are they preferred for processing large datasets (like files or network payloads)?",
        "How does middleware architecture function in Express.js? Explain the role of the `next()` callback."
    ],
    "Kubernetes": [
        "What is a Pod in Kubernetes, and why do containers inside the same Pod share network namespaces and storage volumes?",
        "Describe the difference between a Deployment, a StatefulSet, and a DaemonSet in Kubernetes cluster scheduling.",
        "What is a Kubernetes Service? Explain ClusterIP, NodePort, and LoadBalancer configurations."
    ],
    "Git": [
        "Compare `git merge` and `git rebase`. What are the trade-offs of having a clean linear history vs. preserving exact commit timelines?",
        "What does `git reset` do? Contrast the behavior of the `--soft`, `--mixed`, and `--hard` flags.",
        "How do you identify, analyze, and resolve a merge conflict in Git?"
    ],
    "NLP": [
        "Explain tokenization, stemming, and lemmatization. Why is lemmatization generally preferred for semantic processing?",
        "How does the TF-IDF algorithm represent text? Describe the math behind term frequency and inverse document frequency.",
        "What are word embeddings? Explain how Word2Vec represents semantic similarity in a vector space."
    ],
    "LLM": [
        "Compare Retrieval-Augmented Generation (RAG) and Fine-Tuning. In what scenarios is RAG superior for updating LLM knowledge?",
        "Explain how the 'temperature' parameter governs the probability distribution of generated tokens in LLM sampling.",
        "What is prompt injection? What strategies can you employ to protect LLM-powered applications from malicious user inputs?"
    ]
}

def generate_questions_for_skills(skills: List[str], max_questions_per_skill: int = 3) -> Dict[str, List[str]]:
    """
    Extracts custom interview questions based on the candidate's skills.
    
    Args:
        skills: List of extracted skills.
        max_questions_per_skill: Maximum questions to retrieve per matched skill.
        
    Returns:
        Dictionary mapping skills to lists of interview questions.
    """
    matched_questions = {}
    
    for skill in skills:
        # Match case-insensitively
        found_key = None
        for key in QUESTION_BANK.keys():
            if key.lower() == skill.lower():
                found_key = key
                break
                
        if found_key:
            questions = QUESTION_BANK[found_key]
            # Take a slice of the questions up to the max requested
            matched_questions[found_key] = questions[:max_questions_per_skill]
            
    return matched_questions
