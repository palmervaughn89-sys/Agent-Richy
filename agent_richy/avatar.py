"""Agent Richy — Animated Avatar Component.

Generates an SVG/CSS animated avatar for Richy that can be embedded
in Streamlit via st.html().  Inspired by the Virtual_Avatar_ChatBot
VTube Studio sentiment system, adapted for the web.

Expressions: neutral, happy, thinking, talking, excited, concerned
"""

# ── Expression configurations ────────────────────────────────────────────
EXPRESSIONS = {
    "neutral": {
        "left_eye": "open",
        "right_eye": "open",
        "mouth": "smile",
        "brow": "normal",
        "color_accent": "#FFD700",
        "anim": "idle",
    },
    "happy": {
        "left_eye": "happy",
        "right_eye": "happy",
        "mouth": "big_smile",
        "brow": "raised",
        "color_accent": "#FFD700",
        "anim": "bounce",
    },
    "thinking": {
        "left_eye": "open",
        "right_eye": "squint",
        "mouth": "flat",
        "brow": "raised_one",
        "color_accent": "#87CEEB",
        "anim": "tilt",
    },
    "talking": {
        "left_eye": "open",
        "right_eye": "open",
        "mouth": "open",
        "brow": "normal",
        "color_accent": "#FFD700",
        "anim": "talk",
    },
    "excited": {
        "left_eye": "wide",
        "right_eye": "wide",
        "mouth": "open_big",
        "brow": "raised",
        "color_accent": "#FF6B6B",
        "anim": "shake",
    },
    "concerned": {
        "left_eye": "open",
        "right_eye": "open",
        "mouth": "frown",
        "brow": "worried",
        "color_accent": "#FFB347",
        "anim": "none",
    },
}

