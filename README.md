# Redrob Intelligent Ranker

A candidate ranking system built for Redrob's Intelligent Candidate Discovery and Ranking Challenge.

Most ranking approaches reward candidates for listing the right keywords. This system treats career history as the primary signal and skills as supporting evidence, a skill listed in a profile only counts if the candidate's actual career history shows it was used. Candidates who pad their profile with unused buzzwords get discounted; candidates whose work genuinely matches the role rise to the top.

Live sandbox: [redrob-intelligent-ranker.streamlit.app](https://redrob-intelligent-ranker.streamlit.app/)

## How it works

Each candidate is scored across five weighted dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| Career history | 40% | Job title and career description match against the role, with penalties for consulting-only current employers |
| Skills | 25% | Relevant skill coverage, weighted by proficiency and duration, discounted heavily if career history shows no supporting evidence |
| Behavioral signals | 20% | Availability and platform engagement: response rate, notice period, recent activity, interview completion |
| Experience range | 10% | Years of experience against the role's target band |
| Profile quality | 5% | Completeness, verification status, GitHub activity |

Career relevance also acts as a gate on the final score: a candidate with near-zero career fit is not competitive even with strong behavioral signals, since availability alone does not indicate role fit.

### Honeypot detection

The dataset contains synthetic trap profiles, candidates with logically impossible attribute combinations. Two checks catch these:

- A skill marked "expert" with zero months of recorded use
- Stated years of experience that diverges significantly, in either direction, from the sum of the candidate's own career history durations (found through manual inspection of suspicious top-ranked candidates during development, where a profile stated 16.2 years while its career history summed to roughly 8.2 years, with the profile's own summary text matching the lower, correct figure)

### Reasoning

Each ranked candidate gets a short, fact-grounded reasoning string built from their actual profile data, current title and company, relevant skills found in their record, engagement signals, and availability. No templated language and no claims not supported by the underlying data.

## Repository structure

```
ranker.py                  Core scoring and ranking logic, no external dependencies
app.py                     Streamlit sandbox entry point and page navigation
shared_ui.py                Shared styling used across sandbox pages
hero_component.html         Animated hero section for the sandbox home page
results_component.html      Animated results display for the sandbox
pages/
  home_page.py               Sandbox home page
  upload_page.py             Candidate data loading page
  results_page.py            Ranking execution and results page
sample_candidates.json      50-candidate reference sample
candidate_schema.json       Schema reference for the candidate data format
requirements.txt            Sandbox dependencies (streamlit, pandas); ranker.py itself has none
```

## Setup

The core ranker requires no installation beyond Python 3.10 or later, it uses only the standard library.

To run the sandbox locally:

```
pip install -r requirements.txt
streamlit run app.py
```

## Usage

Place `candidates.jsonl` in the project root, then run:

```
python ranker.py
```

This loads the full candidate pool, scores and ranks all candidates, and writes the top 100 to `submission.csv` in the format specified by the challenge. The script also runs a verification suite covering row count, rank uniqueness, score monotonicity, honeypot rate, and reasoning quality before completing.

Typical runtime is under 40 seconds for 100,000 candidates, well inside the 5-minute, CPU-only, no-network compute budget.

## Design notes

Career history was weighted highest after manually reviewing the 50-candidate sample set and finding that skills lists were an unreliable signal on their own, several candidates listed highly relevant skills such as fine-tuning LLMs or NLP while their career history showed entirely unrelated work, typically at consulting firms. Job title and career description content proved to be a far stronger indicator of genuine fit than self-reported skill tags.

The skills-discount mechanism and the career-score gate on the final ranking were both added after this finding, to prevent keyword-stuffed profiles from outranking candidates with weaker skill lists but directly relevant career experience.