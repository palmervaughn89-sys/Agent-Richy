"""Agent Richy — Full-Body Animated Avatar Component.

Renders a fully visible, animated SVG character with:
- Full-body design (hat, face, suit, arms)
- 6 expressive states (neutral, happy, thinking, talking, excited, concerned)
- Speech bubble with animated text
- Persistent sidebar/header presence
- Smooth CSS transitions between expressions
- Idle floating animation + per-expression animations

NOTE: Streamlit's st.markdown(unsafe_allow_html=True) strips <svg> and <style> tags.
All avatar rendering MUST go through streamlit.components.v1.html() for proper display.
Use the render_avatar_component() helper or call components.html(html, height=...) directly.
"""

from typing import Optional

# ── Expression configurations ────────────────────────────────────────────
EXPRESSIONS = {
    "neutral": {
        "left_eye": "open", "right_eye": "open",
        "mouth": "smile", "brow": "normal",
        "color_accent": "#FFD700", "anim": "idle",
        "body_tilt": 0, "arm_pose": "down",
    },
    "happy": {
        "left_eye": "happy", "right_eye": "happy",
        "mouth": "big_smile", "brow": "raised",
        "color_accent": "#FFD700", "anim": "bounce",
        "body_tilt": 0, "arm_pose": "wave",
    },
    "thinking": {
        "left_eye": "open", "right_eye": "squint",
        "mouth": "flat", "brow": "raised_one",
        "color_accent": "#87CEEB", "anim": "tilt",
        "body_tilt": 5, "arm_pose": "chin",
    },
    "talking": {
        "left_eye": "open", "right_eye": "open",
        "mouth": "open", "brow": "normal",
        "color_accent": "#FFD700", "anim": "talk",
        "body_tilt": 0, "arm_pose": "gesture",
    },
    "excited": {
        "left_eye": "wide", "right_eye": "wide",
        "mouth": "open_big", "brow": "raised",
        "color_accent": "#FF6B6B", "anim": "shake",
        "body_tilt": -3, "arm_pose": "up",
    },
    "concerned": {
        "left_eye": "open", "right_eye": "open",
        "mouth": "frown", "brow": "worried",
        "color_accent": "#FFB347", "anim": "none",
        "body_tilt": 3, "arm_pose": "crossed",
    },
}

# ── Sentiment detection keywords ─────────────────────────────────────────
SENTIMENT_KEYWORDS = {
    "happy": ["great", "awesome", "amazing", "perfect", "congrats", "nice work",
              "crushing it", "excellent", "wonderful", "fantastic", "proud",
              "good job", "well done", "impressive", "keep it up"],
    "excited": ["let's go", "exciting", "incredible", "wow", "whoa", "🚀",
                "fire", "boom", "huge", "milestone", "breakthrough", "yes!",
                "million", "amazing news", "congratulations"],
    "thinking": ["let me think", "consider", "analyze", "hmm", "interesting",
                 "let's look at", "calculating", "breakdown", "compare",
                 "so basically", "let me see", "the numbers show"],
    "concerned": ["careful", "warning", "risk", "watch out", "debt", "danger",
                  "struggling", "behind", "overdue", "urgent", "emergency",
                  "paycheck to paycheck", "worried", "high interest"],
    "talking": [],
}


def detect_expression(text: str) -> str:
    """Detect the best expression for a given text response."""
    text_lower = text.lower()
    scores = {expr: 0 for expr in SENTIMENT_KEYWORDS}
    for expr, keywords in SENTIMENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[expr] += 1
    best = max(scores, key=scores.get)
    return "happy" if scores[best] == 0 else best


# ═══════════════════════════════════════════════════════════════════════
#  SVG COMPONENT BUILDERS
# ═══════════════════════════════════════════════════════════════════════

