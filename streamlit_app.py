"""
Google Play Store Reviews Scraper
Run:  streamlit run play-store-scraper.py
Deps: pip install streamlit google-play-scraper pandas openpyxl requests markdown
"""

import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime
import time
import requests
import json
from io import BytesIO

try:
    import markdown as md_lib
    HAS_MD = True
except ImportError:
    HAS_MD = False

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Play Store Reviews Scraper",
    page_icon="★",
    layout="wide",
)

# ── Session state ────────────────────────────────────────────
for key, default in [
    ("df", None), ("meta", {}), ("chart_mode", "chart"),
    ("summary_text", None), ("dark_mode", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

dark = st.session_state.dark_mode


# ══════════════════════════════════════════════════════════════
# DESIGN TOKENS
# Inspired by Apple product pages: generous whitespace,
# large type, minimal chrome, pill CTAs, section rhythm.
# ══════════════════════════════════════════════════════════════

if dark:
    BG            = "#000000"
    BG_ELEVATED   = "#0d0d0d"
    SURFACE       = "#141414"
    SURFACE_ALT   = "#1a1a1a"
    BORDER        = "#222222"
    BORDER_SUB    = "#1c1c1c"

    TEXT_1        = "#f5f5f7"   # primary
    TEXT_2        = "#a1a1a6"   # secondary
    TEXT_3        = "#6e6e73"   # muted

    INPUT_BG      = "#1a1a1a"
    INPUT_BR      = "#333333"
    INPUT_TX      = "#f5f5f7"
    INPUT_PH      = "#555555"
    INPUT_FOCUS   = "#0071e3"

    TAG_BG        = "#2a2a2a"
    TAG_TX        = "#d2d2d7"

    DROP_BG       = "#1c1c1e"
    DROP_HOVER    = "#2c2c2e"
    DROP_TX       = "#f5f5f7"

    ACCENT_FILL   = "#f5f5f7"
    ACCENT_TEXT   = "#000000"
    ACCENT_HOVER  = "#d2d2d7"

    BTN_SEC_BG    = "#1a1a1a"
    BTN_SEC_TX    = "#f5f5f7"
    BTN_SEC_BR    = "#333333"
    BTN_SEC_HOVER = "#222222"

    CHART_CLR     = "#636366"

    CARD_BG       = "#141414"
    CARD_BR       = "#222222"
    CARD_LABEL    = "#86868b"
    CARD_VALUE    = "#f5f5f7"

    SUMMARY_BG    = "#0d0d0d"
    SUMMARY_BR    = "#1c1c1c"
    SUMMARY_TX    = "#d2d2d7"
    SUMMARY_H     = "#f5f5f7"

    SB_BG         = "#000000"
else:
    BG            = "#ffffff"
    BG_ELEVATED   = "#ffffff"
    SURFACE       = "#f5f5f7"
    SURFACE_ALT   = "#fbfbfd"
    BORDER        = "#d2d2d7"
    BORDER_SUB    = "#e8e8ed"

    TEXT_1        = "#1d1d1f"
    TEXT_2        = "#6e6e73"
    TEXT_3        = "#86868b"

    INPUT_BG      = "#ffffff"
    INPUT_BR      = "#d2d2d7"
    INPUT_TX      = "#1d1d1f"
    INPUT_PH      = "#86868b"
    INPUT_FOCUS   = "#0071e3"

    TAG_BG        = "#e8e8ed"
    TAG_TX        = "#1d1d1f"

    DROP_BG       = "#ffffff"
    DROP_HOVER    = "#f5f5f7"
    DROP_TX       = "#1d1d1f"

    ACCENT_FILL   = "#1d1d1f"
    ACCENT_TEXT   = "#ffffff"
    ACCENT_HOVER  = "#333336"

    BTN_SEC_BG    = "#f5f5f7"
    BTN_SEC_TX    = "#1d1d1f"
    BTN_SEC_BR    = "#d2d2d7"
    BTN_SEC_HOVER = "#e8e8ed"

    CHART_CLR     = "#1d1d1f"

    CARD_BG       = "#f5f5f7"
    CARD_BR       = "#e8e8ed"
    CARD_LABEL    = "#86868b"
    CARD_VALUE    = "#1d1d1f"

    SUMMARY_BG    = "#f5f5f7"
    SUMMARY_BR    = "#e8e8ed"
    SUMMARY_TX    = "#1d1d1f"
    SUMMARY_H     = "#1d1d1f"

    SB_BG         = "#000000"


# Sidebar is always dark
SB_TX         = "#f5f5f7"
SB_LABEL      = "#86868b"
SB_INPUT_BG   = "#1a1a1a"
SB_INPUT_BR   = "#333333"
SB_INPUT_TX   = "#f5f5f7"
SB_PH         = "#555555"
SB_DIV        = "#222222"
SB_TAG_BG     = "rgba(255,255,255,0.1)"


# ══════════════════════════════════════════════════════════════
# STYLESHEET
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>

/* =============================================================
   FONTS
   Apple uses SF Pro; we use the system font stack that includes
   SF Pro on Mac and Segoe UI on Windows.
   ============================================================= */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text',
                 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
}}


