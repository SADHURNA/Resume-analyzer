import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skill_extractor import extract_skills_qualifications
from matcher import match_roles


def load_json_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

# Load datasets
job_roles = load_json_data('data/job_roles.json')
study_materials = load_json_data('data/study_materials.json')
certifications = load_json_data('data/certifications.json')
interview_tips = load_json_data('data/interview_tips.json')

# ------------------------ Resume Analyzer ------------------------
def analyze_resume(resume_text):
    if not resume_text.strip():
        return {"error": "Resume is empty or contains only stop words."}

    all_roles = [
        job.get("role", "Unknown Role") + " - " + ", ".join(job.get("skills", []))
        for job in job_roles if isinstance(job, dict)
    ]

    tfidf = TfidfVectorizer()
    try:
        role_vectors = tfidf.fit_transform(all_roles)
        resume_vector = tfidf.transform([resume_text])
    except ValueError:
        return {"error": "Unable to process resume. It may contain only stop words."}

    similarities = cosine_similarity(resume_vector, role_vectors).flatten()
    matched_jobs = [
        {
            "role": job_roles[idx].get("role", "Unknown Role"),
            "accuracy": round(score * 100, 2)
        }
        for idx, score in enumerate(similarities) if score > 0.1
    ]

    matched_jobs = sorted(matched_jobs, key=lambda x: x["accuracy"], reverse=True)
    matched_roles = [job["role"] for job in matched_jobs]

    study_recommendations = recommend_study_materials(matched_roles)
    cert_recommendations = recommend_certification_courses(matched_roles)
    interview_tip_links = recommend_interview_tips(matched_roles)

    return {
        "job_roles": matched_jobs,
        "study_materials": study_recommendations,
        "certifications": cert_recommendations,
        "interview_tips": interview_tip_links
    }

# ------------------------ Recommendation Functions ------------------------

def recommend_study_materials(job_roles):
    material_links = {
        'Data Scientist': [
            'https://www.kaggle.com/learn',
            'https://www.coursera.org/learn/machine-learning',
            'https://towardsdatascience.com/',
            'https://www.datacamp.com/',
            'https://scikit-learn.org/stable/tutorial/index.html',
            'https://machinelearningmastery.com/'
        ],
        'Software Developer': [
            'https://www.geeksforgeeks.org/data-structures/',
            'https://www.w3schools.com/java/',
            'https://developer.mozilla.org/en-US/docs/Web/JavaScript'
        ],
        'Web Developer': [
            'https://www.freecodecamp.org/learn/',
            'https://www.w3schools.com/html/',
            'https://css-tricks.com/'
        ],
        'AI Engineer': [
            'https://www.udacity.com/course/intro-to-artificial-intelligence--cs271',
            'https://www.deeplearning.ai/',
            'https://machinelearningmastery.com/'
        ],
        'Cloud Engineer': [
            'https://www.aws.training/',
            'https://learn.microsoft.com/en-us/training/azure/',
            'https://cloud.google.com/training'
        ],
        'UI/UX Designer': [
            'https://www.interaction-design.org/courses',
            'https://www.coursera.org/specializations/ui-ux-design',
            'https://www.behance.net/galleries/ui-ux'
        ],
        'Machine Learning Engineer': [
            'https://www.kaggle.com/learn/machine-learning',
            'https://www.coursera.org/learn/machine-learning',
            'https://machinelearningmastery.com/'
        ],
        'Network Engineer': [
            'https://www.udemy.com/course/networking-basics/',
            'https://www.cisco.com/',
            'https://www.geeksforgeeks.org/computer-network-tutorials/'
        ],
        'Cyber Security Analyst': [
            'https://www.udemy.com/course/cyber-security-course/',
            'https://www.coursera.org/specializations/cyber-security',
            'https://owasp.org/'
        ],
        'Graphic Designer': [
            'https://www.canva.com/learn/',
            'https://www.adobe.com/creativecloud.html',
            'https://www.skillshare.com/en/browse/graphic-design'
        ],
        'Animator': [
            'https://www.coursera.org/learn/animation',
            'https://www.udemy.com/course/2d-animation/',
            'https://www.blender.org/support/tutorials/'
        ],
        'Content Creator': [
            'https://www.hubspot.com/resources/content-marketing',
            'https://moz.com/blog',
            'https://buffer.com/library/'
        ]
    }

    return {role: material_links[role] for role in job_roles if role in material_links}