def _eye_svg(style: str, side: str, cx: int, cy: int) -> str:
    """Build SVG for one eye."""
    ox = 18
    ex = cx - ox if side == "left" else cx + ox
    ey = cy - 5
    r = 9
    pr = 5

    if style == "open":
        return f"""
        <circle cx="{ex}" cy="{ey}" r="{r}" fill="white"/>
        <circle cx="{ex}" cy="{ey}" r="{pr}" fill="#1a1a2e"/>
        <circle cx="{ex - 2}" cy="{ey - 2}" r="2" fill="white" opacity="0.8"/>"""
    elif style == "happy":
        return f"""
        <path d="M{ex - r},{ey} Q{ex},{ey - 12} {ex + r},{ey}"
              fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"/>"""
    elif style == "squint":
        return f"""
        <ellipse cx="{ex}" cy="{ey}" rx="{r}" ry="5" fill="white"/>
        <circle cx="{ex + 1}" cy="{ey}" r="{pr}" fill="#1a1a2e"/>"""
    elif style == "wide":
        return f"""
        <circle cx="{ex}" cy="{ey}" r="11" fill="white"/>
        <circle cx="{ex}" cy="{ey}" r="6" fill="#1a1a2e"/>
        <circle cx="{ex - 2}" cy="{ey - 2}" r="2" fill="white" opacity="0.8"/>"""
    return ""


def _mouth_svg(style: str, cx: int, cy: int) -> str:
    """Build SVG for the mouth."""
    my = cy + 18

    if style == "smile":
        return f"""
        <path d="M{cx - 14},{my} Q{cx},{my + 14} {cx + 14},{my}"
              fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"/>"""
    elif style == "big_smile":
        return f"""
        <path d="M{cx - 18},{my - 2} Q{cx},{my + 20} {cx + 18},{my - 2}"
              fill="none" stroke="white" stroke-width="3" stroke-linecap="round"/>"""
    elif style == "flat":
        return f"""
        <line x1="{cx - 10}" y1="{my}" x2="{cx + 10}" y2="{my}"
              stroke="white" stroke-width="2.5" stroke-linecap="round"/>"""
    elif style == "open":
        return f"""
        <ellipse cx="{cx}" cy="{my + 2}" rx="8" ry="5"
                 fill="#2a0a0a" stroke="white" stroke-width="1.5"/>"""
    elif style == "open_big":
        return f"""
        <ellipse cx="{cx}" cy="{my + 2}" rx="10" ry="9"
                 fill="#2a0a0a" stroke="white" stroke-width="1.5"/>"""
    elif style == "frown":
        return f"""
        <path d="M{cx - 14},{my + 6} Q{cx},{my - 5} {cx + 14},{my + 6}"
              fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"/>"""
    return ""


def _brow_svg(style: str, cx: int, cy: int) -> str:
    """Build SVG for eyebrows."""
    by = cy - 18
    ox = 18
    bw = 10
    sw = 2.5

    if style == "normal":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by}" x2="{cx - ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by}" x2="{cx + ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>"""
    elif style == "raised":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by + 3}" x2="{cx - ox + bw}" y2="{by - 4}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by - 4}" x2="{cx + ox + bw}" y2="{by + 3}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>"""
    elif style == "raised_one":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by}" x2="{cx - ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by + 3}" x2="{cx + ox + bw}" y2="{by - 6}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>"""
    elif style == "worried":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by - 5}" x2="{cx - ox + bw}" y2="{by + 3}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by + 3}" x2="{cx + ox + bw}" y2="{by - 5}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>"""
    return ""