/* =============================================================
   1. PAGE
   ============================================================= */

.stApp {{
    background: {BG} !important;
}}
.block-container {{
    padding: 2.5rem 3.5rem 3rem !important;
    max-width: 1120px;
}}


/* =============================================================
   2. GLOBAL TEXT
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"],
.stApp [data-testid="stMainBlockContainer"] p,
.stApp [data-testid="stMainBlockContainer"] span,
.stApp [data-testid="stMainBlockContainer"] li,
.stApp [data-testid="stMainBlockContainer"] td,
.stApp [data-testid="stMainBlockContainer"] th,
.stApp [data-testid="stMainBlockContainer"] div,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] span,
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stText"] {{
    color: {TEXT_1} !important;
}}


/* =============================================================
   3. LABELS — every single variant Streamlit generates
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] label,
.stApp [data-testid="stMainBlockContainer"] label p,
.stApp [data-testid="stMainBlockContainer"] label span,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"],
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] span,
.stApp [data-testid="stMainBlockContainer"] .stTextInput label,
.stApp [data-testid="stMainBlockContainer"] .stTextInput label p,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput label,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput label p,
.stApp [data-testid="stMainBlockContainer"] .stSelectbox label,
.stApp [data-testid="stMainBlockContainer"] .stSelectbox label p,
.stApp [data-testid="stMainBlockContainer"] .stMultiSelect label,
.stApp [data-testid="stMainBlockContainer"] .stMultiSelect label p,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label span,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label p,
.stApp [data-testid="stMainBlockContainer"] .stRadio label,
.stApp [data-testid="stMainBlockContainer"] .stRadio label p {{
    color: {TEXT_2} !important;
}}


/* =============================================================
   4. INPUTS — text, number, textarea
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stTextInput input,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea {{
    background: {INPUT_BG} !important;
    color: {INPUT_TX} !important;
    border: 1px solid {INPUT_BR} !important;
    border-radius: 12px !important;
    padding: 0.55rem 0.85rem !important;
    font-size: 0.88rem !important;
    caret-color: {INPUT_TX} !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea:focus {{
    border-color: {INPUT_FOCUS} !important;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.15) !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input::placeholder,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea::placeholder {{
    color: {INPUT_PH} !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button {{
    color: {TEXT_2} !important;
    border-color: {INPUT_BR} !important;
    background: {INPUT_BG} !important;
    border-radius: 8px !important;
}}


/* =============================================================
   5. SELECT / DROPDOWN
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
    background: {INPUT_BG} !important;
    border-color: {INPUT_BR} !important;
    border-radius: 12px !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] span,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="singleValue"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="placeholder"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] input {{
    color: {INPUT_TX} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg {{
    fill: {TEXT_3} !important;
}}

/* Tags / pills */
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] {{
    background: {TAG_BG} !important;
    border: none !important;
    border-radius: 8px !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] span {{
    color: {TAG_TX} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg {{
    fill: {TAG_TX} !important;
}}


/* =============================================================
   6. DROPDOWN POPOVER
   ============================================================= */

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[data-baseweb="list"],
[data-baseweb="list"] ul {{
    background: {DROP_BG} !important;
    background-color: {DROP_BG} !important;
    border-color: {INPUT_BR} !important;
    border-radius: 12px !important;
    overflow: hidden;
}}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[data-baseweb="list"] li {{
    color: {DROP_TX} !important;
    background: transparent !important;
    padding: 0.5rem 0.85rem !important;
}}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[data-baseweb="list"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"],
[data-baseweb="menu"] li[aria-selected="true"],
[data-baseweb="list"] li[aria-selected="true"] {{
    background: {DROP_HOVER} !important;
}}
[data-baseweb="popover"] li span,
[data-baseweb="menu"] li span,
[data-baseweb="list"] li span {{
    color: {DROP_TX} !important;
}}


/* =============================================================
   7. HELP / TOOLTIP
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon,
.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon svg,
.stApp [data-testid="stMainBlockContainer"] [data-testid="tooltipHoverTarget"],
.stApp small {{
    color: {TEXT_3} !important;
    fill: {TEXT_3} !important;
}}


/* =============================================================
   8. METRIC CARDS — Apple comparison-card style
   ============================================================= */

div[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {CARD_BR};
    border-radius: 16px;
    padding: 20px 24px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,{('0.25' if dark else '0.06')});
}}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label p {{
    color: {CARD_LABEL} !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600 !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {CARD_VALUE} !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.02em;
}}


/* =============================================================
   9. SIDEBAR — always dark, Apple nav-bar feel
   ============================================================= */

[data-testid="stSidebar"] {{
    background: {SB_BG} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 2.2rem 1.6rem !important;
}}

/* Text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] label span,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stCheckbox label span {{
    color: {SB_TX} !important;
}}

/* Labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p {{
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {SB_LABEL} !important;
}}

/* Text inputs */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {{
    background: {SB_INPUT_BG} !important;
    border: 1px solid {SB_INPUT_BR} !important;
    color: {SB_INPUT_TX} !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.8rem !important;
    font-size: 0.88rem !important;
    caret-color: {SB_INPUT_TX} !important;
    transition: border-color 0.2s;
}}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {{
    border-color: #0071e3 !important;
    box-shadow: 0 0 0 3px rgba(0,113,227,0.2) !important;
}}
[data-testid="stSidebar"] .stTextInput input::placeholder {{
    color: {SB_PH} !important;
}}
[data-testid="stSidebar"] .stNumberInput button {{
    color: {SB_TX} !important;
    border-color: {SB_INPUT_BR} !important;
    background: {SB_INPUT_BG} !important;
    border-radius: 8px !important;
}}

/* Selects */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {SB_INPUT_BG} !important;
    border-color: {SB_INPUT_BR} !important;
    border-radius: 10px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] [class*="singleValue"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"],
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    color: {SB_INPUT_TX} !important;
    fill: {SB_INPUT_TX} !important;
}}

/* Multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: {SB_TAG_BG} !important;
    border: none !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
    color: #ffffff !important;
    fill: #ffffff !important;
}}

/* Tooltips */
[data-testid="stSidebar"] .stTooltipIcon,
[data-testid="stSidebar"] .stTooltipIcon svg {{
    color: rgba(255,255,255,0.3) !important;
    fill: rgba(255,255,255,0.3) !important;
}}

/* Dividers */
[data-testid="stSidebar"] hr {{
    border-color: {SB_DIV} !important;
    margin: 1.4rem 0 !important;
}}


/* =============================================================
   10. SIDEBAR BUTTONS — pill-shaped, Apple CTA style
   ============================================================= */

[data-testid="stSidebar"] .stButton > button {{
    background: #0071e3 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 980px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em;
    transition: all 0.2s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: #0077ed !important;
    transform: scale(1.02);
    box-shadow: 0 2px 12px rgba(0,113,227,0.35);
}}


/* =============================================================
   11. MAIN BUTTONS
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stButton > button {{
    background: {BTN_SEC_BG} !important;
    color: {BTN_SEC_TX} !important;
    border: 1px solid {BTN_SEC_BR} !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease;
}}
.stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background: {BTN_SEC_HOVER} !important;
    transform: scale(1.02);
}}

/* Download — see class-specific styles */

