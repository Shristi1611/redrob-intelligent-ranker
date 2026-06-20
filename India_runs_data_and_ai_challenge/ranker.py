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
    'mindtree', 'capgemini', 'hcl', 'mphasis', 'tech mahindra'
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
    Honeypots contain logically impossible attribute combinations
    and are assigned relevance tier 0 in the ground truth.
    Submissions ranking >10% honeypots in top-100 are disqualified.
    """
    for skill in candidate['skills']:
        if skill['proficiency'] == 'expert' and skill.get('duration_months', 1) == 0:
            return True

    years = candidate['profile']['years_of_experience']
    if years < 0 or years > 50:
        return True

    # Cross-validate stated years_of_experience against summed career_history
    # duration. Found via manual inspection of suspicious top-ranked candidates
    # (e.g. profile stating 16.2yrs while career_history sums to ~8.2yrs, with
    # the profile summary itself matching the LOWER, correct figure). A profile
    # whose stated experience diverges significantly from its own career
    # history, in either direction, indicates a data-consistency trap rather
    # than a genuine candidate.
    total_months = sum(j.get('duration_months', 0) for j in candidate['career_history'])
    implied_years = total_months / 12
    if implied_years > 0:
        ratio = years / implied_years
        if ratio > 1.6 or ratio < 0.6:
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

    # Penalize based on CURRENT employer, not full career history.
    # The original check only fired if every past job was at a consulting
    # firm, which missed candidates currently at one with a mixed history.
    current_company = profile['current_company'].lower()
    currently_at_consulting = any(firm in current_company for firm in CONSULTING_FIRMS)
    if currently_at_consulting:
        score -= 0.4

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


def score_behavioral(candidate):
    """
    Scores candidate availability and platform engagement.
    """
    sig = candidate['redrob_signals']
    score = 0.0

    if sig['open_to_work_flag']:
        score += 0.2

    try:
        last_active = datetime.strptime(sig['last_active_date'], '%Y-%m-%d')
        days_inactive = (datetime.now() - last_active).days
        if days_inactive <= 30:
            score += 0.2
        elif days_inactive <= 90:
            score += 0.1
        elif days_inactive <= 180:
            score += 0.05
    except Exception:
        pass

    score += sig['recruiter_response_rate'] * 0.3

    notice = sig['notice_period_days']
    if notice <= 30:
        score += 0.2
    elif notice <= 60:
        score += 0.1

    score += sig['interview_completion_rate'] * 0.1

    return max(0.0, min(1.0, score))


def score_experience(candidate):
    """
    Scores years of experience against the JD target band of 5-9 years.
    """
    years = candidate['profile']['years_of_experience']

    if 5 <= years <= 9:
        return 1.0
    elif 4 <= years < 5:
        return 0.7
    elif 9 < years <= 11:
        return 0.6
    elif 11 < years <= 13:
        return 0.3
    else:
        return 0.1


def score_profile(candidate):
    """
    Scores profile completeness and verification signals.
    """
    sig = candidate['redrob_signals']
    score = 0.0

    if sig['verified_email']:
        score += 0.2
    if sig['verified_phone']:
        score += 0.2
    if sig['linkedin_connected']:
        score += 0.1

    score += (sig['profile_completeness_score'] / 100) * 0.3

    gh = sig['github_activity_score']
    if gh > 0:
        score += (gh / 100) * 0.2

    return min(score, 1.0)


def generate_reasoning(candidate, scores):
    """
    Produces a specific, fact-grounded reasoning string for each ranked candidate.
    """
    p = candidate['profile']
    sig = candidate['redrob_signals']

    title = p['current_title']
    years = p['years_of_experience']
    company = p['current_company']
    resp = sig['recruiter_response_rate']
    notice = sig['notice_period_days']
    gh = sig['github_activity_score']

    parts = []
    parts.append(f"{title} with {years}yr at {company}")

    if scores['career'] < 0.15:
        parts.append("career history shows limited evidence of production ML/AI work relevant to this role")

    top_skills = [
        s['name'] for s in candidate['skills']
        if any(c in s['name'].lower() for c in CORE_SKILLS)
    ][:3]

    if top_skills:
        parts.append(f"relevant skills: {', '.join(top_skills)}")

    if resp >= 0.7:
        parts.append(f"strong engagement ({resp:.0%} response rate)")
    elif resp < 0.3:
        parts.append(f"low response rate ({resp:.0%}) is a concern")

    if notice <= 30:
        parts.append(f"available immediately (notice: {notice}d)")
    elif notice > 90:
        parts.append(f"long notice period ({notice}d) reduces fit")

    if gh > 50:
        parts.append(f"active GitHub (score: {gh:.0f})")

    return '; '.join(parts) + '.'


def rank_candidates(candidates):
    """
    Main ranking pipeline. Scores each candidate across five dimensions,
    applies weighted aggregation, filters honeypots, and returns
    a sorted list with ranks assigned.
    """
    results = []

    for c in candidates:
        if is_honeypot(c):
            continue

        career_score = score_career(c)

        # Discount skills score if career history shows no production ML work.
        # This penalises keyword stuffing — skills listed without demonstrated use.
        # A career_score of exactly 0 gets a near-total discount, since at that
        # point the listed skills have no supporting evidence at all.
        raw_skills = score_skills(c)
        if career_score == 0:
            career_multiplier = 0.05
        else:
            career_multiplier = 0.3 + 0.7 * career_score
        discounted_skills = raw_skills * career_multiplier

        scores = {
            'career':     career_score,
            'skills':     discounted_skills,
            'behavioral': score_behavioral(c),
            'experience': score_experience(c),
            'profile':    score_profile(c),
        }

        weighted_sum = sum(WEIGHTS[k] * scores[k] for k in WEIGHTS)

        # Career relevance also gates the FINAL score. A candidate with
        # near-zero career fit should not be competitive even with strong
        # behavioral signals, since behavioral/profile scores alone don't
        # indicate role fit.
        career_gate = 0.2 + 0.8 * career_score
        final = weighted_sum * career_gate

        results.append({
            'candidate_id': c['candidate_id'],
            'score':        round(final, 4),
            'scores':       scores,
            'reasoning':    generate_reasoning(c, scores)
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    for i, r in enumerate(results):
        r['rank'] = i + 1

    return results

def load_candidates_jsonl(filepath):
    """
    Loads the full candidate pool from JSONL format —
    one JSON object per line, as specified in the README.
    """
    candidates = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates


def write_submission_csv(ranked_results, filepath, top_n=100):
    """
    Writes the final submission CSV per submission_spec.docx Section 2.
    Only the top N candidates are included, each rank used exactly once.
    """
    import csv

    top_results = ranked_results[:top_n]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for r in top_results:
            writer.writerow([
                r['candidate_id'],
                r['rank'],
                f"{r['score']:.4f}",
                r['reasoning']
            ])

    print(f"Wrote top {len(top_results)} candidates to {filepath}")


if __name__ == '__main__':
    import time

    start = time.time()

    print("Loading full candidate pool...")
    candidates = load_candidates_jsonl('candidates.jsonl')
    load_time = time.time() - start
    print(f"Loaded {len(candidates)} candidates in {load_time:.2f}s")

    rank_start = time.time()
    ranked = rank_candidates(candidates)
    rank_time = time.time() - rank_start
    print(f"Ranked all candidates in {rank_time:.2f}s")

    total_time = time.time() - start
    print(f"Total runtime: {total_time:.2f}s\n")

    print("--- TOP 15 ---")
    for r in ranked[:15]:
        print(f"[{r['rank']}] {r['candidate_id']}: score={r['score']}")

    write_submission_csv(ranked, 'submission.csv', top_n=100)