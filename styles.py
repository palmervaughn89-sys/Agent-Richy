"""Centralized CSS styles for Agent Richy — Premium dark fintech theme."""

from config import COLORS


def get_global_css() -> str:
    """Return the complete global CSS for the application."""
    return f"""
<style>
    /* ── Import Fonts ──────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Root Variables ────────────────────────────────────────── */
    :root {{
        --navy: {COLORS['navy']};
        --navy-light: {COLORS['navy_light']};
        --navy-card: {COLORS['navy_card']};
        --blue: {COLORS['blue']};
        --blue-light: {COLORS['blue_light']};
        --gold: {COLORS['gold']};
        --gold-light: {COLORS['gold_light']};
        --white: {COLORS['white']};
        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
        --text-muted: {COLORS['text_muted']};
        --green: {COLORS['green']};
        --red: {COLORS['red']};
        --border: {COLORS['border']};
        --surface: {COLORS['surface']};
    }}

    /* ── Global Reset ──────────────────────────────────────────── */
    .stApp {{
        background: linear-gradient(180deg, {COLORS['navy']} 0%, {COLORS['surface']} 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {COLORS['text_primary']};
    }}

    /* ── Hide Streamlit defaults ───────────────────────────────── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    div[data-testid="stDecoration"] {{display: none;}}
    .viewerBadge_container__r5tak {{display: none !important;}}
    .viewerBadge_link__qRIco {{display: none !important;}}

    /* ── Sidebar ───────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['navy']} 0%, {COLORS['navy_light']} 100%);
        border-right: 1px solid {COLORS['border']};
    }}
    section[data-testid="stSidebar"] .stMarkdown p {{
        color: {COLORS['text_secondary']};
    }}

    /* ── Typography ────────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif !important;
        color: {COLORS['text_primary']} !important;
        font-weight: 700 !important;
    }}
    h1 {{ font-size: 2.2rem !important; }}
    h2 {{ font-size: 1.6rem !important; }}
    h3 {{ font-size: 1.3rem !important; }}

    p, li, span {{
        font-family: 'Inter', sans-serif;
    }}

    /* ── Buttons ────────────────────────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['blue']} 0%, {COLORS['blue_hover']} 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.5);
        background: linear-gradient(135deg, {COLORS['blue_light']} 0%, {COLORS['blue']} 100%);
    }}
    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Gold variant (for premium CTAs) */
    .gold-btn > button {{
        background: linear-gradient(135deg, {COLORS['gold']} 0%, {COLORS['gold_dim']} 100%) !important;
        color: {COLORS['navy']} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3) !important;
    }}
    .gold-btn > button:hover {{
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.5) !important;
    }}

    /* ── Cards ──────────────────────────────────────────────────── */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1rem;
    }}

    /* ── Expander ──────────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background: {COLORS['navy_card']} !important;
        border-radius: 10px !important;
        border: 1px solid {COLORS['border']} !important;
        color: {COLORS['text_primary']} !important;
        font-weight: 600 !important;
    }}
    .streamlit-expanderContent {{
        background: {COLORS['navy_light']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }}

    /* ── Metrics ────────────────────────────────────────────────── */
    div[data-testid="stMetric"] {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1rem;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {COLORS['text_secondary']} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS['text_primary']} !important;
        font-weight: 700 !important;
    }}

    /* ── Inputs ─────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: {COLORS['navy_light']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 10px !important;
        color: {COLORS['text_primary']} !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {COLORS['blue']} !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3) !important;
    }}

    /* ── Tabs ───────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 8px 16px;
        color: {COLORS['text_secondary']};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background: {COLORS['blue']} !important;
        color: white !important;
        border-color: {COLORS['blue']} !important;
    }}

    /* ── Progress bar ──────────────────────────────────────────── */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {COLORS['blue']}, {COLORS['gold']});
        border-radius: 8px;
    }}
    .stProgress > div > div {{
        background: {COLORS['navy_card']};
        border-radius: 8px;
    }}

    /* ── Chat ──────────────────────────────────────────────────── */
    .stChatMessage {{
        background: {COLORS['navy_card']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stChatInput"] {{
        background: {COLORS['navy_card']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        color: {COLORS['text_primary']} !important;
    }}

    /* ── Forms ─────────────────────────────────────────────────── */
    div[data-testid="stForm"] {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1.5rem;
    }}

    /* ── Dividers ──────────────────────────────────────────────── */
    hr {{
        border-color: {COLORS['border']} !important;
        opacity: 0.5;
    }}

    /* ── Alerts ────────────────────────────────────────────────── */
    .stAlert {{
        border-radius: 12px !important;
        border: none !important;
    }}
    div[data-testid="stAlert"][data-baseweb] {{
        border-radius: 12px;
    }}

    /* ── Links ─────────────────────────────────────────────────── */
    a {{
        color: {COLORS['blue_light']} !important;
    }}
    a:hover {{
        color: {COLORS['gold']} !important;
    }}

    /* ── Scrollbar ─────────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['navy']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['border']};
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['text_muted']};
    }}

    /* ── Custom Component Classes ──────────────────────────────── */
    .premium-card {{
        background: linear-gradient(135deg, {COLORS['navy_card']}, {COLORS['navy_light']});
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }}
    .premium-card:hover {{
        border-color: {COLORS['blue']};
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.15);
        transform: translateY(-2px);
    }}

    .hero-title {{
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, {COLORS['gold']}, {COLORS['gold_light']}, {COLORS['gold']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }}

    .hero-subtitle {{
        font-size: 1.2rem;
        text-align: center;
        color: {COLORS['text_secondary']};
        margin-bottom: 2rem;
        font-weight: 400;
    }}

    .agent-card {{
        background: linear-gradient(135deg, {COLORS['navy_card']}, {COLORS['navy_light']});
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 160px;
    }}
    .agent-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }}
    .agent-card h4 {{
        margin: 0.5rem 0 0.3rem;
        font-size: 1rem;
    }}
    .agent-card p {{
        margin: 0;
        color: {COLORS['text_secondary']};
        font-size: 0.8rem;
    }}
    .agent-icon {{
        font-size: 2rem;
        display: block;
        margin-bottom: 0.3rem;
    }}

    .stat-card {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1rem 1.2rem;
        text-align: center;
    }}
    .stat-card .stat-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
    }}
    .stat-card .stat-label {{
        font-size: 0.75rem;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }}
    .stat-card .stat-delta {{
        font-size: 0.8rem;
        margin-top: 4px;
    }}
    .stat-delta.positive {{ color: {COLORS['green']}; }}
    .stat-delta.negative {{ color: {COLORS['red']}; }}

    .lock-overlay {{
        position: relative;
        opacity: 0.5;
        pointer-events: none;
    }}
    .lock-badge {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.7);
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.9rem;
        color: {COLORS['gold']};
        font-weight: 600;
        z-index: 10;
    }}

    .premium-badge {{
        background: linear-gradient(135deg, {COLORS['gold']}, {COLORS['gold_dim']});
        color: {COLORS['navy']};
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 6px;
    }}

    .onboarding-step {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 2rem;
        max-width: 600px;
        margin: 0 auto;
    }}

    .feature-card {{
        background: linear-gradient(135deg, {COLORS['navy_card']}, {COLORS['navy_light']});
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }}
    .feature-card:hover {{
        border-color: {COLORS['blue']};
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.1);
    }}
    .feature-card .icon {{
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}
    .feature-card h4 {{
        color: {COLORS['gold']} !important;
        margin: 0.3rem 0;
    }}
    .feature-card p {{
        color: {COLORS['text_secondary']};
        font-size: 0.85rem;
        margin: 0;
    }}

    .module-card {{
        background: linear-gradient(135deg, {COLORS['navy_card']}, {COLORS['navy_light']});
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.2rem;
        transition: all 0.3s ease;
    }}
    .module-card:hover {{
        border-color: {COLORS['blue']};
        transform: translateY(-2px);
    }}

    .video-lesson-card {{
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 1rem;
        transition: all 0.3s ease;
    }}
    .video-lesson-card:hover {{
        border-color: {COLORS['blue']};
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.15);
    }}

    .duration-badge {{
        background: {COLORS['navy']};
        color: {COLORS['text_secondary']};
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 500;
    }}

    .achievement-badge {{
        display: inline-block;
        font-size: 2rem;
        margin: 4px;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    }}
    .achievement-badge.locked {{
        filter: grayscale(100%);
        opacity: 0.3;
    }}

    .comparison-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .comparison-table th {{
        background: {COLORS['navy_card']};
        color: {COLORS['text_primary']};
        padding: 12px 16px;
        text-align: left;
        border-bottom: 2px solid {COLORS['border']};
    }}
    .comparison-table td {{
        padding: 10px 16px;
        border-bottom: 1px solid {COLORS['border']};
        color: {COLORS['text_secondary']};
    }}
    .comparison-table tr:hover td {{
        background: {COLORS['navy_light']};
    }}

    /* ── Spinner replacement ───────────────────────────────────── */
    @keyframes pulse-ring {{
        0% {{ transform: scale(0.8); opacity: 1; }}
        50% {{ transform: scale(1.1); opacity: 0.5; }}
        100% {{ transform: scale(0.8); opacity: 1; }}
    }}
    .custom-spinner {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        background: {COLORS['navy_card']};
        border: 1px solid {COLORS['border']};
    }}
    .custom-spinner .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {COLORS['blue']};
        animation: pulse-ring 1.2s ease-in-out infinite;
    }}
    .custom-spinner .dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .custom-spinner .dot:nth-child(3) {{ animation-delay: 0.4s; }}

    /* ── Kids-friendly overrides ───────────────────────────────── */
    .kids-mode .premium-card {{
        border: 2px solid #06B6D4;
        background: linear-gradient(135deg, #0C4A6E, #164E63);
    }}
    .kids-mode h3, .kids-mode h4 {{
        color: #06B6D4 !important;
    }}

    /* ── Responsive ────────────────────────────────────────────── */
    @media (max-width: 768px) {{
        .hero-title {{ font-size: 2rem; }}
        .hero-subtitle {{ font-size: 1rem; }}
        .agent-card {{ min-height: 120px; padding: 0.8rem; }}
        .stat-card .stat-value {{ font-size: 1.4rem; }}
    }}
</style>
"""


def get_spinner_html(text: str = "Thinking...") -> str:
    """Custom loading spinner."""
    return f"""
    <div class="custom-spinner">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <span style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">{text}</span>
    </div>
    """


def inject_styles():
    """Inject all styles into the current Streamlit page. Call at the top of every page."""
    import streamlit as st
    st.markdown(get_global_css(), unsafe_allow_html=True)
