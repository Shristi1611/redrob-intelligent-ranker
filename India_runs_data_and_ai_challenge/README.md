# Redrob Intelligent Ranker

Most ranking systems reward candidates for listing the right keywords. This one doesn't.

Built for Redrob's Intelligent Candidate Discovery & Ranking Challenge, this system treats career history as the primary signal and skills as supporting evidence. Candidates who pad their profile with unused buzzwords get discounted; candidates whose work genuinely matches the role rise to the top.

The system also catches a subtler problem: profiles where stated experience doesn't add up against career history (e.g. claiming 16 years while job history sums to 8), a honeypot pattern found through manual data inspection, not assumed in advance.

Runs entirely on the Python standard library. No GPU, no network calls, no external ML libraries. Ranks 100,000 candidates in under 40 seconds, well inside the 5-minute compute budget.

## Setup

No installation required beyond Python 3.10+.