def _arm_svg(pose: str, cx: int, body_top: int) -> str:
    """Build SVG for arms based on pose."""
    sw = 4
    ay = body_top + 20

    if pose == "down":
        return f"""
        <line x1="{cx - 30}" y1="{ay}" x2="{cx - 42}" y2="{ay + 32}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        <line x1="{cx + 30}" y1="{ay}" x2="{cx + 42}" y2="{ay + 32}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>"""
    elif pose == "wave":
        return f"""
        <line x1="{cx - 30}" y1="{ay}" x2="{cx - 42}" y2="{ay + 32}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        <g class="richy-wave">
            <line x1="{cx + 30}" y1="{ay}" x2="{cx + 50}" y2="{ay - 22}"
                  stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
            <text x="{cx + 53}" y="{ay - 24}" font-size="14">👋</text>
        </g>"""
    elif pose == "chin":
        return f"""
        <line x1="{cx - 30}" y1="{ay}" x2="{cx - 38}" y2="{ay + 30}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        <line x1="{cx + 30}" y1="{ay}" x2="{cx + 12}" y2="{ay - 22}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>"""
    elif pose == "gesture":
        return f"""
        <g class="richy-gesture">
            <line x1="{cx - 30}" y1="{ay}" x2="{cx - 50}" y2="{ay - 12}"
                  stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        </g>
        <line x1="{cx + 30}" y1="{ay}" x2="{cx + 50}" y2="{ay - 12}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>"""
    elif pose == "up":
        return f"""
        <g class="richy-arms-up">
            <line x1="{cx - 30}" y1="{ay}" x2="{cx - 48}" y2="{ay - 32}"
                  stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
            <line x1="{cx + 30}" y1="{ay}" x2="{cx + 48}" y2="{ay - 32}"
                  stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        </g>"""
    elif pose == "crossed":
        return f"""
        <line x1="{cx - 30}" y1="{ay}" x2="{cx + 12}" y2="{ay + 12}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>
        <line x1="{cx + 30}" y1="{ay}" x2="{cx - 12}" y2="{ay + 12}"
              stroke="#1a1a2e" stroke-width="{sw}" stroke-linecap="round"/>"""
    return ""


# ═══════════════════════════════════════════════════════════════════════
#  FULL AVATAR RENDER — FULL BODY
# ═══════════════════════════════════════════════════════════════════════

