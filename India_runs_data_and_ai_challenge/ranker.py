import json
import math
from datetime import datetime, date

# Scoring weights derived from JD analysis.
# Career history is the strongest signal: skills lists are unreliable
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


