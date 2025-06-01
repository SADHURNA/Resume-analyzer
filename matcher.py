# matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('all-MiniLM-L6-v2')


def load_job_roles():
    with open(os.path.join('data', 'job_roles.json'), encoding='utf-8') as f:
        return json.load(f)

def match_roles(skills, qualifications):
    user_text = ' '.join(skills + qualifications)
    job_roles = load_job_roles()

    corpus = [user_text] + [role.get("description", "") for role in job_roles]
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform(corpus)
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    roles = match_roles(skills, qualifications)
    print("🎯 Matched Roles:", roles)
    job_roles = [
        "Data Scientist",
        "Web Developer",
        "AI Engineer",
        "System Analyst",
        "Software Developer",
        "Network Engineer",
        "Cloud Engineer"
    ]

    combined_profile = " ".join(skills + qualifications)
    sentences = [combined_profile] + job_roles

    vectors = model.encode(sentences)
    cosine_sim = cosine_similarity([vectors[0]], vectors[1:]).flatten()

    matched_roles = [job_roles[i] for i in cosine_sim.argsort()[::-1][:3]]
    

    ranked_roles = sorted(zip(job_roles, cosine_sim), key=lambda x: x[1], reverse=True)
    return [
        {
            "role": r.get("title", "Unknown"),
            "accuracy": round(score * 100, 2)
        }
        for r, score in ranked_roles if score > 0.1
    ]
# matcher.py

# Define sample rol
ROLE_DATABASE = {
    'Web Developer': ['html', 'css', 'javascript', 'flask', 'django'],
    'Data Scientist': ['python', 'machine learning', 'sql', 'pandas', 'numpy', 'statistics'],
    'Backend Developer': ['node.js', 'sql', 'flask', 'django', 'python', 'api', 'database', 'backend server', 'c'],
    'Frontend Developer': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'bootstrap'],
    'Data Analyst': ['python', 'sql', 'excel', 'tableau', 'pandas', 'data analysis', 'visualization', 'powerbi'],
    'Full Stack Developer': ['html', 'css', 'javascript', 'python', 'flask', 'node.js', 'sql', 'react', 'frontend', 'backend'],
    'Machine Learning Engineer': ['python', 'tensorflow', 'sklearn', 'pandas', 'numpy', 'machine learning', 'ai model training', 'deep learning'],
    'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'ci', 'cd', 'linux', 'git', 'devops', 'automation', 'jenkins'],
    'UI/UX Designer': ['ui', 'ux', 'figma', 'adobe', 'design', 'wireframe', 'user experience', 'prototyping'],
    'Network Engineer': ['networking', 'tcp/ip', 'dns', 'routing', 'switching', 'firewall', 'cisco', 'subnetting'],
    'Cyber Security Analyst': ['cybersecurity', 'ethical hacking', 'penetration testing', 'vulnerability assessment', 'network security', 'encryption', 'firewall'],
    'Graphic Designer': ['photoshop', 'illustrator', 'coreldraw', 'indesign', 'graphics', 'visual design', 'typography'],
    'Animator': ['animation', 'after effects', 'maya', 'blender', '2d animation', '3d modeling', 'motion graphics'],
    'Content Creator': ['content writing', 'seo', 'blogging', 'copywriting', 'social media', 'script writing', 'storytelling'],
    'Software Developer': ['java', 'python', 'c++', 'c#', '.net', 'oop', 'data structures', 'algorithms', 'software engineering']
}


def match_roles(skills, qualifications):
    results = {}

    for role, role_skills in ROLE_DATABASE.items():
        matched = set(skills).intersection(role_skills)
        if matched:
            score = round((len(matched) / len(role_skills)) * 100, 2)
            results[role] = score

    return results