def get_avatar_html(expression: str = "neutral", size: int = 200, show_name: bool = True) -> str:
    """Return full HTML/SVG/CSS for the full-body animated Richy avatar.

    Args:
        expression: One of EXPRESSIONS keys
        size: Overall pixel width
        show_name: Show 'Agent Richy' label below
    """
    expr = EXPRESSIONS.get(expression, EXPRESSIONS["neutral"])
    accent = expr["color_accent"]
    anim = expr["anim"]
    arm_pose = expr["arm_pose"]
    tilt = expr.get("body_tilt", 0)

    vw, vh = 200, 280
    scale = size / vw
    actual_h = int(vh * scale)

    cx = 100
    head_cy = 70
    body_top = 120
    body_bottom = 230

    left_eye = _eye_svg(expr["left_eye"], "left", cx, head_cy)
    right_eye = _eye_svg(expr["right_eye"], "right", cx, head_cy)
    mouth = _mouth_svg(expr["mouth"], cx, head_cy)
    brows = _brow_svg(expr["brow"], cx, head_cy)
    arms = _arm_svg(arm_pose, cx, body_top)

    name_html = ""
    if show_name:
        fs = max(11, int(14 * scale))
        name_html = f"""
        <div style="text-align:center;font-family:'Segoe UI',sans-serif;font-weight:800;
                    font-size:{fs}px;color:{accent};margin-top:2px;
                    letter-spacing:0.5px;text-shadow:0 0 12px rgba(255,215,0,0.4);">
            Agent Richy
        </div>"""

    anim_css = _animation_css(anim)

    return f"""
    <div class="richy-full-wrap" style="display:inline-block;text-align:center;">
    <style>
        {anim_css}
        .richy-full-wrap svg {{
            filter: drop-shadow(0 6px 20px rgba(255, 215, 0, 0.25));
        }}
        .richy-blink {{
            animation: richy-blink-anim 4s ease-in-out infinite;
        }}
        @keyframes richy-blink-anim {{
            0%, 45%, 55%, 100% {{ transform: scaleY(1); }}
            50% {{ transform: scaleY(0.1); }}
        }}
        .richy-wave {{
            animation: richy-wave-anim 1s ease-in-out infinite;
            transform-origin: {cx + 30}px {body_top + 20}px;
        }}
        @keyframes richy-wave-anim {{
            0%, 100% {{ transform: rotate(-5deg); }}
            50% {{ transform: rotate(15deg); }}
        }}
        .richy-gesture {{
            animation: richy-gesture-anim 2s ease-in-out infinite;
            transform-origin: {cx - 30}px {body_top + 20}px;
        }}
        @keyframes richy-gesture-anim {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(-10deg); }}
        }}
        .richy-arms-up {{
            animation: richy-arms-up-anim 0.5s ease-in-out 3;
        }}
        @keyframes richy-arms-up-anim {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}
        .richy-mouth-talk {{
            animation: richy-talk-mouth 0.3s ease-in-out infinite;
        }}
        @keyframes richy-talk-mouth {{
            0%, 100% {{ transform: scaleY(1); }}
            50% {{ transform: scaleY(0.6); }}
        }}
    </style>
    <svg width="{size}" height="{actual_h}" viewBox="0 0 {vw} {vh}" class="richy-avatar {anim}"
         style="transform:rotate({tilt}deg);">
        <defs>
            <radialGradient id="rfg" cx="50%" cy="35%" r="50%">
                <stop offset="0%" stop-color="#3a3a5c"/>
                <stop offset="100%" stop-color="#1a1a2e"/>
            </radialGradient>
            <linearGradient id="rhg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{accent}"/>
                <stop offset="100%" stop-color="#FFA500"/>
            </linearGradient>
            <linearGradient id="rsg" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#2a2a4a"/>
                <stop offset="100%" stop-color="#16213e"/>
            </linearGradient>
            <radialGradient id="rgl" cx="50%" cy="30%" r="60%">
                <stop offset="0%" stop-color="{accent}" stop-opacity="0.12"/>
                <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
            </radialGradient>
        </defs>

        <!-- Ambient glow -->
        <ellipse cx="{cx}" cy="{head_cy + 40}" rx="90" ry="120" fill="url(#rgl)"/>

        <!-- Body (suit jacket) -->
        <path d="M{cx - 35},{body_top} Q{cx - 45},{body_top + 30} {cx - 40},{body_bottom}
                 L{cx + 40},{body_bottom} Q{cx + 45},{body_top + 30} {cx + 35},{body_top} Z"
              fill="url(#rsg)" stroke="{accent}" stroke-width="1.5" opacity="0.95"/>

        <!-- Shirt / tie area -->
        <rect x="{cx - 8}" y="{body_top}" width="16" height="60"
              rx="3" fill="white" opacity="0.15"/>

        <!-- Tie -->
        <polygon points="{cx},{body_top + 5} {cx - 8},{body_top + 20} {cx},{body_top + 55} {cx + 8},{body_top + 20}"
                 fill="{accent}" opacity="0.9"/>
        <circle cx="{cx}" cy="{body_top + 8}" r="4" fill="{accent}" opacity="0.7"/>

        <!-- Collar points -->
        <polygon points="{cx - 8},{body_top + 2} {cx - 22},{body_top + 18} {cx - 12},{body_top + 22}"
                 fill="#2a2a4a" stroke="{accent}" stroke-width="0.5"/>
        <polygon points="{cx + 8},{body_top + 2} {cx + 22},{body_top + 18} {cx + 12},{body_top + 22}"
                 fill="#2a2a4a" stroke="{accent}" stroke-width="0.5"/>

        <!-- Arms -->
        {arms}

        <!-- Neck -->
        <rect x="{cx - 10}" y="{body_top - 12}" width="20" height="16"
              rx="5" fill="url(#rfg)"/>

        <!-- Head -->
        <circle cx="{cx}" cy="{head_cy}" r="42" fill="url(#rfg)"
                stroke="{accent}" stroke-width="2"/>

        <!-- Top hat -->
        <rect x="{cx - 28}" y="{head_cy - 70}" width="56" height="40"
              rx="6" fill="url(#rhg)" opacity="0.95"/>
        <rect x="{cx - 35}" y="{head_cy - 32}" width="70" height="8"
              rx="4" fill="url(#rhg)" opacity="0.95"/>
        <!-- Hat band -->
        <rect x="{cx - 28}" y="{head_cy - 38}" width="56" height="8"
              rx="2" fill="#1a1a2e" opacity="0.6"/>
        <!-- $ on hat -->
        <text x="{cx}" y="{head_cy - 44}" text-anchor="middle"
              font-size="20" font-weight="bold" fill="#1a1a2e"
              font-family="'Segoe UI',sans-serif">$</text>

        <!-- Eyebrows -->
        {brows}

        <!-- Eyes with blink -->
        <g class="richy-blink">
            {left_eye}
            {right_eye}
        </g>

        <!-- Mouth -->
        <g class="{'richy-mouth-talk' if expression == 'talking' else ''}">
            {mouth}
        </g>

        <!-- Suit pocket accent -->
        <rect x="{cx + 12}" y="{body_top + 25}" width="14" height="2"
              rx="1" fill="{accent}" opacity="0.5"/>

        <!-- Suit buttons -->
        <circle cx="{cx}" cy="{body_top + 30}" r="2.5" fill="{accent}" opacity="0.4"/>
        <circle cx="{cx}" cy="{body_top + 42}" r="2.5" fill="{accent}" opacity="0.4"/>

        <!-- Shoes -->
        <ellipse cx="{cx - 18}" cy="{body_bottom + 5}" rx="14" ry="6" fill="#0a0a1e"/>
        <ellipse cx="{cx + 18}" cy="{body_bottom + 5}" rx="14" ry="6" fill="#0a0a1e"/>
    </svg>
    {name_html}
    </div>"""