def recommend_certification_courses(job_roles):
    course_links = {
        'Data Scientist': [
            'https://www.coursera.org/specializations/jhu-data-science',
            'https://www.udemy.com/course/data-science-and-machine-learning-bootcamp-with-r/',
            'https://www.edx.org/professional-certificate/harvardx-data-science'
        ],
        'Software Developer': [
            'https://www.udemy.com/course/the-complete-java-developer-course/',
            'https://www.edx.org/learn/software-development'
        ],
        'Web Developer': [
            'https://www.coursera.org/specializations/web-design',
            'https://www.udemy.com/course/the-complete-web-developer-zero-to-mastery/'
        ],
        'AI Engineer': [
            'https://www.coursera.org/ai',
            'https://www.edx.org/learn/artificial-intelligence'
        ],
        'Cloud Engineer': [
            'https://www.coursera.org/professional-certificates/google-cloud',
            'https://www.udemy.com/course/aws-certified-solutions-architect-associate/'
        ],
        'UI/UX Designer': [
            'https://www.coursera.org/specializations/ui-ux-design',
            'https://www.udemy.com/course/user-experience-design/'
        ],
        'Machine Learning Engineer': [
            'https://www.coursera.org/learn/machine-learning',
            'https://www.udacity.com/course/intro-to-machine-learning--ud120'
        ],
        'Network Engineer': [
            'https://www.udemy.com/course/cisco-ccna-complete-guide/',
            'https://www.pluralsight.com/paths/networking-fundamentals'
        ],
        'Cyber Security Analyst': [
            'https://www.udemy.com/course/learn-ethical-hacking-from-scratch/',
            'https://www.coursera.org/specializations/ibm-cybersecurity-analyst'
        ],
        'Graphic Designer': [
            'https://www.coursera.org/specializations/graphic-design',
            'https://www.udemy.com/course/graphic-design-masterclass-everything-you-need-to-know/'
        ],
        'Animator': [
            'https://www.coursera.org/specializations/3d-animation',
            'https://www.udemy.com/course/blender-character-creation/'
        ],
        'Content Creator': [
            'https://www.linkedin.com/learning/content-marketing-foundations',
            'https://www.udemy.com/course/content-marketing-masterclass/'
        ]
    }

    return {role: course_links[role] for role in job_roles if role in course_links}

def recommend_interview_tips(job_roles):
    tips_links = {
        'common': [
            'https://www.indiabix.com/aptitude/questions-and-answers/',
            'https://www.geeksforgeeks.org/most-frequently-asked-interview-questions/',
            'https://www.interviewbit.com/hr-interview-questions/'
        ],
        'Data Scientist': ['https://www.kdnuggets.com/2020/07/data-science-interview-questions.html'],
        'Software Developer': ['https://www.interviewbit.com/software-engineering-interview-questions/'],
        'Web Developer': ['https://careerfoundry.com/en/blog/web-development/web-developer-interview-questions/'],
        'AI Engineer': ['https://towardsdatascience.com/ai-machine-learning-interview-questions-answers-2022-8b4a92e1f6fc'],
        'Cloud Engineer': ['https://intellipaat.com/blog/interview-question/cloud-engineer-interview-questions/'],
        'UI/UX Designer': ['https://www.interaction-design.org/literature/topics/ux-design-interview-questions'],
        'Machine Learning Engineer': ['https://www.springboard.com/blog/data-science/machine-learning-interview-questions/'],
        'Network Engineer': ['https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/interview-questions.html'],
        'Cyber Security Analyst': ['https://www.simplilearn.com/cyber-security-interview-questions-article'],
        'Graphic Designer': ['https://www.indeed.com/career-advice/interviewing/graphic-designer-interview-questions'],
        'Animator': ['https://www.indeed.com/career-advice/interviewing/animator-interview-questions'],
        'Content Creator': ['https://www.glassdoor.com/Interview/content-creator-interview-questions-SRCH_KO0,16.htm']
    }

    result = {'common': tips_links['common']}
    for role in job_roles:
        if role in tips_links:
            result[role] = tips_links[role]
    return result