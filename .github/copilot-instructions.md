# Copilot Instructions for Agent-Richy

## Project Overview
- `agent_richy` is a comprehensive Python CLI financial coaching platform for **all ages** — kids, middle/high schoolers, and adults.
- Two interactive modules:
  - **Youth** (`agent_richy/modules/youth.py`) — 12-feature menu: talent discovery, earning ideas, side-hustle builder, budgeting workshop, savings challenges, investing intro, bad habits quiz, real-world scenarios, AI video lessons, ask Richy, financial snapshot.
  - **Adult** (`agent_richy/modules/adult.py`) — 16-feature menu: full financial assessment, budget simulation, paycheck-to-paycheck escape plan, bad habits check, subscription audit, debt destroyer (snowball/avalanche), tax estimator, mortgage calculator, vacation planner (multi-year), goal planner, investment portfolio builder, insurance guide, AI video lessons, ask Richy, financial snapshot.
- **Entry point:** `main.py` — CLI onboarding (name, age) that routes to `YouthModule` (age < 18) or `AdultModule`.
- Session state: `agent_richy/profiles.py` (`UserProfile` dataclass) — expanded with debts, subscriptions, talents, side hustles, vacation planning, credit score, bad habits, and computed properties.
- Shared utilities: `agent_richy/utils/helpers.py` — CLI formatting, input parsing, LLM integration, investment data loading/filtering.
- AI video generation: `agent_richy/utils/video_generator.py` — CogVideoX-powered educational video creator with 12+ pre-crafted prompts keyed by audience (kids/middle/high).

## Architecture & Data Flow (important)
- Module classes (`YouthModule`, `AdultModule`) are stateful, receiving `UserProfile` + optional `llm_client` in `__init__`.
- User input flow: `prompt(...)` → `parse_number` / `parse_yes_no` / `choose_one` / `choose_many` → update `UserProfile` → print formatted output.
- LLM flow: `ask_llm(...)` in `helpers.py` → OpenAI chat completions → fallback to deterministic advice if no API key.
- Video flow: `video_generator.py` lazy-loads `THUDM/CogVideoX-2b` pipeline → generates `.mp4` or falls back to text-based storyboard lessons.
- Investment data: `load_investments()` / `filter_investments(risk, themes, esg_min, asset_type)` reads `data/investments.json`.
- Keep interactive UX inside module methods (`run`, `_tax_helper`, `_budget_simulation`, etc.), not in utilities.

## Existing Conventions to Follow
- Motivational, practical tone with emoji section headers.
- Reuse helpers — never use bare `input()` or `print()` for formatting:
  - `prompt`, `print_header`, `print_divider`, `print_tip`, `print_warning`, `print_success`, `wrap_text`, `format_currency`, `progress_bar`
  - `parse_number` handles `$1,200`, `20%`, etc.
  - `choose_one` / `choose_many` for menu selections.
- Early-return validation pattern when input parsing fails.
- Store durable state on `UserProfile` fields, not local variables.
- Private method naming: `_feature_name` for each menu section.

## LLM Integration Notes
- OpenAI client via `get_openai_client()` (requires `OPENAI_API_KEY` env var or `.env` file).
- `ask_llm` uses `gpt-4o`, `temperature=0.7`, `max_tokens=800`.
- **Always** keep a non-LLM fallback path so features work offline.

## Video Generation Notes
- `video_generator.py` provides `is_video_generation_available()`, `list_videos_for_audience(audience)`, `generate_video(prompt_key)`, `show_lesson_without_video(prompt_key)`.
- Requires `diffusers`, `torch`, `accelerate` (optional — gracefully degrades).
- 12+ educational prompts covering savings, compound interest, budgeting, side hustles, investing, impulse control, debt.

## Data & External Inputs
- `data/investments.json` — stocks, ETFs, funds, commodities, crypto with `risk`, `themes`, `esg_score`, `growth_rate`, `description`.
- Both `youth.py` (investing intro) and `adult.py` (portfolio builder) read this data via `load_investments()` / `filter_investments()`.

## Developer Workflow
- Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run: `python main.py`
- Dependencies: `openai`, `python-dotenv`, `requests`, `pytest`, `diffusers` (optional), `torch` (optional), `accelerate` (optional).
- No test suite yet; manual testing via CLI.

## Scope Guidance for Changes
- Edit the relevant module (`youth.py` vs `adult.py`) and keep helpers generic.
- Preserve menu-driven CLI structure and `_feature_name` naming.
- New features should update `UserProfile` fields and provide both LLM-enhanced and offline paths.
- Avoid web frameworks unless explicitly requested — this is a lightweight CLI package.