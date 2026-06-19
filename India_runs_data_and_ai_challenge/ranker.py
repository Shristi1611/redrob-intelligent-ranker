import json
import math
from datetime import datetime, date

# Scoring weights derived from JD analysis.
# Career history is the strongest signal — skills lists are unreliable
# as candidates frequently list aspirational rather than demonstrated skills.
WEIGHTS = {
    'career':     0.40,
    'skills':     0.25,
    'behavioral': 0.20,
    'experience': 0.10,
    'profile':    0.05,
}

CONSULTING_FIRMS = [
    'tcs', 'infosys', 'wipro', 'accenture', 'cognizant',
    'mindtree', 'capgemini', 'hcl', 'mphasis'
]

CORE_SKILLS = [
    'embeddings', 'vector', 'qdrant', 'pinecone', 'faiss',
    'elasticsearch', 'weaviate', 'milvus', 'retrieval', 'ranking',
    'nlp', 'llm', 'machine learning', 'deep learning', 'pytorch',
    'transformers', 'sentence-transformers', 'fine-tuning', 'rag',
    'recommendation', 'search', 'reranking', 'hybrid search'
]

PRODUCTION_ML_KEYWORDS = [
    'deployed', 'production', 'retrieval', 'embedding', 'vector',
    'ranking', 'recommendation', 'search', 'nlp', 'llm', 'built',
    'shipped', 'scaled', 'latency', 'inference', 'fine-tun',
    'rerank', 'semantic', 'index', 'pipeline'
]

STRONG_TITLES = [
    'ml engineer', 'machine learning engineer', 'ai engineer',
    'nlp engineer', 'search engineer', 'recommendation',
    'applied scientist', 'research engineer', 'data scientist',
    'ranking engineer', 'retrieval'
]

WEAK_TITLES = [
    'marketing', 'accountant', 'civil', 'mechanical', 'graphic',
    'hr manager', 'operations manager', 'customer support',
    'business analyst', 'project manager', 'content writer',
    'frontend', 'mobile developer', '.net'
]


def is_honeypot(candidate):
    """
    Identifies synthetic trap profiles embedded in the dataset.
    """
    for skill in candidate['skills']:
        if skill['proficiency'] == 'expert' and skill.get('duration_months', 1) == 0:
            return True

    years = candidate['profile']['years_of_experience']
    if years < 0 or years > 50:
        return True

    return False


def score_career(candidate):
    """
    Scores fit based on job title and career description content.
    """
    score = 0.0
    profile = candidate['profile']
    career = candidate['career_history']

    current_title = profile['current_title'].lower()

    if any(t in current_title for t in STRONG_TITLES):
        score += 0.4

    if any(t in current_title for t in WEAK_TITLES):
        score -= 0.3

    career_text = ' '.join([j['description'].lower() for j in career])
    keyword_hits = sum(1 for k in PRODUCTION_ML_KEYWORDS if k in career_text)
    score += min(keyword_hits / 8.0, 0.4)

    all_companies = [j['company'].lower() for j in career]
    all_consulting = all(
        any(firm in co for firm in CONSULTING_FIRMS)
        for co in all_companies
    )
    if all_consulting:
        score -= 0.2

    return max(0.0, min(1.0, score))


def score_skills(candidate):
    """
    Scores relevant skill coverage weighted by proficiency level
    and usage duration.
    """
    score = 0.0
    skills = candidate['skills']

    proficiency_weights = {
        'beginner':     0.25,
        'intermediate': 0.5,
        'advanced':     0.75,
        'expert':       1.0
    }

    for skill in skills:
        name = skill['name'].lower()
        if any(core in name for core in CORE_SKILLS):
            prof_weight = proficiency_weights.get(skill['proficiency'], 0.5)
            duration_bonus = min(skill.get('duration_months', 0) / 36, 1.0)
            score += prof_weight * (0.7 + 0.3 * duration_bonus)

    return min(score / 5.0, 1.0)