def get_avatar_chat_html(expression: str = "neutral", size: int = 80) -> str:
    """Smaller inline avatar for chat messages."""
    return get_avatar_html(expression, size, show_name=False)


def get_thinking_html(size: int = 80) -> str:
    """Avatar in thinking state with animated dots."""
    avatar = get_avatar_html("thinking", size, show_name=False)
    return f"""
    <div style="display:flex;align-items:center;gap:14px;">
        {avatar}
        <div style="display:flex;gap:5px;align-items:center;">
            <div class="rd" style="animation-delay:0s;"></div>
            <div class="rd" style="animation-delay:0.2s;"></div>
            <div class="rd" style="animation-delay:0.4s;"></div>
        </div>
    </div>
    <style>
        .rd {{
            width:12px; height:12px; border-radius:50%;
            background: #FFD700;
            animation: rd-anim 1.4s ease-in-out infinite;
        }}
        @keyframes rd-anim {{
            0%,100% {{ opacity:0.3; transform:translateY(0); }}
            50% {{ opacity:1; transform:translateY(-8px); }}
        }}
    </style>"""


def get_avatar_with_speech(expression: str = "talking", size: int = 160,
                           speech: str = "", show_name: bool = True) -> str:
    """Avatar with an animated speech bubble. Great for headers and intros."""
    avatar = get_avatar_html(expression, size, show_name=show_name)
    if not speech:
        return avatar

    bubble_width = max(200, min(400, len(speech) * 7))
    return f"""
    <div style="display:flex;align-items:flex-start;gap:16px;justify-content:center;">
        {avatar}
        <div style="
            background: linear-gradient(135deg, #16213e, #1a1a2e);
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 16px 16px 16px 4px;
            padding: 14px 18px;
            max-width: {bubble_width}px;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            animation: bubble-in 0.5s ease both;
        ">
            <div style="font-weight:700;color:#FFD700;font-size:12px;margin-bottom:4px;">Agent Richy</div>
            {speech}
        </div>
    </div>
    <style>
        @keyframes bubble-in {{
            from {{ opacity:0; transform:translateX(-10px) scale(0.95); }}
            to {{ opacity:1; transform:translateX(0) scale(1); }}
        }}
    </style>"""


