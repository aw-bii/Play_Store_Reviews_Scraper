"""
Google Play Store Reviews Scraper
Bertelsmann Corporate Design — As of January 2022
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

st.set_page_config(
    page_title="Play Store Reviews Scraper",
    page_icon="★",
    layout="wide",
    initial_sidebar_state="expanded",
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
# BERTELSMANN DESIGN TOKENS
# Source: Corporate Design Manual, January 2022
#
# Primary:   Be Blue #002d64 | Be Blue 2 #afbed2 | Be Blue 3 #8ca0b9
#            Be Blue 4 #6482a0 | Be Blue 5 #415f8c
# Gray:      Be Gray #464646 | Be Gray 2 #dcdcdc | Be Gray 3 #cdcdcd
#            Be Gray 4 #a0a0a0 | Be Gray 5 #646464
# Secondary: Be Red #e60028 | Be Orange #f07d19 | Be Aquamarin #0090a0
# Typography: Arial (screen substitute for Univers)
# Charts:    2D only, no shading, primary colors, dotted grid
# ══════════════════════════════════════════════════════════════

# Bertelsmann brand palette
BE_BLUE     = "#002d64"
BE_BLUE_2   = "#afbed2"
BE_BLUE_3   = "#8ca0b9"
BE_BLUE_4   = "#6482a0"
BE_BLUE_5   = "#415f8c"
BE_GRAY     = "#464646"
BE_GRAY_2   = "#dcdcdc"
BE_GRAY_3   = "#cdcdcd"
BE_GRAY_4   = "#a0a0a0"
BE_GRAY_5   = "#646464"
BE_RED      = "#e60028"
BE_RED_2    = "#eb5a50"
BE_ORANGE   = "#f07d19"
BE_AQUA     = "#0090a0"

if dark:
    BG            = "#0a0e18"
    SURFACE       = "#0f1525"
    SURFACE_ALT   = "#141c30"
    BORDER        = "#1e2a45"
    BORDER_SUB    = "#172035"

    TEXT_1        = "#e8ecf2"
    TEXT_2        = BE_BLUE_2
    TEXT_3        = BE_BLUE_3

    INPUT_BG      = "#141c30"
    INPUT_BR      = "#253555"
    INPUT_TX      = "#e8ecf2"
    INPUT_PH      = "#506080"
    INPUT_FOCUS   = BE_BLUE_3

    TAG_BG        = "#1e2a45"
    TAG_TX        = BE_BLUE_2

    DROP_BG       = "#141c30"
    DROP_HOVER    = "#1e2a45"
    DROP_TX       = "#e8ecf2"

    ACCENT_BLUE   = BE_BLUE_2
    CTA_BG        = BE_RED
    CTA_TX        = "#ffffff"
    CTA_HOVER     = BE_RED_2

    BTN_SEC_BG    = "#141c30"
    BTN_SEC_TX    = "#e8ecf2"
    BTN_SEC_BR    = "#253555"
    BTN_SEC_HOVER = "#1e2a45"

    OUTLINE_BG    = "transparent"
    OUTLINE_TX    = "#e8ecf2"
    OUTLINE_BR    = "#354565"
    OUTLINE_HOVER = "#1e2a45"
    OUTLINE_BR_H  = BE_BLUE_3

    CHART_CLR     = BE_BLUE_3

    CARD_BG       = "#0f1525"
    CARD_BR       = "#1e2a45"
    CARD_LABEL    = BE_BLUE_3
    CARD_VALUE    = "#e8ecf2"
    CARD_SHADOW   = "0.3"

    SUMMARY_BG    = "#0a0e18"
    SUMMARY_BR    = "#1e2a45"
    SUMMARY_TX    = BE_BLUE_2
    SUMMARY_H     = "#e8ecf2"

    SB_BG         = BE_BLUE
else:
    BG            = "#ffffff"
    SURFACE       = "#f5f6f8"
    SURFACE_ALT   = "#fafbfc"
    BORDER        = BE_GRAY_2
    BORDER_SUB    = "#e8ecf0"

    TEXT_1        = BE_GRAY
    TEXT_2        = BE_GRAY_5
    TEXT_3        = BE_GRAY_4

    INPUT_BG      = "#ffffff"
    INPUT_BR      = BE_GRAY_3
    INPUT_TX      = BE_GRAY
    INPUT_PH      = BE_GRAY_4
    INPUT_FOCUS   = BE_BLUE

    TAG_BG        = BE_BLUE_2
    TAG_TX        = BE_BLUE

    DROP_BG       = "#ffffff"
    DROP_HOVER    = "#f5f6f8"
    DROP_TX       = BE_GRAY

    ACCENT_BLUE   = BE_BLUE
    CTA_BG        = BE_RED
    CTA_TX        = "#ffffff"
    CTA_HOVER     = BE_RED_2

    BTN_SEC_BG    = "#f5f6f8"
    BTN_SEC_TX    = BE_GRAY
    BTN_SEC_BR    = BE_GRAY_3
    BTN_SEC_HOVER = BE_GRAY_2

    OUTLINE_BG    = "transparent"
    OUTLINE_TX    = BE_GRAY
    OUTLINE_BR    = BE_GRAY_3
    OUTLINE_HOVER = "#f5f6f8"
    OUTLINE_BR_H  = BE_GRAY_5

    CHART_CLR     = BE_BLUE

    CARD_BG       = "#f5f6f8"
    CARD_BR       = "#e8ecf0"
    CARD_LABEL    = BE_GRAY_5
    CARD_VALUE    = BE_BLUE
    CARD_SHADOW   = "0.05"

    SUMMARY_BG    = "#f5f6f8"
    SUMMARY_BR    = "#e8ecf0"
    SUMMARY_TX    = BE_GRAY
    SUMMARY_H     = BE_BLUE

    SB_BG         = BE_BLUE

# Sidebar always Bertelsmann Blue
SB_TX         = "#ffffff"
SB_LABEL      = BE_BLUE_2
SB_INPUT_BG   = "rgba(255,255,255,0.08)"
SB_INPUT_BR   = "rgba(255,255,255,0.18)"
SB_INPUT_TX   = "#ffffff"
SB_PH         = "rgba(175,190,210,0.6)"
SB_DIV        = "rgba(255,255,255,0.12)"
SB_TAG_BG     = "rgba(255,255,255,0.12)"


# ══════════════════════════════════════════════════════════════
# STYLESHEET
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>

/* =============================================================
   FONTS — Arial (Bertelsmann screen substitute for Univers)
   ============================================================= */

*, *::before, *::after {{
    font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif !important;
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
   2. FIXED SIDEBAR — Bertelsmann Blue
   ============================================================= */

[data-testid="stSidebar"] {{
    background: {SB_BG} !important;
    min-width: 320px !important;
    max-width: 320px !important;
    transform: none !important;
    transition: none !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 2.2rem 1.6rem !important;
}}
button[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important; height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
}}


/* =============================================================
   3. GLOBAL TEXT
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
   4. LABELS
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] label,
.stApp [data-testid="stMainBlockContainer"] label p,
.stApp [data-testid="stMainBlockContainer"] label span,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"],
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] span,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label span,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label p {{
    color: {TEXT_2} !important;
}}


/* =============================================================
   5. INPUTS
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stTextInput input,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea {{
    background: {INPUT_BG} !important;
    color: {INPUT_TX} !important;
    border: 1px solid {INPUT_BR} !important;
    border-radius: 4px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 0.88rem !important;
    caret-color: {INPUT_TX} !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input:focus {{
    border-color: {INPUT_FOCUS} !important;
    box-shadow: 0 0 0 2px {INPUT_FOCUS}33 !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input::placeholder {{
    color: {INPUT_PH} !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button {{
    color: {TEXT_2} !important;
    border-color: {INPUT_BR} !important;
    background: {INPUT_BG} !important;
}}


/* =============================================================
   6. SELECT / DROPDOWN
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
    background: {INPUT_BG} !important;
    border-color: {INPUT_BR} !important;
    border-radius: 4px !important;
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
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] {{
    background: {TAG_BG} !important;
    border: none !important; border-radius: 3px !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] span {{ color: {TAG_TX} !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg {{ fill: {TAG_TX} !important; }}


/* =============================================================
   7. DROPDOWN POPOVER
   ============================================================= */

[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="menu"], [data-baseweb="menu"] ul,
[data-baseweb="list"], [data-baseweb="list"] ul {{
    background: {DROP_BG} !important;
    border-color: {INPUT_BR} !important;
    border-radius: 4px !important;
}}
[data-baseweb="popover"] li, [data-baseweb="menu"] li, [data-baseweb="list"] li {{
    color: {DROP_TX} !important;
    background: transparent !important;
    padding: 0.45rem 0.75rem !important;
}}
[data-baseweb="popover"] li:hover, [data-baseweb="menu"] li:hover, [data-baseweb="list"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"], [data-baseweb="menu"] li[aria-selected="true"] {{
    background: {DROP_HOVER} !important;
}}
[data-baseweb="popover"] li span, [data-baseweb="menu"] li span {{ color: {DROP_TX} !important; }}


/* =============================================================
   8. HELP / TOOLTIP
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon,
.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon svg,
.stApp small {{
    color: {TEXT_3} !important; fill: {TEXT_3} !important;
}}


/* =============================================================
   9. METRIC CARDS — clean Bertelsmann style
   ============================================================= */

div[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {CARD_BR};
    border-radius: 4px;
    padding: 18px 22px;
    transition: box-shadow 0.15s ease;
}}
div[data-testid="stMetric"]:hover {{
    box-shadow: 0 2px 12px rgba(0,45,100,{CARD_SHADOW});
}}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] label p {{
    color: {CARD_LABEL} !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600 !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {CARD_VALUE} !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}}


/* =============================================================
   10. SIDEBAR — text, inputs, selects
   ============================================================= */

[data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] li,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] label p,
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
[data-testid="stSidebar"] label, [data-testid="stSidebar"] label p {{
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {SB_LABEL} !important;
}}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {{
    background: {SB_INPUT_BG} !important;
    border: 1px solid {SB_INPUT_BR} !important;
    color: {SB_INPUT_TX} !important;
    border-radius: 4px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 0.88rem !important;
    caret-color: {SB_INPUT_TX} !important;
}}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {{
    border-color: {BE_BLUE_2} !important;
    box-shadow: 0 0 0 2px rgba(175,190,210,0.25) !important;
}}
[data-testid="stSidebar"] .stTextInput input::placeholder {{ color: {SB_PH} !important; }}
[data-testid="stSidebar"] .stNumberInput button {{
    color: {SB_TX} !important; border-color: {SB_INPUT_BR} !important;
    background: {SB_INPUT_BG} !important; border-radius: 3px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {SB_INPUT_BG} !important;
    border-color: {SB_INPUT_BR} !important;
    border-radius: 4px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] [class*="singleValue"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"],
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    color: {SB_INPUT_TX} !important; fill: {SB_INPUT_TX} !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: {SB_TAG_BG} !important; border: none !important; border-radius: 3px !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] svg {{ color: #fff !important; fill: #fff !important; }}
[data-testid="stSidebar"] .stTooltipIcon,
[data-testid="stSidebar"] .stTooltipIcon svg {{ color: rgba(255,255,255,0.3) !important; fill: rgba(255,255,255,0.3) !important; }}
[data-testid="stSidebar"] hr {{ border-color: {SB_DIV} !important; margin: 1.4rem 0 !important; }}


/* =============================================================
   11. SIDEBAR BUTTONS — Be Red CTA
   ============================================================= */

[data-testid="stSidebar"] .stButton > button {{
    background: {CTA_BG} !important;
    color: {CTA_TX} !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    transition: all 0.15s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {CTA_HOVER} !important;
    box-shadow: 0 2px 10px rgba(230,0,40,0.3);
}}


/* =============================================================
   12. MAIN BUTTONS
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] .stButton > button {{
    background: {BTN_SEC_BG} !important;
    color: {BTN_SEC_TX} !important;
    border: 1px solid {BTN_SEC_BR} !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease;
}}
.stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background: {BTN_SEC_HOVER} !important;
}}


/* =============================================================
   13. DOWNLOAD BUTTONS — outline style, both identical
   ============================================================= */

.stDownloadButton > button,
.stDownloadButton button[kind="primary"],
.stDownloadButton button[kind="secondary"],
.stDownloadButton button[data-testid="stBaseButton-primary"],
.stDownloadButton button[data-testid="stBaseButton-secondary"] {{
    background: {OUTLINE_BG} !important;
    color: {OUTLINE_TX} !important;
    border: 1.5px solid {OUTLINE_BR} !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease;
}}
.stDownloadButton > button:hover,
.stDownloadButton button[kind="primary"]:hover,
.stDownloadButton button[kind="secondary"]:hover {{
    background: {OUTLINE_HOVER} !important;
    border-color: {OUTLINE_BR_H} !important;
}}


/* =============================================================
   14. STATUS WIDGET — fixed, no collapse
   ============================================================= */

[data-testid="stStatusWidget"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 4px !important;
    transition: none !important;
}}
[data-testid="stStatusWidget"] * {{ transition: none !important; animation: none !important; }}
[data-testid="stStatusWidget"] p, [data-testid="stStatusWidget"] span,
[data-testid="stStatusWidget"] div {{ color: {TEXT_1} !important; }}
[data-testid="stStatusWidget"] summary {{ pointer-events: none !important; cursor: default !important; }}
[data-testid="stStatusWidget"] summary svg {{ display: none !important; }}
.stSpinner > div > span {{ color: {TEXT_2} !important; }}


/* =============================================================
   15. DATAFRAME & CHART — non-interactive
   ============================================================= */

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER}; border-radius: 4px; overflow: hidden;
}}
[data-testid="stVegaLiteChart"] canvas {{ pointer-events: none !important; }}
[data-testid="stVegaLiteChart"] {{ pointer-events: none !important; }}
.stApp [data-testid="stVegaLiteChart"] text {{ fill: {TEXT_3} !important; }}


/* =============================================================
   16. CHART/TABLE TOGGLE — Be Blue pill
   ============================================================= */

.viz-toggle .stButton > button {{
    background: transparent !important;
    color: {ACCENT_BLUE} !important;
    border: 1.5px solid {ACCENT_BLUE} !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    padding: 0.28rem 0.9rem !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.viz-toggle .stButton > button:hover {{
    background: {ACCENT_BLUE} !important;
    color: #ffffff !important;
}}


/* =============================================================
   17. DIVIDERS
   ============================================================= */

.stApp hr {{ border-color: {BORDER_SUB} !important; }}


/* =============================================================
   18. SVG / ICON FIX
   ============================================================= */

.stApp [data-testid="stMainBlockContainer"] svg {{ fill: {TEXT_2} !important; color: {TEXT_2} !important; }}
.stApp [data-testid="stMainBlockContainer"] svg path {{ fill: {TEXT_2} !important; }}
[data-testid="stSidebar"] svg, [data-testid="stSidebar"] svg path {{ fill: {SB_TX} !important; color: {SB_TX} !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg path {{ fill: {TEXT_3} !important; }}
[data-testid="stSidebar"] [data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] svg path {{ fill: {SB_INPUT_TX} !important; }}
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button svg path {{ fill: {TEXT_2} !important; }}
[data-testid="stSidebar"] .stNumberInput button svg path {{ fill: {SB_TX} !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg path {{ fill: {TAG_TX} !important; }}
[data-testid="stHeader"] svg, [data-testid="stHeader"] svg path {{ fill: {TEXT_2} !important; color: {TEXT_2} !important; }}
[data-testid="stStatusWidget"] svg path {{ fill: {TEXT_2} !important; }}
.viz-toggle .stButton > button svg, .viz-toggle .stButton > button svg path {{ fill: {ACCENT_BLUE} !important; }}


/* =============================================================
   19. CUSTOM HTML
   ============================================================= */

.app-header h1 {{
    color: {BE_BLUE if not dark else '#e8ecf2'};
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}}
.app-sub {{
    color: {TEXT_3};
    font-size: 0.92rem;
    margin-top: 0.4rem;
    margin-bottom: 2rem;
}}
.section-hdr {{
    font-weight: 700;
    font-size: 1.05rem;
    color: {BE_BLUE if not dark else '#e8ecf2'};
    margin: 2rem 0 0.7rem;
    letter-spacing: -0.01em;
}}
.empty-state {{
    text-align: center; padding: 8rem 2rem;
}}
.empty-state .icon {{ font-size: 2.4rem; margin-bottom: 1rem; color: {TEXT_3}; }}
.empty-state p {{ font-size: 0.95rem; max-width: 360px; margin: 0 auto; line-height: 1.7; color: {TEXT_3}; }}
.empty-state b {{ color: {TEXT_2}; }}
.file-meta {{ margin-top: 0.8rem; font-size: 0.78rem; color: {TEXT_3}; font-weight: 500; }}
.file-meta b {{ color: {TEXT_2}; font-weight: 600; }}

/* Summary card */
.summary-card {{
    background: {SUMMARY_BG};
    border: 1px solid {SUMMARY_BR};
    border-radius: 4px;
    padding: 1.6rem 1.8rem;
    margin-top: 0.8rem;
    line-height: 1.75;
    font-size: 0.9rem;
    color: {SUMMARY_TX};
}}
.summary-card p {{ color: {SUMMARY_TX} !important; }}
.summary-card li {{ color: {SUMMARY_TX} !important; margin-bottom: 0.2rem; }}
.summary-card ul {{ padding-left: 1.2rem; margin: 0.3rem 0 0.6rem; }}
.summary-card ol {{ padding-left: 1.2rem; margin: 0.3rem 0 0.6rem; }}
.summary-card h1, .summary-card h2, .summary-card h3,
.summary-card h4, .summary-card h5, .summary-card strong {{ color: {SUMMARY_H} !important; }}
.summary-card h2 {{ font-size: 0.95rem; font-weight: 700; margin: 1rem 0 0.4rem; }}
.summary-card h3 {{ font-size: 0.9rem; font-weight: 700; margin: 0.8rem 0 0.3rem; }}
.summary-card h4 {{ font-size: 0.85rem; font-weight: 700; margin: 0.8rem 0 0.3rem; }}
.summary-card h2:first-child, .summary-card h3:first-child, .summary-card h4:first-child {{ margin-top: 0; }}

/* Expander */
[data-testid="stExpander"] {{ border-color: {BORDER} !important; background: {SURFACE} !important; border-radius: 4px !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary span {{ color: {TEXT_1} !important; }}
[data-testid="stExpander"] svg {{ fill: {TEXT_2} !important; }}

</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>Play Store<br>Reviews Scraper</h1>
</div>
<p class="app-sub">Pull, preview, and export Google Play reviews for any app.</p>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### Settings")
    st.divider()

    app_id = st.text_input(
        "APP ID", placeholder="com.example.app",
        help="From the Play Store URL: play.google.com/store/apps/details?id=com.example.app",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        country = st.text_input("COUNTRY", value="in", help="ISO alpha-2 code")
    with col_b:
        count = st.number_input("REVIEWS", min_value=1, max_value=10000, value=200, step=50)

    sort_order = st.selectbox("SORT BY", ["Newest", "Most Relevant"])
    filter_score = st.multiselect("STAR FILTER", options=[1, 2, 3, 4, 5], default=[], help="Leave empty for all ratings")
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
            all_reviews, batch_size, token = [], min(count, 200), None
            while len(all_reviews) < count:
                fetch_count = min(batch_size, count - len(all_reviews))
                st.write(f"Fetching batch... ({len(all_reviews)}/{count})")
                result, token = reviews(
                    app_id, lang="en", country=country.strip().lower(), sort=sort_val,
                    count=fetch_count,
                    filter_score_with=filter_val[0] if filter_val and len(filter_val) == 1 else None,
                    continuation_token=token,
                )
                if not result: break
                all_reviews.extend(result)
                if token is None: break
                time.sleep(0.3)
            status.update(label=f"Done — {len(all_reviews)} reviews fetched", state="complete")
        except Exception as e:
            st.error(f"Scrape failed: {e}"); st.stop()

    if not all_reviews:
        st.warning("No reviews found. Check the App ID and country code."); st.stop()

    df = pd.DataFrame(all_reviews)
    keep = [c for c in ["userName", "score", "content", "at", "reviewCreatedVersion"] if c in df.columns]
    df = df[keep]
    df.rename(columns={"userName": "User", "score": "Rating", "content": "Review", "at": "Date", "reviewCreatedVersion": "App Version"}, inplace=True)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M")
    if filter_val and len(filter_val) > 1:
        df = df[df["Rating"].isin(filter_val)]
    st.session_state.df = df
    st.session_state.meta = {"app_id": app_id, "country": country}


# ══════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════

df = st.session_state.df

if df is not None and not df.empty:
    meta = st.session_state.meta
    show_cols = ["User", "Rating", "Review", "Date"]
    if include_version and "App Version" in df.columns:
        show_cols.append("App Version")
    display_df = df[[c for c in show_cols if c in df.columns]]

    # ── 1. Metrics ───────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    avg = df["Rating"].mean() if "Rating" in df.columns else 0
    m1.metric("Total Reviews", f"{len(df):,}")
    m2.metric("Avg Rating", f"{avg:.2f} ★")
    m3.metric("5-Star", f"{(df['Rating'] == 5).sum():,}" if "Rating" in df.columns else "—")
    m4.metric("1-Star", f"{(df['Rating'] == 1).sum():,}" if "Rating" in df.columns else "—")

    # ── 2. Rating distribution ───────────────────────────────
    st.markdown('<div class="section-hdr">Rating Distribution</div>', unsafe_allow_html=True)
    tog1, tog2, _ = st.columns([0.08, 0.08, 0.84])
    with tog1:
        st.markdown('<div class="viz-toggle">', unsafe_allow_html=True)
        if st.button("Chart", key="btn_chart", use_container_width=True):
            st.session_state.chart_mode = "chart"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tog2:
        st.markdown('<div class="viz-toggle">', unsafe_allow_html=True)
        if st.button("Table", key="btn_table", use_container_width=True):
            st.session_state.chart_mode = "table"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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

    # ── 3. AI Summary ────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">AI Summary</div>', unsafe_allow_html=True)
    if st.button("Summarize Reviews", use_container_width=False):
        reviews_text = "\n\n".join(
            f"[{row.get('Rating', '?')}★] {row.get('Review', '')}" for _, row in df.head(300).iterrows()
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
            "- Do NOT use rule-of-three constructions.\n"
            "- Write in plain, direct language. Short sentences. No filler.\n"
            "- Sound like a sharp analyst writing a Slack message to their team, not a blog post.\n"
            "- Use markdown formatting: **bold** for section headers, bullet points for lists."
        )
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nHere are the reviews:\n\n{reviews_text}"}]}],
                   "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048}}
        with st.spinner("Generating summary..."):
            try:
                resp = requests.post(url, json=payload, timeout=60); resp.raise_for_status()
                st.session_state.summary_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                st.error(f"Summary generation failed: {e}")

    if st.session_state.summary_text:
        html_summary = md_lib.markdown(st.session_state.summary_text) if HAS_MD else st.session_state.summary_text
        st.markdown(f'<div class="summary-card">{html_summary}</div>', unsafe_allow_html=True)

    # ── 4. Export ────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">Export</div>', unsafe_allow_html=True)
    fname_base = f"{meta.get('app_id', 'app')}_{meta.get('country', 'xx')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    dl1, dl2, dl_meta = st.columns([0.15, 0.15, 0.7])
    with dl1:
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv_data, f"{fname_base}.csv", "text/csv", use_container_width=True)
    with dl2:
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            display_df.to_excel(w, index=False, sheet_name="Reviews")
        st.download_button("Download XLSX", buf.getvalue(), f"{fname_base}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.xml", use_container_width=True)
    with dl_meta:
        st.markdown(f'<div class="file-meta"><b>{len(display_df):,}</b> rows  ·  <b>{len(display_df.columns)}</b> cols  ·  {len(csv_data)/1024:.0f} KB</div>', unsafe_allow_html=True)

    # ── 5. Reviews table ─────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">Reviews</div>', unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, height=480,
                 column_config={"Rating": st.column_config.NumberColumn(format="%d ★"),
                                "Review": st.column_config.TextColumn(width="large")})

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">★</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start Scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