/* CSV — solid filled pill */
.stDownloadButton button[kind="primary"],
.stDownloadButton button[data-testid="stBaseButton-primary"] {{
    background: {ACCENT_FILL} !important;
    color: {ACCENT_TEXT} !important;
    border: none !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease;
}}
.stDownloadButton button[kind="primary"]:hover,
.stDownloadButton button[data-testid="stBaseButton-primary"]:hover {{
    background: {ACCENT_HOVER} !important;
    transform: scale(1.02);
}}

/* XLSX — outline pill */
.stDownloadButton button[kind="secondary"],
.stDownloadButton button[data-testid="stBaseButton-secondary"] {{
    background: transparent !important;
    color: {TEXT_1} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease;
}}
.stDownloadButton button[kind="secondary"]:hover,
.stDownloadButton button[data-testid="stBaseButton-secondary"]:hover {{
    background: {SURFACE} !important;
    border-color: {TEXT_3} !important;
    transform: scale(1.02);
}}


/* =============================================================
   12. STATUS / SPINNER
   ============================================================= */

[data-testid="stStatusWidget"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 16px !important;
}}
[data-testid="stStatusWidget"] p,
[data-testid="stStatusWidget"] span,
[data-testid="stStatusWidget"] div {{
    color: {TEXT_1} !important;
}}
.stSpinner > div > span {{
    color: {TEXT_2} !important;
}}


/* =============================================================
   13. DATAFRAME
   ============================================================= */

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 16px;
    overflow: hidden;
}}


/* =============================================================
   14. DIVIDERS
   ============================================================= */

.stApp hr {{
    border-color: {BORDER_SUB} !important;
}}


/* =============================================================
   15. CUSTOM HTML
   ============================================================= */

.app-header h1 {{
    color: {TEXT_1};
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.04em;
    line-height: 1.1;
}}
.app-sub {{
    color: {TEXT_3};
    font-size: 0.95rem;
    margin-top: 0.5rem;
    margin-bottom: 2rem;
    font-weight: 400;
}}
.section-hdr {{
    font-weight: 700;
    font-size: 1.15rem;
    color: {TEXT_1};
    margin: 2rem 0 0.8rem;
    letter-spacing: -0.02em;
}}
.empty-state {{
    text-align: center;
    padding: 8rem 2rem;
}}
.empty-state .icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
    color: {TEXT_3};
}}
.empty-state p {{
    font-size: 1rem;
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.7;
    color: {TEXT_3};
}}
.empty-state b {{
    color: {TEXT_2};
}}
.file-meta {{
    margin-top: 0.8rem;
    font-size: 0.78rem;
    color: {TEXT_3};
    line-height: 1.5;
    font-weight: 500;
}}
.file-meta b {{
    color: {TEXT_2};
    font-weight: 600;
}}

/* Summary */
.summary-card {{
    background: {SUMMARY_BG};
    border: 1px solid {SUMMARY_BR};
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    line-height: 1.8;
    font-size: 0.9rem;
    color: {SUMMARY_TX};
}}
.summary-card p {{ color: {SUMMARY_TX} !important; }}
.summary-card li {{ color: {SUMMARY_TX} !important; margin-bottom: 0.25rem; }}
.summary-card ul {{ padding-left: 1.2rem; margin: 0.3rem 0 0.8rem; }}
.summary-card ol {{ padding-left: 1.2rem; margin: 0.3rem 0 0.8rem; }}
.summary-card h1, .summary-card h2, .summary-card h3,
.summary-card h4, .summary-card h5, .summary-card strong {{
    color: {SUMMARY_H} !important;
}}
.summary-card h2 {{
    font-size: 1rem;
    font-weight: 700;
    margin: 1.2rem 0 0.4rem;
    letter-spacing: -0.01em;
}}
.summary-card h3 {{
    font-size: 0.92rem;
    font-weight: 700;
    margin: 1rem 0 0.3rem;
}}
.summary-card h4 {{
    font-size: 0.88rem;
    font-weight: 700;
    margin: 1rem 0 0.3rem;
}}
.summary-card h2:first-child,
.summary-card h3:first-child,
.summary-card h4:first-child {{ margin-top: 0; }}