def get_sidebar_avatar(expression: str = "happy", name: str = "Friend") -> str:
    """Compact sidebar avatar with name and status glow."""
    avatar = get_avatar_html(expression, 120, show_name=True)
    return f"""
    <div style="text-align:center;padding:8px 0;">
        <div style="
            display:inline-block;
            border-radius:16px;
            padding:12px;
            background: linear-gradient(135deg, rgba(255,215,0,0.05), rgba(255,165,0,0.05));
            border: 1px solid rgba(255,215,0,0.15);
        ">
            {avatar}
        </div>
        <div style="margin-top:6px;font-size:13px;color:#aaa;">
            Coaching <span style="color:#FFD700;font-weight:700;">{name}</span>
        </div>
    </div>"""


def get_large_hero_avatar(expression: str = "happy") -> str:
    """Large hero avatar for the home/landing page with glow effects."""
    avatar = get_avatar_html(expression, 260, show_name=False)
    return f"""
    <div style="text-align:center;position:relative;">
        <div style="
            display:inline-block;
            position:relative;
            animation: hero-float 3s ease-in-out infinite;
        ">
            {avatar}
            <div style="
                position:absolute;
                top:50%;left:50%;
                transform:translate(-50%,-50%);
                width:280px;height:380px;
                border-radius:50%;
                background:radial-gradient(ellipse,rgba(255,215,0,0.08) 0%,transparent 70%);
                pointer-events:none;
                animation: glow-pulse 4s ease-in-out infinite;
            "></div>
        </div>
    </div>
    <style>
        @keyframes hero-float {{
            0%,100% {{ transform:translateY(0); }}
            50% {{ transform:translateY(-12px); }}
        }}
        @keyframes glow-pulse {{
            0%,100% {{ opacity:0.6; transform:translate(-50%,-50%) scale(1); }}
            50% {{ opacity:1; transform:translate(-50%,-50%) scale(1.08); }}
        }}
    </style>"""


# ═══════════════════════════════════════════════════════════════════════
#  ANIMATION CSS
# ═══════════════════════════════════════════════════════════════════════

def _animation_css(anim: str) -> str:
    """Return CSS keyframes for the given animation type."""
    base = """
        .idle { animation: richy-idle 3s ease-in-out infinite; }
        @keyframes richy-idle {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
    """
    extras = {
        "bounce": """
            .bounce { animation: richy-bounce 0.6s ease-in-out 3, richy-idle 3s ease-in-out 1.8s infinite; }
            @keyframes richy-bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-12px); }
            }
        """,
        "tilt": """
            .tilt { animation: richy-tilt 2.5s ease-in-out infinite; }
            @keyframes richy-tilt {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(5deg); }
            }
        """,
        "talk": """
            .talk { animation: richy-talk 0.4s ease-in-out infinite; }
            @keyframes richy-talk {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-3px); }
            }
        """,
        "shake": """
            .shake { animation: richy-shake 0.4s ease-in-out 3, richy-idle 3s ease-in-out 1.2s infinite; }
            @keyframes richy-shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-6px); }
                75% { transform: translateX(6px); }
            }
        """,
        "none": "",
    }
    return base + extras.get(anim, "")


# ═══════════════════════════════════════════════════════════════════════
#  HTML WRAPPER — for streamlit.components.v1.html()
# ═══════════════════════════════════════════════════════════════════════

def wrap_avatar_html(inner_html: str) -> str:
    """Wrap avatar HTML in a full document so it renders in an iframe.

    Streamlit's st.markdown strips <svg> and <style> tags even with
    unsafe_allow_html=True.  components.html() renders in an iframe and
    works perfectly.  This helper adds the boilerplate <html> wrapper.
    """
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
    html, body {{
        margin: 0; padding: 0;
        background: transparent;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100%;
    }}
</style>
</head>
<body>{inner_html}</body>
</html>"""
