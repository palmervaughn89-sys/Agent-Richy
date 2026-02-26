# Agent Richy — Comprehensive Codebase Audit Report

## Migration Context

**Source**: Streamlit multi-page app (root-level Python files)  
**Target**: `agent-richy-v2/` — Next.js 14 frontend + FastAPI backend  
**Status**: Migration is ~85% structurally complete. Most features are rebuilt. Critical import issues block backend from running.

---

## Table of Contents

1. [CRITICAL ISSUES](#critical-issues)
2. [agent-richy-v2/backend/](#backend)
3. [agent-richy-v2/frontend/](#frontend)
4. [Root-Level Streamlit Source (Original)](#streamlit-source)
5. [Migration Gap Analysis](#migration-gap-analysis)

---

## CRITICAL ISSUES

### 🔴 Issue 1: Backend agents import old Streamlit package

Multiple backend files import `from agent_richy.profiles import UserProfile` — this references the **old** CLI package's dataclass, NOT the new Pydantic `FinancialProfile` model in `agent-richy-v2/backend/models/profile.py`.

**Affected files:**
- `backend/agents/base_agent.py` (line ~3, and in `_build_known_data`)
- `backend/agents/coach_richy.py` (line ~19 inside `get_system_prompt`)
- `backend/agents/budget_bot.py` (same pattern)
- `backend/agents/invest_intel.py` (same pattern)
- `backend/agents/debt_destroyer.py` (same pattern)
- `backend/agents/savings_sage.py` (same pattern)
- `backend/agents/kid_coach.py` (same pattern)
- `backend/routers/chat.py` (line ~15)

**Impact**: Backend will crash on startup unless `agent_richy` package is on `sys.path`. The Dockerfile.backend actually copies `../agent_richy` into the container as a workaround, but this couples the new system to the old one.

**Fix**: Replace all `from agent_richy.profiles import UserProfile` with `from models.profile import FinancialProfile` and update the code to use Pydantic model fields.

### 🟡 Issue 2: Kids router uses sys.path hack

`backend/routers/kids.py` does `sys.path.insert(0, ...)` to import `video_data.py` from the root level. Should use its own data module or the frontend's `kidsData.ts`.

### 🟡 Issue 3: Empty directories

- `backend/configs/` — empty
- `backend/scripts/` — empty

These may be planned for future use but currently add clutter.

### 🟡 Issue 4: Duplicate empty route directories in frontend

`src/app/chat/`, `src/app/dashboard/`, `src/app/kids/`, etc. exist as empty directories alongside the actual `(app)/chat/`, `(app)/dashboard/`, etc. group routes.

---

## BACKEND

### `agent-richy-v2/backend/main.py`
- **Status**: ✅ COMPLETE
- **Summary**: FastAPI app entry point. Mounts 6 routers (chat, keystroke, profile, kids, calculators, coupons). CORS for localhost:3000. Health check endpoint. Agent listing endpoint.
- **TODOs**: None
- **Issues**: None

### `agent-richy-v2/backend/requirements.txt`
- **Status**: ✅ COMPLETE
- **Summary**: 9 dependencies: fastapi, uvicorn, python-dotenv, pydantic, openai, google-generativeai, scikit-learn, httpx, sse-starlette.
- **Issues**: Missing `agent_richy` dependency (would need it for the UserProfile import)

### `agent-richy-v2/backend/core/config.py`
- **Status**: ✅ COMPLETE (130 lines)
- **Summary**: API keys from env, LLM settings (GPT-4o, temp 0.7, max 1000 tokens), COLORS dict, free tier limits (10 msgs, 1 module, 2 lessons), AGENTS dict (6 agents with name/icon/color/specialty/tagline/sample_q/avatar), onboarding options (AGE_RANGES, EXPERIENCE_LEVELS, FINANCIAL_GOALS).
- **Migration**: Mirrors root `config.py` exactly. Removed Streamlit-specific Plotly theme. Added avatar URLs.

### `agent-richy-v2/backend/core/financial_calculators.py`
- **Status**: ✅ COMPLETE (232 lines)
- **Summary**: 7 calculator functions: `compound_interest`, `debt_payoff`, `debt_snowball_vs_avalanche`, `emergency_fund_status`, `budget_50_30_20`, `savings_goal_timeline`, `net_worth_calculator`. All return detailed dicts with breakdowns. `CALCULATOR_REGISTRY` maps names to functions.
- **Migration**: Direct port from root `utils/financial_calculators.py` with identical logic. Added `net_worth_calculator` (new).

### `agent-richy-v2/backend/core/intent_detection.py`
- **Status**: ✅ COMPLETE (305 lines)
- **Summary**: Intent categories with keyword mapping → calculator + agent routing. `extract_numbers()`, `extract_percentage()`, `detect_intent()`, `try_auto_calculate()`, `build_enriched_context()`. Full pipeline: cache check → intent → calculator → RAG → enriched prompt.
- **Migration**: Port from root `utils/intent_detection.py`. Streamlit `st.session_state` replaced with function params.

### `agent-richy-v2/backend/core/knowledge_retrieval.py`
- **Status**: ✅ COMPLETE
- **Summary**: `TFIDFRetriever` class. Loads markdown from `knowledge_base/`, splits by `##` sections, uses sklearn TfidfVectorizer with cosine similarity. Falls back to keyword matching if sklearn unavailable. `retrieve_context()` helper.
- **Migration**: Direct port from root `utils/knowledge_retrieval.py`. Path adjusted for backend directory.

### `agent-richy-v2/backend/core/response_cache.py`
- **Status**: ✅ COMPLETE (143 lines)
- **Summary**: 7 pre-written Q&A entries (compound interest, investing, 50/30/20, emergency fund, debt vs invest, snowball, avalanche). Keyword similarity matching. In-memory session cache (replaces `st.session_state`).
- **Migration**: Port from root `utils/response_cache.py`. Removed all Streamlit session_state references. Uses in-memory dict instead.
- **Note**: Root version has 30+ cached responses; backend version has only 7. Content was reduced.

### `agent-richy-v2/backend/agents/__init__.py`
- **Status**: ✅ COMPLETE (48 lines)
- **Summary**: Agent registry with `get_agent()`, `_create_agent()`, `get_all_agents()`, `route_to_agent()` factory functions. Lazy singleton pattern.
- **Migration**: Identical structure to root `agents/__init__.py`.

### `agent-richy-v2/backend/agents/base_agent.py`
- **Status**: ✅ COMPLETE (287 lines)
- **Summary**: Abstract base class. Methods: `get_system_prompt()` (abstract), `_build_known_data()`, `_format_base_rules()`, `send_message()` (OpenAI streaming + Gemini), `_send_gemini()`, `_offline_response()`, `_profile_to_dict()`, `extract_financial_data()`, `strip_json_block()`, `detect_topic()`, `suggest_agent()`.
- **Migration**: Port from root `agents/base_agent.py`. Nearly identical.
- **🔴 ISSUE**: Imports `from agent_richy.profiles import UserProfile` — old package dependency.

### `agent-richy-v2/backend/agents/coach_richy.py`
- **Status**: ✅ COMPLETE
- **Summary**: Main financial coach. Dynamic system prompt (youth vs adult modes). Extensive `_offline_response()` with keyword matching. `get_opening_message()` for first interaction.
- **Migration**: Identical to root version.
- **🔴 ISSUE**: `get_system_prompt()` imports `from agent_richy.profiles import UserProfile` inline.

### `agent-richy-v2/backend/agents/budget_bot.py`
- **Status**: ✅ COMPLETE
- **Summary**: Analytical budget specialist. System prompt emphasizes math, tables, spending pattern analysis. Offline response generates 50/30/20 table.
- **🔴 ISSUE**: Same `agent_richy.profiles` import issue.

### `agent-richy-v2/backend/agents/invest_intel.py`
- **Status**: ✅ COMPLETE
- **Summary**: Investment specialist. System prompt covers asset allocation, tax-advantaged accounts, compound interest projections. Offline shows priority ladder.
- **🔴 ISSUE**: Same import issue.

### `agent-richy-v2/backend/agents/debt_destroyer.py`
- **Status**: ✅ COMPLETE
- **Summary**: Debt payoff specialist. War/battle themed personality. Covers avalanche, snowball, consolidation. Offline shows battle plan.
- **🔴 ISSUE**: Same import issue.

### `agent-richy-v2/backend/agents/savings_sage.py`
- **Status**: ✅ COMPLETE
- **Summary**: Savings specialist. Patient, milestone-based personality. Covers emergency funds, HYSA, sinking funds, savings challenges.
- **🔴 ISSUE**: Same import issue.

### `agent-richy-v2/backend/agents/kid_coach.py`
- **Status**: ✅ COMPLETE
- **Summary**: Youth financial literacy. Age-adaptive tone (under 11 / under 15 / 15+). Uses relatable analogies, games, challenges.
- **🔴 ISSUE**: Same import issue.

### `agent-richy-v2/backend/models/chat.py`
- **Status**: ✅ COMPLETE
- **Summary**: Pydantic models: `ChatRequest` (message, agent, session_id, context), `ChatMessage` (role, content, agent).
- **NEW**: No Streamlit equivalent — this is a new REST API model.

### `agent-richy-v2/backend/models/profile.py`
- **Status**: ✅ COMPLETE
- **Summary**: Pydantic models: `FinancialProfile` (full profile with debts, goals, etc.), `ProfileUpdate` (partial update). Methods: `monthly_surplus()`, `total_debt()`.
- **NEW**: Replaces `agent_richy.profiles.UserProfile` dataclass. But agents still import the old one.

### `agent-richy-v2/backend/models/structured_response.py`
- **Status**: ✅ COMPLETE
- **Summary**: Pydantic models: `ChartConfig` (Recharts-compatible), `Example`, `Milestone`, `TimeHorizon`, `Evidence`, `StructuredResponse` (message + charts + examples + time_horizon + evidence + avatar_emotion + suggested_agent + calculator_result).
- **NEW**: No Streamlit equivalent — powers the rich frontend rendering.

### `agent-richy-v2/backend/routers/chat.py`
- **Status**: ✅ COMPLETE (276 lines)
- **Summary**: Two endpoints: `POST /api/chat` (sync), `POST /api/chat/stream` (SSE). In-memory chat history and profiles. Full pipeline: enriched context → cache check → agent routing → LLM call → data extraction → response formatting.
- **NEW**: Replaces `pages/2_Chat.py` Streamlit chat interface.
- **🔴 ISSUE**: Imports `from agent_richy.profiles import UserProfile`.

### `agent-richy-v2/backend/routers/keystroke.py`
- **Status**: ✅ COMPLETE
- **Summary**: `POST /api/keystroke`. Keyword → expression mapping with priorities. Returns expression + random reaction bubble. Designed for <50ms response.
- **NEW**: Entirely new feature for real-time avatar reactions.

### `agent-richy-v2/backend/routers/profile.py`
- **Status**: ✅ COMPLETE
- **Summary**: CRUD: `GET/PUT/DELETE /api/profile/{session_id}`. In-memory dict storage.
- **NEW**: Replaces `st.session_state.profile` with REST API.

### `agent-richy-v2/backend/routers/kids.py`
- **Status**: ✅ COMPLETE
- **Summary**: `GET /api/kids/modules`, `GET /api/kids/modules/{id}`, `GET/POST /api/kids/progress/{session_id}`. Badge completion checking.
- **NEW**: Replaces `3_Kids_Education.py` page logic.
- **🟡 ISSUE**: Uses `sys.path` hack to import `video_data.py` from root. Has fallback data.

### `agent-richy-v2/backend/routers/calculators.py`
- **Status**: ✅ COMPLETE
- **Summary**: 7 POST endpoints (compound-interest, debt-payoff, debt-compare, emergency-fund, budget, savings-goal, net-worth). Each has Pydantic request model. Results include chart configs.
- **NEW**: Calculators were previously inline in Streamlit pages. Now exposed as API.

### `agent-richy-v2/backend/routers/coupons.py`
- **Status**: ✅ COMPLETE (247 lines)
- **Summary**: Coupon search via CouponAPI.org with mock fallback. Daily personalized coupons, shopping profile CRUD, savings tracking. In-memory storage.
- **NEW**: Entirely new feature not in Streamlit version.

### `agent-richy-v2/backend/services/avatar_emotion.py`
- **Status**: ✅ COMPLETE
- **Summary**: `determine_emotion()` function. Priority: content keywords > intent mapping > agent default > 'friendly'. 6 emotion rules.
- **NEW**: Entirely new for avatar system.

### `agent-richy-v2/backend/services/chart_generator.py`
- **Status**: ✅ COMPLETE
- **Summary**: `generate_charts_from_calculator()` produces Recharts-compatible `ChartConfig` objects for each calculator type. Supports area, line, bar, pie charts.
- **NEW**: Replaces Plotly chart generation from Dashboard/Plan pages.

### `agent-richy-v2/backend/services/response_formatter.py`
- **Status**: ✅ COMPLETE
- **Summary**: `format_response()` strips JSON blocks, generates charts, determines avatar emotion, extracts evidence patterns. Returns `StructuredResponse`.
- **NEW**: Centralizes response processing that was scattered across Streamlit pages.

### `agent-richy-v2/backend/prompts/system_prompt.md`
- **Status**: ✅ COMPLETE
- **Summary**: Comprehensive system prompt defining Agent Richy's personality, capabilities (10 areas), response style, agent team descriptions, coupon features, 8 rules.
- **NEW**: Consolidates prompts that were inline in agent classes.

### `agent-richy-v2/backend/knowledge_base/`
- **Status**: ✅ COMPLETE (17 markdown files)
- **Summary**: Same files as `data/knowledge_base/`. Budgeting, debt management, investing, savings/credit/taxes/insurance, kids education, calculators reference, plus topic-specific files.
- **Note**: Docker volume mounts from root `data/knowledge_base/`.

### `agent-richy-v2/backend/configs/`
- **Status**: ❌ EMPTY
- **Summary**: Empty directory. Possibly planned for environment configs, deployment configs, or agent config YAML.

### `agent-richy-v2/backend/scripts/`
- **Status**: ❌ EMPTY
- **Summary**: Empty directory. Possibly planned for migration scripts, seed scripts, or deployment scripts.

---

## FRONTEND

### `agent-richy-v2/frontend/package.json`
- **Status**: ✅ COMPLETE
- **Summary**: Next.js 14, React 18, TypeScript 5.3, Tailwind CSS 3.4, Recharts 2.12, Framer Motion 11, Zustand 4.5, Lottie React 2.4. 9 dependencies, 6 devDependencies.

### `agent-richy-v2/frontend/next.config.js`
- **Status**: ✅ COMPLETE
- **Summary**: API rewrites `* /api/:path*` → `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

### `agent-richy-v2/frontend/tailwind.config.js`
- **Status**: ✅ COMPLETE
- **Summary**: Extended colors (navy scale, brand colors, gold scale, surface), Inter font, custom animations (bounce-slow, pulse-soft, wiggle, float). Dark mode 'class'.
- **Migration**: Colors match `config.py`'s COLORS dict.

### `agent-richy-v2/frontend/tsconfig.json`
- **Status**: ✅ COMPLETE
- **Summary**: Standard Next.js config with `@/*` path alias to `./src/*`.

### `agent-richy-v2/frontend/postcss.config.js`
- **Status**: ✅ COMPLETE

### `agent-richy-v2/frontend/src/styles/globals.css`
- **Status**: ✅ COMPLETE
- **Summary**: Tailwind directives, CSS variables, dark scrollbar, chat message markdown styles, speech bubble styles.
- **Migration**: Replaces `styles.py`'s `get_global_css()`. Same design system, native CSS instead of injected HTML.

### `agent-richy-v2/frontend/src/app/layout.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Root layout with metadata, Inter font, dark navy background.

### `agent-richy-v2/frontend/src/app/page.tsx`
- **Status**: ✅ COMPLETE (104 lines)
- **Summary**: Landing page with hero section (RichyAvatar, CTA buttons), features grid (6 features), footer. Framer Motion animations.
- **Migration**: Replaces `app.py`'s welcome screen (step 0). Significantly enhanced with avatar and animations.

### `agent-richy-v2/frontend/src/app/(app)/layout.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: App shell with Sidebar + main content area + MobileNav.
- **Migration**: Replaces `app.py`'s sidebar boilerplate repeated on every page.

### `agent-richy-v2/frontend/src/app/(app)/dashboard/page.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: 4 metric cards (net worth, savings rate, DTI, emergency fund), financial health progress bars, no-profile prompt, agent team grid, quick actions, CTA section.
- **Migration**: Replaces `pages/1_Dashboard.py`. Uses Recharts instead of Plotly. Missing: Plotly chart equivalents (donut budget, income vs expenses bar, debt payoff projection, savings growth projection). These charts exist in the calculators page instead.

### `agent-richy-v2/frontend/src/app/(app)/chat/page.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Chat page with ChatPanel, right sidebar (desktop: avatar, agent switcher, agent info, suggested topics). URL param agent switching.
- **Migration**: Replaces `pages/2_Chat.py`. Enhanced with SSE streaming, avatar reactions, agent switcher sidebar. Missing: follow-up suggestion buttons (were in Streamlit version).

### `agent-richy-v2/frontend/src/app/(app)/kids/page.tsx`
- **Status**: ✅ COMPLETE (219 lines)
- **Summary**: Tabs (modules/active-lesson/badges). Module grid with lesson cards, progress bars, lock/premium indicators. Video player + quiz integration. Badge display.
- **Migration**: Replaces `pages/3_Kids_Education.py`. Content now in `kidsData.ts` with real YouTube URLs (Streamlit version had PLACEHOLDERs in `video_data.py`). Badge system preserved.
- **TODO**: `const [isPremium] = useState(false); // TODO: connect to real subscription`

### `agent-richy-v2/frontend/src/app/(app)/plan/page.tsx`
- **Status**: ✅ COMPLETE (292 lines)
- **Summary**: 3 tabs (budget/debt/goals). 50/30/20 budget visualization, surplus indicator, debt avalanche strategy display, goals with progress bars and add/remove.
- **Migration**: Replaces `pages/4_My_Plan.py`. Budget donut chart replaced with colored bars. Debt payoff chart replaced with table display. Investment projection section NOT yet migrated.

### `agent-richy-v2/frontend/src/app/(app)/profile/page.tsx`
- **Status**: ✅ COMPLETE (370 lines)
- **Summary**: Full profile form: personal info, income/expenses with surplus, savings/emergency fund, debts CRUD (add/remove with APR), credit score with color-coded progress bar, financial goals, risk tolerance.
- **Migration**: Replaces `pages/5_Financial_Profile.py`. All fields preserved. Enhanced UX with real-time surplus calculation.

### `agent-richy-v2/frontend/src/app/(app)/upgrade/page.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: 3-tier pricing (Free/$0, Pro/$9.99, Family/$14.99). Feature lists, highlighted "Most Popular" card.
- **Migration**: Replaces `pages/6_Upgrade.py`. Changed from 2-tier (Free/Premium $10) to 3-tier. Demo toggle removed.

### `agent-richy-v2/frontend/src/app/(app)/calculators/page.tsx`
- **Status**: ✅ COMPLETE (208 lines)
- **Summary**: 5 calculators (compound interest, budget, emergency fund, savings timeline, debt payoff). Dynamic form fields, API calls, chart + result display.
- **NEW**: No direct Streamlit equivalent. Calculators were embedded in chat pipeline and dashboard. Now standalone page.

### `agent-richy-v2/frontend/src/lib/types.ts`
- **Status**: ✅ COMPLETE
- **Summary**: All TypeScript interfaces: ChatRequest, ChartConfig, Example, Milestone, TimeHorizon, Evidence, StructuredResponse, ChatMessage, StreamEvent, KeystrokeResponse, AvatarExpression (12 expressions), FinancialProfile, Quiz, Lesson, KidsModule, KidsProgress, AgentInfo, AgentKey.

### `agent-richy-v2/frontend/src/lib/constants.ts`
- **Status**: ✅ COMPLETE
- **Summary**: COLORS, CHART_COLORS, free tier limits, AGENTS record (6 agents), AGENT_KEYS, onboarding options.
- **Migration**: Mirrors `config.py` exactly.

### `agent-richy-v2/frontend/src/lib/api.ts`
- **Status**: ✅ COMPLETE
- **Summary**: Full API client: `fetchJSON`, `sendChatMessage`, `streamChatMessage` (SSE), `analyzeKeystroke`, `getProfile`, `updateProfile`, `getAgents`, `getKidsModules`, `getKidsProgress`, 7 calculator functions.

### `agent-richy-v2/frontend/src/lib/kidsData.ts`
- **Status**: ✅ COMPLETE (494 lines)
- **Summary**: 4 modules (What is Money, Saving & Spending Wisely, Earning & Growing Money, Smart Money Habits), 16 total lessons with real YouTube embed URLs, quiz questions with explanations. Badge system. Helper functions.
- **Migration**: Replaces `video_data.py` + `config.py`'s KIDS_MODULES. **Key improvement**: Real YouTube URLs instead of PLACEHOLDERs. Different quiz format (uses `correct_index` + `explanation` vs old `answer` index).

### `agent-richy-v2/frontend/src/hooks/useAvatar.ts`
- **Status**: ✅ COMPLETE
- **Summary**: Zustand store: expression, bubble, isTyping, lastActivity. Actions: setExpression, setBubble, setTyping/setIsTyping, goIdle.
- **NEW**: No Streamlit equivalent.

### `agent-richy-v2/frontend/src/hooks/useChat.ts`
- **Status**: ✅ COMPLETE
- **Summary**: Zustand store: messages, activeAgent, isLoading, streamingContent. Actions: setActiveAgent, sendMessage (SSE streaming), clearMessages.
- **Migration**: Replaces `utils/session.py`'s chat history management + `2_Chat.py`'s message handling.

### `agent-richy-v2/frontend/src/hooks/useFinancialProfile.ts`
- **Status**: ✅ COMPLETE
- **Summary**: Zustand store: profile, isLoading. Actions: fetchProfile, updateField.
- **Migration**: Replaces `utils/session.py`'s `get_profile()`/`apply_extracted_data()`.

### `agent-richy-v2/frontend/src/components/avatar/RichyAvatar.tsx`
- **Status**: ✅ COMPLETE (314 lines)
- **Summary**: Main avatar component. 11 body animation variants. TypingDots indicator. 4 size configs. Multi-layered rendering: ambient glow, particles, speech bubble, SVG face with eye tracking + blinking, expression label.
- **NEW**: Entirely new. No Streamlit equivalent. Premium interactive avatar.

### `agent-richy-v2/frontend/src/components/avatar/SVGFace.tsx`
- **Status**: ✅ COMPLETE (295 lines)
- **Summary**: Pure SVG face renderer. Brows, eyes (with gaze tracking + pupil highlight + optional star eyes), mouth. Framer-motion path morphing.
- **NEW**: Entirely new vector face system.

### `agent-richy-v2/frontend/src/components/avatar/AvatarExpressionEngine.ts`
- **Status**: ✅ COMPLETE
- **Summary**: `resolveExpression()` maps context (agent, text, charts, calculator, error, greeting) to AvatarExpression. Agent defaults, text sentiment rules.
- **NEW**: AI-driven expression mapping.

### `agent-richy-v2/frontend/src/components/avatar/expressions.ts`
- **Status**: ✅ COMPLETE (181 lines)
- **Summary**: 12 expression configs (idle, watching, confused, excited, thinking, presenting, laughing, empathetic, serious, celebrating, teaching, friendly). Each with label, emoji, eyeStyle, mouthStyle, browStyle, bodyAnimation, bgGlow. Keystroke trigger keywords. Reaction bubble text pools.
- **NEW**: Data-driven expression system.

### `agent-richy-v2/frontend/src/components/avatar/faceShapes.ts`
- **Status**: ✅ COMPLETE (269 lines)
- **Summary**: SVG path definitions in 100×100 viewBox. 9 eye shapes, 9 mouth shapes, 5 brow shapes. `EXPRESSION_FACES` maps each of 12 expressions to face config. `EXPRESSION_PALETTES` maps to color scheme.
- **NEW**: Hand-crafted SVG geometry.

### `agent-richy-v2/frontend/src/components/avatar/AmbientGlow.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Multi-layered glow (radial gradient backdrop, pulsing ring, inner glow ring). Colors from expression palette.
- **NEW**: Visual polish for avatar.

### `agent-richy-v2/frontend/src/components/avatar/AvatarParticles.tsx`
- **Status**: ✅ COMPLETE (268 lines)
- **Summary**: Expression-specific particle effects (emoji symbols). Confetti burst for celebrating. Physics: curved paths with lerp, lifetime, radius. 8 particle configs.
- **NEW**: Expression-reactive particle system.

### `agent-richy-v2/frontend/src/components/avatar/SpeechBubble.tsx`
- **Status**: ✅ COMPLETE (170 lines)
- **Summary**: Typewriter text reveal, spring entrance/exit animations, decorative pointer tails (top/right/left positions), gradient accent border, auto-dismiss.
- **NEW**: Interactive speech bubble for avatar reactions.

### `agent-richy-v2/frontend/src/components/avatar/useEyeTracking.ts`
- **Status**: ✅ COMPLETE (117 lines)
- **Summary**: Tracks mouse cursor relative to avatar container. Returns smoothed (x, y) gaze offset via requestAnimationFrame lerp at 60fps.
- **NEW**: Real-time eye tracking.

### `agent-richy-v2/frontend/src/components/avatar/useBlinking.ts`
- **Status**: ✅ COMPLETE
- **Summary**: Returns `isBlinking` boolean. Randomized interval (2-6s), blink duration (150ms). Manual `triggerBlink()` and `triggerDoubleBlink()`.
- **NEW**: Natural blinking simulation.

### `agent-richy-v2/frontend/src/components/avatar/useKeystrokeWatcher.ts`
- **Status**: ✅ COMPLETE (136 lines)
- **Summary**: Watches chat input keystrokes, debounces (150ms), matches keywords → avatar expression + reaction bubble. Fire-and-forget backend `/api/keystroke` call. Idle timeout (4s). Reaction cooldown (3s).
- **NEW**: Real-time keystroke → avatar reaction pipeline.

### `agent-richy-v2/frontend/src/components/avatar/index.ts`
- **Status**: ✅ COMPLETE (barrel export)

### `agent-richy-v2/frontend/src/components/chat/ChatPanel.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Chat container with header, scrollable message area, streaming indicator (token-by-token + typing dots), auto-scroll, ChatInput.
- **Migration**: Replaces Streamlit `st.chat_message` rendering loop.

### `agent-richy-v2/frontend/src/components/chat/ChatInput.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Auto-resizing textarea, keystroke watcher integration, Enter to send.
- **Migration**: Replaces `st.chat_input()`.

### `agent-richy-v2/frontend/src/components/chat/ChatMessage.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: User/assistant message bubbles with agent badge, content, ResponseRenderer, timestamp.

### `agent-richy-v2/frontend/src/components/chat/ResponseRenderer.tsx`
- **Status**: ✅ COMPLETE (155 lines)
- **Summary**: Renders charts (FinancialChart), calculator results, time horizons with progress bars and milestones, evidence cards, examples.
- **NEW**: Rich structured response rendering. No Streamlit equivalent.

### `agent-richy-v2/frontend/src/components/charts/FinancialChart.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Recharts wrapper supporting line, bar, pie (donut), and area charts. Auto-detects y-keys, custom tooltip styling.
- **Migration**: Replaces Plotly charts from `1_Dashboard.py` and `4_My_Plan.py`.

### `agent-richy-v2/frontend/src/components/evidence/EvidenceCard.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Expandable card showing source, confidence badge (color-coded), fact/snippet.
- **NEW**: RAG evidence display. No Streamlit equivalent.

### `agent-richy-v2/frontend/src/components/kids/VideoLesson.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: YouTube iframe embed with play button overlay.
- **Migration**: Replaces `components/video_player.py`'s `render_video_player()`.

### `agent-richy-v2/frontend/src/components/kids/QuizCard.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Multiple choice quiz with correct/incorrect highlighting, explanation reveal.
- **Migration**: Replaces `components/quiz.py`'s `render_quiz()`.

### `agent-richy-v2/frontend/src/components/kids/BadgeDisplay.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Badge grid showing earned/locked badges with hover animation.
- **Migration**: Replaces inline badge HTML from `3_Kids_Education.py`.

### `agent-richy-v2/frontend/src/components/layout/Sidebar.tsx`
- **Status**: ✅ COMPLETE
- **Summary**: Desktop sidebar with brand header (avatar + name), 6 nav items with active indicator, upgrade CTA.
- **Migration**: Replaces repeated `st.sidebar` code across all Streamlit pages.

### `agent-richy-v2/frontend/src/components/layout/TopNav.tsx`
- **Status**: ✅ COMPLETE

### `agent-richy-v2/frontend/src/components/layout/MobileNav.tsx`
- **Status**: ✅ COMPLETE
- **NEW**: Mobile-responsive navigation. No Streamlit equivalent.

### All barrel `index.ts` files
- **Status**: ✅ COMPLETE (layout, chat, charts, evidence, kids, avatar)

---

## STREAMLIT SOURCE

### `app.py` (411 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Entry point. 4-step onboarding (Welcome → Personal Info → Goals → Financial Snapshot → Meet Coaches). Post-onboarding sidebar + welcome dashboard with metrics and navigation.
- **Migrated to**: `src/app/page.tsx` (landing), `src/app/(app)/dashboard/page.tsx`, `src/app/(app)/profile/page.tsx` (onboarding data captured there). **Note**: Multi-step onboarding flow NOT explicitly migrated — v2 uses the profile page for data entry and landing page for first impression.

### `config.py` (413 lines)
- **Status**: ✅ COMPLETE
- **Summary**: API keys, LLM settings, COLORS, Plotly theme, free tier limits, AGENTS dict, KIDS_MODULES (4 modules with lessons/quizzes/video URLs), onboarding options.
- **Migrated to**: `backend/core/config.py` + `frontend/src/lib/constants.ts`. KIDS_MODULES now in `frontend/src/lib/kidsData.ts`. Plotly theme dropped (using Recharts).

### `video_data.py` (319 lines)
- **Status**: ✅ COMPLETE
- **Summary**: 4 video modules with 3 lessons each (12 total). PLACEHOLDER video URLs. Badges. Helper functions.
- **Migrated to**: `frontend/src/lib/kidsData.ts` (4 modules, 16 lessons, real YouTube URLs). Backend `routers/kids.py` imports this with fallback.
- **Key difference**: v2 has 16 lessons (4 per module) vs v1's 12 (3 per module). v2 has real YouTube URLs.

### `styles.py` (528 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Complete CSS injection for Streamlit. Hides defaults, custom typography, buttons, cards, metrics, tabs, chat, forms, hero classes, agent cards, responsive styles.
- **Migrated to**: `frontend/src/styles/globals.css` + `frontend/tailwind.config.js`. Design system preserved.

### `pages/1_Dashboard.py` (332 lines)
- **Status**: ✅ COMPLETE
- **Summary**: 4 metric cards, 4 Plotly charts (budget donut, income vs expenses bar, debt payoff projection, savings growth projection), quick actions, financial health indicators.
- **Migrated to**: `src/app/(app)/dashboard/page.tsx`. **Gap**: Dashboard page doesn't include charts — those are in the calculators page. Metric cards migrated. Quick actions migrated.

### `pages/2_Chat.py` (412 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Full chat interface. Agent switcher sidebar. Smart pipeline: cache → intent → calculator → RAG → LLM. OpenAI + Gemini streaming. JSON data extraction. Follow-up suggestions. Message limit enforcement.
- **Migrated to**: `src/app/(app)/chat/page.tsx` + `useChat.ts` + `ChatPanel` + backend `routers/chat.py`. **Gap**: Follow-up suggestion buttons not yet in v2. Plan generation detection not in v2.

### `pages/3_Kids_Education.py` (470 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Full kids education portal. Module grid, lesson cards, video player, quiz system, badge tracking, progress bars, free/premium tier gating.
- **Migrated to**: `src/app/(app)/kids/page.tsx` + `VideoLesson`, `QuizCard`, `BadgeDisplay` components + `kidsData.ts`. Fully migrated.

### `pages/4_My_Plan.py` (386 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Budget visualization, debt payoff strategy, investment recommendations, goals display, AI recommendations.
- **Migrated to**: `src/app/(app)/plan/page.tsx`. **Gaps**: Investment recommendations section not migrated. AI recommendations section not migrated. Charts are simpler.

### `pages/5_Financial_Profile.py` (370+ lines)
- **Status**: ✅ COMPLETE
- **Summary**: Full profile editor: personal info, income/expenses, savings, debts CRUD, goals, credit score, risk tolerance.
- **Migrated to**: `src/app/(app)/profile/page.tsx`. Fully migrated. Enhanced with employment status field.

### `pages/6_Upgrade.py` (200+ lines)
- **Status**: ✅ COMPLETE
- **Summary**: 2-tier comparison (Free/$0 vs Premium/$10/mo). Feature lists, demo toggle.
- **Migrated to**: `src/app/(app)/upgrade/page.tsx`. Changed to 3-tier (Free/Pro/Family). Demo toggle removed.

### `agents/__init__.py`
- **Status**: ✅ COMPLETE → Migrated to `backend/agents/__init__.py`

### `agents/base_agent.py` (300 lines)
- **Status**: ✅ COMPLETE → Migrated to `backend/agents/base_agent.py` (nearly identical)

### `agents/coach_richy.py`
- **Status**: ✅ COMPLETE → Migrated to `backend/agents/coach_richy.py` (identical)

### `agents/budget_bot.py`, `invest_intel.py`, `debt_destroyer.py`, `savings_sage.py`, `kid_coach.py`
- **Status**: ✅ COMPLETE → All migrated identically to `backend/agents/`

### `utils/session.py` (213 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Streamlit session state management. `init_session_state()`, `get_profile()`, `get_chat_history()`, `add_message()`, `is_message_limit_reached()`, `apply_extracted_data()`.
- **Migrated to**: `useChat.ts`, `useFinancialProfile.ts` (frontend stores) + `backend/routers/chat.py` (in-memory dicts). Session initialization replaced by Zustand stores.

### `utils/calculations.py` (241 lines)
- **Status**: ✅ COMPLETE
- **Summary**: `compound_growth()`, `debt_payoff_schedule()`, `months_to_goal()`, `estimate_federal_tax()`, `mortgage_payment()`, `savings_rate_pct()`, `debt_to_income()`, `emergency_fund_months()`.
- **Migrated to**: `backend/core/financial_calculators.py` (includes all functions with slightly different signatures).

### `utils/financial_calculators.py` (292 lines)
- **Status**: ✅ COMPLETE
- **Summary**: 7 precise calculators with detailed breakdowns. Used by intent detection pipeline.
- **Migrated to**: `backend/core/financial_calculators.py`. Identical logic.

### `utils/intent_detection.py` (360 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Intent categories, keyword mapping, number extraction, calculator routing, RAG integration, enriched context building.
- **Migrated to**: `backend/core/intent_detection.py`. Streamlit session state removed.

### `utils/response_cache.py` (595 lines)
- **Status**: ✅ COMPLETE
- **Summary**: 30+ pre-written Q&A pairs. Keyword matching. Session caching.
- **Migrated to**: `backend/core/response_cache.py`. **Reduced from 30+ to 7 entries**. Missing: tax bracket, credit building, 401k, Roth IRA, retirement, side hustle, insurance responses.

### `utils/knowledge_retrieval.py` (160 lines)
- **Status**: ✅ COMPLETE → Migrated to `backend/core/knowledge_retrieval.py`

### `utils/formatters.py`
- **Status**: ✅ COMPLETE
- **Summary**: `format_currency()`, `format_pct()`, `format_months()`, `format_compact()`, `ordinal()`.
- **Migrated to**: NOT explicitly migrated. Formatting is done inline in frontend components using `Intl.NumberFormat` and template literals.

### `utils/video_loader.py` (184 lines)
- **Status**: ✅ COMPLETE
- **Summary**: Multi-source video resolution: local MP4 → video_urls.json → YouTube embed → placeholder.
- **Migrated to**: Frontend `VideoLesson.tsx` handles YouTube embeds directly. Local MP4 pipeline dropped in v2. Simplified.

### `components/__init__.py`
- **Status**: ✅ COMPLETE (barrel exports)

### `components/metric_card.py`
- **Status**: ✅ COMPLETE → Dashboard page renders metrics inline using Tailwind

### `components/agent_card.py`
- **Status**: ✅ COMPLETE → Agent cards rendered inline in dashboard/chat pages

### `components/progress_tracker.py` (154 lines)
- **Status**: ✅ COMPLETE → Progress bars rendered inline using Tailwind

### `components/quiz.py` (164 lines)
- **Status**: ✅ COMPLETE → Migrated to `QuizCard.tsx`

### `components/video_player.py`
- **Status**: ✅ COMPLETE → Migrated to `VideoLesson.tsx`

---

## Docker & Deployment

### `agent-richy-v2/docker-compose.yml`
- **Status**: ✅ COMPLETE
- **Summary**: Two services (backend:8000, frontend:3000). Backend healthcheck. Frontend depends on backend. Volume mounts for knowledge_base and investments.json. Optional nginx proxy commented out.

### `agent-richy-v2/Dockerfile.backend`
- **Status**: ✅ COMPLETE
- **Summary**: Python 3.11-slim. Copies knowledge_base, investments.json, `agent_richy` package (workaround), backend code, root agents. Runs uvicorn.
- **🔴 ISSUE**: `COPY ../agent_richy /app/agent_richy` — this is a workaround for the import issue. Build context issue: `..` paths don't work in Docker COPY.

### `agent-richy-v2/Dockerfile.frontend`
- **Status**: ✅ COMPLETE
- **Summary**: Multi-stage build. Node 20 Alpine. Builds Next.js, copies standalone output.

---

## MIGRATION GAP ANALYSIS

### Features Successfully Migrated ✅
| Streamlit Feature | v2 Equivalent |
|---|---|
| Multi-agent chat with streaming | `ChatPanel` + SSE streaming + `useChat` store |
| Agent switching | Sidebar agent switcher in chat page |
| Profile management | Profile page + `useFinancialProfile` store + REST API |
| Kids education (modules/lessons/quizzes/badges) | Kids page + `kidsData.ts` + dedicated components |
| Dashboard metrics | Dashboard page with metric cards |
| Financial plan (budget/debt/goals) | Plan page with 3 tabs |
| Upgrade/pricing | Upgrade page (enhanced to 3-tier) |
| Financial calculators | Standalone calculators page (new) + API endpoints |
| Knowledge base RAG | Backend TF-IDF retriever |
| Intent detection pipeline | Backend `build_enriched_context()` |
| Response caching | Backend in-memory cache |
| Offline fallback | Agent `_offline_response()` methods |
| Free tier limits | Frontend + backend enforcement |

### New Features in v2 (Not in Streamlit) 🆕
| Feature | Files |
|---|---|
| Interactive SVG avatar with 12 expressions | `RichyAvatar`, `SVGFace`, `faceShapes`, `expressions` |
| Mouse-tracking eyes | `useEyeTracking.ts` |
| Natural blinking | `useBlinking.ts` |
| Keystroke → avatar reaction pipeline | `useKeystrokeWatcher` + `/api/keystroke` |
| Expression-specific particles | `AvatarParticles.tsx` |
| Ambient glow effects | `AmbientGlow.tsx` |
| Speech bubble with typewriter effect | `SpeechBubble.tsx` |
| Structured responses (charts, evidence, examples) | `ResponseRenderer` + `StructuredResponse` model |
| Evidence cards from RAG | `EvidenceCard.tsx` |
| Coupon search & savings tracking | `routers/coupons.py` |
| Mobile-responsive navigation | `MobileNav.tsx` |
| Dedicated calculators page | `calculators/page.tsx` |

### Missing / Incomplete in v2 ❌
| Gap | Severity | Description |
|---|---|---|
| `UserProfile` → `FinancialProfile` migration | 🔴 Critical | All backend agents import old dataclass. Blocks standalone backend. |
| Dashboard charts | 🟡 Medium | Streamlit had 4 Plotly charts. v2 dashboard has metrics only (charts in calculators). |
| Investment recommendations on Plan page | 🟡 Medium | Streamlit version showed portfolio allocation table + growth projection. |
| AI recommendations section on Plan page | 🟡 Medium | Streamlit version displayed `plan.recommendations` list. |
| Follow-up suggestion buttons in chat | 🟢 Low | Streamlit version showed context-aware follow-up buttons after each response. |
| Plan generation detection | 🟢 Low | Streamlit marked `plan_generated` and showed badges in chat sidebar. |
| Response cache completeness | 🟢 Low | Reduced from 30+ to 7 pre-written answers. |
| Multi-step onboarding flow | 🟢 Low | v2 uses profile page instead of guided 4-step wizard. |
| Plotly → Recharts chart parity | 🟢 Low | Some chart types simplified. Core calculations preserved via API. |
| `formatters.py` utilities | 🟢 Low | Not explicitly ported but replaced with inline JS formatting. |
| Dockerfile.backend `COPY ..` paths | 🟡 Medium | Won't work as-is. Need different build context or copy strategy. |
| Video loader multi-source pipeline | 🟢 Low | Simplified to YouTube-only. Local MP4 support dropped. |
| Tax estimator display | 🟢 Low | Calculator exists in backend but no frontend page for it. |

### Recommended Priority Actions
1. **Fix the `UserProfile` import issue** — Replace all `agent_richy.profiles` imports with `models.profile.FinancialProfile` in backend agents and routers
2. **Fix Dockerfile.backend** — Use proper build context or multi-stage approach
3. **Add dashboard charts** — Wire calculators API to dashboard for budget donut + income/expenses bar
4. **Add investment section to Plan page** — Port the portfolio allocation table and growth projection
5. **Verify end-to-end flow** — Run backend + frontend together and test chat streaming, profile CRUD, kids progress