/* Expander */
[data-testid="stExpander"] {{
    border-color: {BORDER} !important;
    background: {SURFACE} !important;
    border-radius: 16px !important;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {{
    color: {TEXT_1} !important;
}}
[data-testid="stExpander"] svg {{
    fill: {TEXT_2} !important;
}}


/* =============================================================
   GLOBAL SVG / ICON FIX — arrows, chevrons, close buttons
   ============================================================= */

/* Main area icons */
.stApp [data-testid="stMainBlockContainer"] svg {{
    fill: {TEXT_2} !important;
    color: {TEXT_2} !important;
}}
.stApp [data-testid="stMainBlockContainer"] svg path {{
    fill: {TEXT_2} !important;
}}
/* Sidebar collapse / expand arrow */
[data-testid="stSidebar"] svg,
[data-testid="stSidebar"] svg path,
button[data-testid="stSidebarCollapseButton"] svg,
button[data-testid="stSidebarCollapseButton"] svg path,
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] svg path {{
    fill: {SB_TX} !important;
    color: {SB_TX} !important;
}}
/* Select dropdown chevron — main area */
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg path {{
    fill: {TEXT_3} !important;
}}
/* Select dropdown chevron — sidebar */
[data-testid="stSidebar"] [data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] svg path {{
    fill: {SB_INPUT_TX} !important;
}}
/* Number input stepper arrows */
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button svg,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button svg path {{
    fill: {TEXT_2} !important;
}}
[data-testid="stSidebar"] .stNumberInput button svg,
[data-testid="stSidebar"] .stNumberInput button svg path {{
    fill: {SB_TX} !important;
}}
/* Multiselect close (x) icon */
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg path {{
    fill: {TAG_TX} !important;
}}
/* Header hamburger / top-bar icons */
[data-testid="stHeader"] svg,
[data-testid="stHeader"] svg path,
[data-testid="stHeader"] button svg,
[data-testid="stHeader"] button svg path {{
    fill: {TEXT_2} !important;
    color: {TEXT_2} !important;
}}
/* Status widget icons */
[data-testid="stStatusWidget"] svg,
[data-testid="stStatusWidget"] svg path {{
    fill: {TEXT_2} !important;
}}
/* Bar chart axis labels */
.stApp [data-testid="stVegaLiteChart"] text {{
    fill: {TEXT_3} !important;
}}


</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>Play Store<br>Reviews Scraper.</h1>
</div>
<p class="app-sub">Pull, preview, and export Google Play reviews for any app.</p>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### Settings")
    st.divider()

    app_id = st.text_input(
        "APP ID",
        placeholder="com.example.app",
        help="From the Play Store URL: play.google.com/store/apps/details?id=com.example.app",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        country = st.text_input("COUNTRY", value="in", help="ISO alpha-2 code")
    with col_b:
        count = st.number_input("REVIEWS", min_value=1, max_value=10000, value=200, step=50)

    sort_order = st.selectbox("SORT BY", ["Newest", "Most Relevant"])

    filter_score = st.multiselect(
        "STAR FILTER",
        options=[1, 2, 3, 4, 5],
        default=[],
        help="Leave empty for all ratings",
    )

    include_version = st.checkbox("Include App Version column", value=False)

    st.divider()
    scrape = st.button("Start Scraping", use_container_width=True)

    st.divider()
    mode_label = "Light Mode" if dark else "Dark Mode"
    if st.button(mode_label, use_container_width=True, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


# ── Scraping ─────────────────────────────────────────────────
SORT_MAP = {"Most Relevant": Sort.MOST_RELEVANT, "Newest": Sort.NEWEST}

if scrape:
    if not app_id.strip():
        st.error("Enter an App ID to continue.")
        st.stop()

    st.session_state.summary_text = None
    st.session_state.chart_mode = "chart"

    sort_val = SORT_MAP[sort_order]
    filter_val = filter_score if filter_score else None

    with st.status(f"Scraping {app_id}  ·  {country.upper()}  ·  {count} reviews", expanded=True) as status:
        try:
            all_reviews = []
            batch_size = min(count, 200)
            token = None

            while len(all_reviews) < count:
                remaining = count - len(all_reviews)
                fetch_count = min(batch_size, remaining)
                st.write(f"Fetching batch... ({len(all_reviews)}/{count})")

                result, token = reviews(
                    app_id,
                    lang="en",
                    country=country.strip().lower(),
                    sort=sort_val,
                    count=fetch_count,
                    filter_score_with=filter_val[0] if filter_val and len(filter_val) == 1 else None,
                    continuation_token=token,
                )

                if not result:
                    break
                all_reviews.extend(result)
                if token is None:
                    break
                time.sleep(0.3)

            status.update(label=f"Done — {len(all_reviews)} reviews fetched", state="complete")

        except Exception as e:
            st.error(f"Scrape failed: {e}")
            st.stop()

    if not all_reviews:
        st.warning("No reviews found. Check the App ID and country code.")
        st.stop()

    df = pd.DataFrame(all_reviews)

    keep = ["userName", "score", "content", "at", "reviewCreatedVersion"]
    keep = [c for c in keep if c in df.columns]
    df = df[keep]

    rename = {
        "userName": "User",
        "score": "Rating",
        "content": "Review",
        "at": "Date",
        "reviewCreatedVersion": "App Version",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M")

    if filter_val and len(filter_val) > 1:
        df = df[df["Rating"].isin(filter_val)]

    st.session_state.df = df
    st.session_state.meta = {"app_id": app_id, "country": country}


# ── Display ──────────────────────────────────────────────────
df = st.session_state.df

if df is not None and not df.empty:
    meta = st.session_state.meta

    show_cols = ["User", "Rating", "Review", "Date"]
    if include_version and "App Version" in df.columns:
        show_cols.append("App Version")
    display_df = df[[c for c in show_cols if c in df.columns]]

    # ── Metrics ──────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    avg = df["Rating"].mean() if "Rating" in df.columns else 0
    m1.metric("Total Reviews", f"{len(df):,}")
    m2.metric("Avg Rating", f"{avg:.2f} ★")
    m3.metric("5-Star", f"{(df['Rating'] == 5).sum():,}" if "Rating" in df.columns else "—")
    m4.metric("1-Star", f"{(df['Rating'] == 1).sum():,}" if "Rating" in df.columns else "—")

    # ── Rating distribution ──────────────────────────────────
    st.markdown('<div class="section-hdr">Rating Distribution</div>', unsafe_allow_html=True)

    tog1, tog2, _ = st.columns([0.08, 0.08, 0.84])
    with tog1:
        if st.button("Chart", key="btn_chart", use_container_width=True):
            st.session_state.chart_mode = "chart"
            st.rerun()
    with tog2:
        if st.button("Table", key="btn_table", use_container_width=True):
            st.session_state.chart_mode = "table"
            st.rerun()

    if "Rating" in df.columns:
        dist = df["Rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        if st.session_state.chart_mode == "chart":
            st.bar_chart(dist, color=CHART_CLR, height=220)
        else:
            dist_df = pd.DataFrame({
                "Rating": [f"{i} ★" for i in range(1, 6)],
                "Count": [int(dist.get(i, 0)) for i in range(1, 6)],
                "Share": [f"{dist.get(i, 0) / len(df) * 100:.1f}%" for i in range(1, 6)],
            })
            st.dataframe(dist_df, use_container_width=False, hide_index=True)

    # ── Reviews table ────────────────────────────────────────
    st.markdown('<div class="section-hdr">Reviews</div>', unsafe_allow_html=True)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=480,
        column_config={
            "Rating": st.column_config.NumberColumn(format="%d ★"),
            "Review": st.column_config.TextColumn(width="large"),
        },
    )

    # ── Export ────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Export</div>', unsafe_allow_html=True)

    fname_base = f"{meta.get('app_id', 'app')}_{meta.get('country', 'xx')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

    dl1, dl2, dl_meta = st.columns([0.15, 0.15, 0.7])
    with dl1:
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{fname_base}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )
    with dl2:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            display_df.to_excel(writer, index=False, sheet_name="Reviews")
        xlsx_data = buffer.getvalue()
        st.download_button(
            label="Download XLSX",
            data=xlsx_data,
            file_name=f"{fname_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.xml",
            use_container_width=True,
            type="secondary",
        )
    with dl_meta:
        st.markdown(f"""
        <div class="file-meta">
            <b>{len(display_df):,}</b> rows  ·  <b>{len(display_df.columns)}</b> cols  ·  {len(csv_data)/1024:.0f} KB
        </div>
        """, unsafe_allow_html=True)

    # ── AI Summary ───────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">AI Summary</div>', unsafe_allow_html=True)

    if st.button("Summarize Reviews", use_container_width=False):
        reviews_text = "\n\n".join(
            f"[{row.get('Rating', '?')}★] {row.get('Review', '')}"
            for _, row in df.head(300).iterrows()
        )

        system_prompt = (
            "Act as an expert App Product Manager and Data Analyst. "
            "I am going to provide you with a batch of user reviews from the Google Play Store for an app. "
            "Your task is to analyze these reviews and provide a structured, actionable summary.\n\n"
            "Please format your response with the following sections:\n"
            "1. Overall Sentiment: A brief paragraph summarizing the general mood of the users "
            "(Positive, Negative, Mixed) and the primary reasons why.\n"
            "2. Top Praises (Pros): List the top 3-5 things users love most about the app.\n"
            "3. Top Complaints (Cons): List the top 3-5 pain points, frustrations, or negative experiences users are having.\n"
            "4. Reported Bugs: Highlight any specific technical issues, crashes, or glitches mentioned by multiple users.\n"
            "5. Feature Requests: Note any specific features or improvements users are asking for.\n\n"
            "Please ignore spam or overly generic reviews (e.g., just saying 'good' or 'bad' without context).\n\n"
            "IMPORTANT WRITING RULES — follow these strictly:\n"
            "- Do NOT use any of these words: crucial, pivotal, landscape, testament, underscores, "
            "notably, arguably, it's important to note, it's worth noting, delve, streamline, "
            "leverage, robust, comprehensive, cutting-edge, holistic, game-changer, paradigm, "
            "synergy, innovative, seamless, dynamic, transformative.\n"
            "- Do NOT use em dashes. Use commas or periods instead.\n"
            "- Do NOT use rule-of-three constructions (e.g., 'fast, reliable, and intuitive').\n"
            "- Write in plain, direct language. Short sentences. No filler.\n"
            "- Sound like a sharp analyst writing a Slack message to their team, not a blog post.\n"
            "- Use markdown formatting: **bold** for section headers, bullet points for lists."
        )

        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nHere are the reviews:\n\n{reviews_text}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            },
        }

        with st.spinner("Generating summary..."):
            try:
                resp = requests.post(url, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                summary = data["candidates"][0]["content"]["parts"][0]["text"]
                st.session_state.summary_text = summary
            except Exception as e:
                st.error(f"Summary generation failed: {e}")

    if st.session_state.summary_text:
        if HAS_MD:
            html_summary = md_lib.markdown(st.session_state.summary_text)
        else:
            html_summary = st.session_state.summary_text
        st.markdown(
            f'<div class="summary-card">{html_summary}</div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">★</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start Scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