# ── Sentiment detection ──────────────────────────────────────────────────
SENTIMENT_KEYWORDS = {
    "happy": ["great", "awesome", "amazing", "perfect", "congrats", "nice work",
              "crushing it", "excellent", "wonderful", "fantastic", "proud"],
    "excited": ["let's go", "exciting", "incredible", "wow", "whoa", "🚀",
                "fire", "boom", "huge", "milestone", "breakthrough"],
    "thinking": ["let me think", "consider", "analyze", "hmm", "interesting",
                 "let's look at", "calculating", "breakdown", "compare"],
    "concerned": ["careful", "warning", "risk", "watch out", "debt", "danger",
                  "struggling", "behind", "overdue", "urgent", "emergency"],
    "talking": [],  # default during streaming
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
    if scores[best] == 0:
        return "happy"  # default
    return best


def get_avatar_html(expression: str = "neutral", size: int = 150, show_name: bool = True) -> str:
    """Return full HTML/CSS/SVG for the animated Richy avatar.

    Args:
        expression: One of the EXPRESSIONS keys.
        size: Pixel size of the avatar.
        show_name: Whether to show the "Agent Richy" label.

    Returns:
        HTML string for embedding via st.html() or st.markdown(unsafe_allow_html=True).
    """
    expr = EXPRESSIONS.get(expression, EXPRESSIONS["neutral"])
    accent = expr["color_accent"]
    anim = expr["anim"]

    # Eye shapes
    left_eye = _eye_svg(expr["left_eye"], "left", size)
    right_eye = _eye_svg(expr["right_eye"], "right", size)
    mouth = _mouth_svg(expr["mouth"], size)
    brows = _brow_svg(expr["brow"], size)

    # Animation keyframes
    anim_css = _animation_css(anim)

    s = size
    cx = s // 2
    cy = s // 2

    name_html = ""
    if show_name:
        name_html = f"""
        <div style="
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 700;
            font-size: {max(12, s // 10)}px;
            color: {accent};
            margin-top: 4px;
            letter-spacing: 0.5px;
        ">Agent Richy</div>"""

    return f"""
    <div class="richy-avatar-wrap" style="display:inline-block;text-align:center;">
    <style>
        {anim_css}
        .richy-avatar-wrap svg {{
            filter: drop-shadow(0 4px 12px rgba(255, 215, 0, 0.3));
        }}
        .richy-blink {{
            animation: richy-blink-anim 4s ease-in-out infinite;
        }}
        @keyframes richy-blink-anim {{
            0%, 45%, 55%, 100% {{ transform: scaleY(1); }}
            50% {{ transform: scaleY(0.1); }}
        }}
    </style>
    <svg width="{s}" height="{s}" viewBox="0 0 {s} {s}" class="richy-avatar {anim}">
        <!-- Body glow -->
        <defs>
            <radialGradient id="rg-glow" cx="50%" cy="40%" r="50%">
                <stop offset="0%" stop-color="{accent}" stop-opacity="0.15"/>
                <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
            </radialGradient>
            <radialGradient id="rg-face" cx="50%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#3a3a5c"/>
                <stop offset="100%" stop-color="#1a1a2e"/>
            </radialGradient>
            <linearGradient id="rg-hat" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{accent}"/>
                <stop offset="100%" stop-color="#FFA500"/>
            </linearGradient>
        </defs>

        <!-- Background glow -->
        <circle cx="{cx}" cy="{cy}" r="{s//2 - 2}" fill="url(#rg-glow)"/>

        <!-- Head -->
        <circle cx="{cx}" cy="{cy + s//12}" r="{s//3}" fill="url(#rg-face)"
                stroke="{accent}" stroke-width="{max(1, s//60)}"/>

        <!-- Top hat / money hat -->
        <rect x="{cx - s//5}" y="{cy - s//3 - s//20}" width="{2*s//5}" height="{s//6}"
              rx="{s//30}" fill="url(#rg-hat)" opacity="0.95"/>
        <rect x="{cx - s//4}" y="{cy - s//3 + s//10}" width="{s//2}" height="{s//25}"
              rx="{s//50}" fill="url(#rg-hat)" opacity="0.95"/>
        <!-- $ symbol on hat -->
        <text x="{cx}" y="{cy - s//3 + s//16}" text-anchor="middle"
              font-size="{s//8}" font-weight="bold" fill="#1a1a2e"
              font-family="'Segoe UI', sans-serif">$</text>

        <!-- Brows -->
        {brows}

        <!-- Eyes -->
        <g class="richy-blink">
            {left_eye}
            {right_eye}
        </g>

        <!-- Mouth -->
        {mouth}

        <!-- Tie / bowtie -->
        <polygon points="{cx},{cy + s//3 + s//20} {cx - s//12},{cy + s//3 + s//8} {cx + s//12},{cy + s//3 + s//8}"
                 fill="{accent}" opacity="0.9"/>

    </svg>
    {name_html}
    </div>
    """


def get_avatar_chat_html(expression: str = "neutral", size: int = 80) -> str:
    """Smaller inline avatar for use next to chat messages."""
    return get_avatar_html(expression, size, show_name=False)


def get_thinking_html(size: int = 80) -> str:
    """Avatar in thinking state with loading dots."""
    avatar = get_avatar_html("thinking", size, show_name=False)
    return f"""
    <div style="display:flex;align-items:center;gap:12px;">
        {avatar}
        <div style="display:flex;gap:4px;align-items:center;">
            <div class="richy-dot" style="animation:richy-dot-anim 1.4s ease-in-out infinite;animation-delay:0s;"></div>
            <div class="richy-dot" style="animation:richy-dot-anim 1.4s ease-in-out infinite;animation-delay:0.2s;"></div>
            <div class="richy-dot" style="animation:richy-dot-anim 1.4s ease-in-out infinite;animation-delay:0.4s;"></div>
        </div>
    </div>
    <style>
        .richy-dot {{
            width: 10px; height: 10px; border-radius: 50%;
            background: #FFD700;
        }}
        @keyframes richy-dot-anim {{
            0%, 100% {{ opacity: 0.3; transform: translateY(0); }}
            50% {{ opacity: 1; transform: translateY(-6px); }}
        }}
    </style>
    """


# ── Private SVG builders ─────────────────────────────────────────────────

def _eye_svg(style: str, side: str, size: int) -> str:
    """Build SVG for one eye."""
    s = size
    cx = s // 2
    cy = s // 2
    ox = s // 7  # offset from center
    ex = cx - ox if side == "left" else cx + ox
    ey = cy + s // 15

    r = s // 14  # eye radius
    pr = s // 28  # pupil radius

    if style == "open":
        return f"""
        <circle cx="{ex}" cy="{ey}" r="{r}" fill="white"/>
        <circle cx="{ex}" cy="{ey}" r="{pr}" fill="#1a1a2e"/>
        <circle cx="{ex - pr//3}" cy="{ey - pr//3}" r="{pr//3}" fill="white" opacity="0.8"/>
        """
    elif style == "happy":
        # Upward arc (happy closed eyes)
        return f"""
        <path d="M{ex - r},{ey} Q{ex},{ey - r * 1.2} {ex + r},{ey}"
              fill="none" stroke="white" stroke-width="{max(2, s//40)}" stroke-linecap="round"/>
        """
    elif style == "squint":
        return f"""
        <ellipse cx="{ex}" cy="{ey}" rx="{r}" ry="{r//2}" fill="white"/>
        <circle cx="{ex + pr//4}" cy="{ey}" r="{pr}" fill="#1a1a2e"/>
        """
    elif style == "wide":
        r2 = int(r * 1.2)
        return f"""
        <circle cx="{ex}" cy="{ey}" r="{r2}" fill="white"/>
        <circle cx="{ex}" cy="{ey}" r="{int(pr * 1.2)}" fill="#1a1a2e"/>
        <circle cx="{ex - pr//3}" cy="{ey - pr//3}" r="{pr//3}" fill="white" opacity="0.8"/>
        """
    return ""


def _mouth_svg(style: str, size: int) -> str:
    """Build SVG for the mouth."""
    s = size
    cx = s // 2
    my = s // 2 + s // 5  # mouth Y

    if style == "smile":
        w = s // 6
        return f"""
        <path d="M{cx - w},{my} Q{cx},{my + w} {cx + w},{my}"
              fill="none" stroke="white" stroke-width="{max(2, s//50)}" stroke-linecap="round"/>
        """
    elif style == "big_smile":
        w = s // 5
        return f"""
        <path d="M{cx - w},{my} Q{cx},{my + int(w*1.3)} {cx + w},{my}"
              fill="none" stroke="white" stroke-width="{max(2, s//40)}" stroke-linecap="round"/>
        """
    elif style == "flat":
        w = s // 8
        return f"""
        <line x1="{cx - w}" y1="{my}" x2="{cx + w}" y2="{my}"
              stroke="white" stroke-width="{max(2, s//50)}" stroke-linecap="round"/>
        """
    elif style == "open":
        r = s // 12
        return f"""
        <ellipse cx="{cx}" cy="{my + r//2}" rx="{r}" ry="{int(r*0.7)}"
                 fill="#2a0a0a" stroke="white" stroke-width="{max(1, s//60)}"/>
        """
    elif style == "open_big":
        r = s // 10
        return f"""
        <ellipse cx="{cx}" cy="{my + r//2}" rx="{r}" ry="{r}"
                 fill="#2a0a0a" stroke="white" stroke-width="{max(1, s//60)}"/>
        """
    elif style == "frown":
        w = s // 6
        return f"""
        <path d="M{cx - w},{my + w//2} Q{cx},{my - w//3} {cx + w},{my + w//2}"
              fill="none" stroke="white" stroke-width="{max(2, s//50)}" stroke-linecap="round"/>
        """
    return ""


def _brow_svg(style: str, size: int) -> str:
    """Build SVG for eyebrows."""
    s = size
    cx = s // 2
    by = s // 2 - s // 10  # brow Y
    ox = s // 7
    bw = s // 10

    sw = max(2, s // 50)

    if style == "normal":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by}" x2="{cx - ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by}" x2="{cx + ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        """
    elif style == "raised":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by + 2}" x2="{cx - ox + bw}" y2="{by - 3}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by - 3}" x2="{cx + ox + bw}" y2="{by + 2}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        """
    elif style == "raised_one":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by}" x2="{cx - ox + bw}" y2="{by}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by + 3}" x2="{cx + ox + bw}" y2="{by - 5}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        """
    elif style == "worried":
        return f"""
        <line x1="{cx - ox - bw}" y1="{by - 4}" x2="{cx - ox + bw}" y2="{by + 2}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        <line x1="{cx + ox - bw}" y1="{by + 2}" x2="{cx + ox + bw}" y2="{by - 4}"
              stroke="white" stroke-width="{sw}" stroke-linecap="round" opacity="0.7"/>
        """
    return ""


def _animation_css(anim: str) -> str:
    """Return CSS keyframes for the given animation type."""
    base = """
        .idle { animation: richy-idle 3s ease-in-out infinite; }
        @keyframes richy-idle {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-3px); }
        }
    """
    extras = {
        "bounce": """
            .bounce { animation: richy-bounce 0.6s ease-in-out 3; }
            @keyframes richy-bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-8px); }
            }
        """,
        "tilt": """
            .tilt { animation: richy-tilt 2s ease-in-out infinite; }
            @keyframes richy-tilt {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(5deg); }
            }
        """,
        "talk": """
            .talk { animation: richy-talk 0.3s ease-in-out infinite; }
            @keyframes richy-talk {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-2px); }
            }
        """,
        "shake": """
            .shake { animation: richy-shake 0.5s ease-in-out 3; }
            @keyframes richy-shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-4px); }
                75% { transform: translateX(4px); }
            }
        """,
        "none": "",
    }
    return base + extras.get(anim, "")
