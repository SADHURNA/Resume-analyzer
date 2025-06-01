import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define skill and qualification keywords (expand as needed)
SKILL_KEYWORDS = [
    'python', 'java', 'html', 'css', 'javascript', 'node.js','swift','php','reactjs','angular','vue.js','express.js',
    'bootstarp','jquery','restapi','json','android','java(android)','flutter','dart','reactnative','swift(ios)','mysql',
    'postgresql','mangodb','sqlite','oracle','redis','firebase','business analysis','software testing','system design','ui ux design','technical writing',
    'c', 'sql', 'machine learning', 'flask', 'django','c++','c#','typescript','go','kotlin','R','matlab','ruby',
    'cassandra','numpy','pandas','scikit-learn','tensorflow','keras','pytorch','matplotlib','seaborn','opencv',
    'NLTK','spacy','transformers','jupyter','data Wrangling','data visualization','model deployment','aws','azure',
    'google cloud(gcp)','docker','kubernetes','jenkins','git','github','gitlab','ci/cd','terraform',
    'vscode','visual studio code','jira','trello','figma','adobe xd',"canva",'postman','selenium','powerbi','tableau',
    'ethical hacking','penetration testing','network security','kali linux','wireshark','metasploit','burp suite','firewall',
]

QUALIFICATIONS_KEYWORDS = [
    'b.e', 'b.tech', 'm.tech', 'mca', 'b.sc', 'msc', 'diploma'
]

def extract_skills_qualifications(text):
    text = text.lower()
    doc = nlp(text)

    skills = set()
    qualifications = set()

    # Use full text matching for multi-word keywords
    for phrase in SKILL_KEYWORDS:
        if phrase in text:
            skills.add(phrase)

    for qual in QUALIFICATIONS_KEYWORDS:
        if qual in text:
            qualifications.add(qual)

    return list(skills), list(qualifications)
