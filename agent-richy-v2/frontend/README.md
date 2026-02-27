# Agent Richy — AI Financial Coach (Frontend)

> Your all-in-one AI financial coach. Budgets, coupons, bill negotiation, investing, debt payoff, and more — powered by Claude.

## Tech Stack

| Layer       | Technology                                      |
|-------------|--------------------------------------------------|
| Framework   | Next.js 14 (App Router, `standalone` output)    |
| Language    | TypeScript (strict mode)                         |
| Styling     | Tailwind CSS (dark-theme design system)         |
| State       | Zustand (chat, avatar, profile stores)          |
| Charts      | Recharts                                         |
| Animation   | Framer Motion                                    |
| AI          | Anthropic Claude API (streaming SSE)            |
| Deployment  | Vercel                                           |

## Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Set environment variables
cp .env.example .env.local
# Required: ANTHROPIC_API_KEY
# Optional: ANTHROPIC_MODEL (default: claude-sonnet-4-20250514)

# 3. Run dev server
npm run dev       # http://localhost:3000

# 4. Build for production
npm run build
npm start
```

## Environment Variables

| Variable            | Required | Description                                |
|---------------------|----------|--------------------------------------------|
| `ANTHROPIC_API_KEY` | Yes      | Anthropic API key for Claude               |
| `ANTHROPIC_MODEL`   | No       | Model override (default: claude-sonnet-4-20250514)  |

## Scripts

| Script          | Description                          |
|-----------------|--------------------------------------|
| `npm run dev`   | Start development server             |
| `npm run build` | Production build                     |
| `npm start`     | Serve production build               |
| `npm run lint`  | Run ESLint                           |

## Architecture

```
src/
├── app/                    # Next.js App Router pages
│   ├── (app)/              # Authenticated app shell (sidebar layout)
│   │   ├── chat/           # Main chat interface
│   │   ├── dashboard/      # Financial overview dashboard
│   │   ├── calculators/    # Interactive financial calculators
│   │   ├── kids/           # Kids financial education
│   │   ├── plan/           # Financial plan builder
│   │   ├── profile/        # User financial profile
│   │   ├── lifestyle-portfolio/ # Lifestyle portfolio
│   │   └── upgrade/        # Upgrade/premium page
│   ├── api/                # API routes
│   │   ├── chat/           # Chat + streaming endpoints
│   │   ├── calculators/    # 7 calculator endpoints
│   │   └── keystroke/      # Real-time keystroke analysis
│   ├── error.tsx           # Global error boundary
│   ├── not-found.tsx       # 404 page
│   ├── loading.tsx         # Global loading state
│   ├── sitemap.ts          # Dynamic sitemap generation
│   └── page.tsx            # Landing page (821 lines)
├── components/
│   ├── chat/               # 42 chat card components
│   ├── charts/             # Recharts wrappers
│   ├── avatar/             # Animated avatar system
│   ├── layout/             # Sidebar, TopNav, MobileNav
│   └── evidence/           # Evidence/source cards
├── hooks/                  # Zustand stores (useChat, useAvatar)
├── lib/                    # Core logic
│   ├── chatEngine.ts       # Agent routing, offline fallback, emotion detection
│   ├── skillDetection.ts   # 21-skill keyword matching
│   ├── calculators.ts      # Financial calculator functions
│   ├── economicFeeds.ts    # 36 economic data feeds
│   ├── decisionScience.ts  # 9-framework decision engine
│   ├── rateLimit.ts        # In-memory rate limiting
│   └── types.ts            # TypeScript interfaces
├── prompts/                # LLM system prompts (28 capabilities)
│   ├── richy-unified.md    # Master unified prompt
│   ├── decision-science.md # Decision science framework
│   └── *.md                # 21 skill-specific prompts
└── styles/
    └── globals.css         # Design system tokens + utilities
```

## Key Features (28 Capabilities)

1. Smart Coupons & Deals
2. Spending Optimizer
3. Investment Intelligence
4. Budget & Cash Flow
5. Tax Strategy
6. Price Intelligence
7. Goal Simulator
8. Bill Predictor
9. Local Deal Radar
10. Receipt Analyzer
11. Grocery Planner
12. Allocation Mapper
13. Financial DNA
14. Proactive Alerts
15. Wealth Trajectory
16. Financial Twin
17. Wealth Race
18. Advisor Marketplace
19. Money Map
20. Ripple Tracker
21. Economic Intelligence
22. Purchase Timing
23. Financial Literacy
24. Decision Science
25. Analyst Consensus
26. Wealth Education
27. Smart Cost Cutting
28. Decision Simulator

## Deployment

Deployed on **Vercel** at [agent-richy-pwgx.vercel.app](https://agent-richy-pwgx.vercel.app).

Build output mode: `standalone` (optimized for serverless).

## Security

- Rate limiting on all API routes (10/min chat, 30/min calculators)
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- No debug logs in production
- Input validation on all endpoints
- Error boundaries at global level

## License

Proprietary — All rights reserved.
