"""
Google Play Store Reviews Scraper
Run:  streamlit run play-store-scraper.py
Deps: pip install streamlit google-play-scraper pandas openpyxl requests
"""

import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime
import time
import requests
import json
from io import BytesIO
import markdown as md_lib

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Play Store Reviews Scraper",
    page_icon="★",
    layout="wide",
)

# ── Session state ────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.meta = {}
if "chart_mode" not in st.session_state:
    st.session_state.chart_mode = "chart"
if "summary_text" not in st.session_state:
    st.session_state.summary_text = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.session_state.dark_mode

# ══════════════════════════════════════════════════════════════
# DESIGN TOKENS
# A single source of truth for every color in the app.
# Everything references these — nothing is hardcoded in CSS.
# ══════════════════════════════════════════════════════════════

if dark:
    # ── Dark palette ─────────────────────────────────────────
    PAGE_BG         = "#0e0e0e"
    SURFACE         = "#161616"
    SURFACE_HOVER   = "#1e1e1e"
    BORDER          = "#282828"
    BORDER_FOCUS    = "#444444"

    TEXT_PRIMARY    = "#e2e2e2"
    TEXT_SECONDARY  = "#aaaaaa"
    TEXT_MUTED      = "#737373"

    INPUT_BG        = "#1a1a1a"
    INPUT_BORDER    = "#333333"
    INPUT_TEXT      = "#e2e2e2"
    INPUT_PLACEHOLDER = "#5a5a5a"

    LABEL_COLOR     = "#c0c0c0"

    ACCENT          = "#ffffff"
    ACCENT_HOVER    = "#dddddd"
    ACCENT_INV      = "#0e0e0e"

    CHART_COLOR     = "#808080"

    METRIC_LABEL    = "#909090"
    METRIC_VALUE    = "#e2e2e2"

    SUMMARY_BG      = "#141414"
    SUMMARY_BORDER  = "#282828"
    SUMMARY_TEXT    = "#cccccc"
    SUMMARY_HEADING = "#e2e2e2"

    TAG_BG          = "#2a2a2a"
    TAG_TEXT         = "#d0d0d0"

    DROPDOWN_BG     = "#1a1a1a"
    DROPDOWN_HOVER  = "#262626"
    DROPDOWN_TEXT   = "#e2e2e2"

    # Sidebar (always dark)
    SB_BG           = "#0a0a0a"
    SB_TEXT         = "#e8e8e8"
    SB_LABEL        = "#aaaaaa"
    SB_INPUT_BG     = "#161616"
    SB_INPUT_BORDER = "#2a2a2a"
    SB_INPUT_TEXT   = "#e8e8e8"
    SB_PLACEHOLDER  = "#555555"
    SB_DIVIDER      = "#222222"
else:
    # ── Light palette ────────────────────────────────────────
    PAGE_BG         = "#ffffff"
    SURFACE         = "#f7f7f7"
    SURFACE_HOVER   = "#eeeeee"
    BORDER          = "#e2e2e2"
    BORDER_FOCUS    = "#bbbbbb"

    TEXT_PRIMARY    = "#111111"
    TEXT_SECONDARY  = "#555555"
    TEXT_MUTED      = "#999999"

    INPUT_BG        = "#ffffff"
    INPUT_BORDER    = "#cccccc"
    INPUT_TEXT      = "#111111"
    INPUT_PLACEHOLDER = "#aaaaaa"

    LABEL_COLOR     = "#333333"

    ACCENT          = "#111111"
    ACCENT_HOVER    = "#333333"
    ACCENT_INV      = "#ffffff"

    CHART_COLOR     = "#111111"

    METRIC_LABEL    = "#888888"
    METRIC_VALUE    = "#111111"

    SUMMARY_BG      = "#f7f7f7"
    SUMMARY_BORDER  = "#e2e2e2"
    SUMMARY_TEXT    = "#222222"
    SUMMARY_HEADING = "#111111"

    TAG_BG          = "#e8e8e8"
    TAG_TEXT         = "#111111"

    DROPDOWN_BG     = "#ffffff"
    DROPDOWN_HOVER  = "#f0f0f0"
    DROPDOWN_TEXT   = "#111111"

    # Sidebar (always dark)
    SB_BG           = "#0a0a0a"
    SB_TEXT         = "#e8e8e8"
    SB_LABEL        = "#aaaaaa"
    SB_INPUT_BG     = "#161616"
    SB_INPUT_BORDER = "#2a2a2a"
    SB_INPUT_TEXT   = "#e8e8e8"
    SB_PLACEHOLDER  = "#555555"
    SB_DIVIDER      = "#222222"


# ══════════════════════════════════════════════════════════════
# STYLESHEET
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>

/* ─────────────────────────────────────────────────────────────
   1. PAGE BACKGROUND & LAYOUT
   ───────────────────────────────────────────────────────────── */

.stApp {{
    background: {PAGE_BG} !important;
}}
.block-container {{
    padding: 2rem 3rem 2.5rem !important;
    max-width: 1200px;
}}


/* ─────────────────────────────────────────────────────────────
   2. GLOBAL TEXT — every text element in main area
   ───────────────────────────────────────────────────────────── */

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
    color: {TEXT_PRIMARY} !important;
}}


/* ─────────────────────────────────────────────────────────────
   3. MAIN AREA — LABELS (the #1 visibility issue)
   Targets every label variant Streamlit generates.
   ───────────────────────────────────────────────────────────── */

.stApp [data-testid="stMainBlockContainer"] label,
.stApp [data-testid="stMainBlockContainer"] label p,
.stApp [data-testid="stMainBlockContainer"] label span,
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
.stApp [data-testid="stMainBlockContainer"] .stRadio label p,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"],
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] span {{
    color: {LABEL_COLOR} !important;
}}


/* ─────────────────────────────────────────────────────────────
   4. MAIN AREA — TEXT INPUTS & NUMBER INPUTS
   ───────────────────────────────────────────────────────────── */

.stApp [data-testid="stMainBlockContainer"] .stTextInput input,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea {{
    background: {INPUT_BG} !important;
    color: {INPUT_TEXT} !important;
    border: 1px solid {INPUT_BORDER} !important;
    border-radius: 8px !important;
    caret-color: {INPUT_TEXT} !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea:focus {{
    border-color: {BORDER_FOCUS} !important;
    box-shadow: 0 0 0 1px {BORDER_FOCUS} !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input::placeholder,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea::placeholder {{
    color: {INPUT_PLACEHOLDER} !important;
}}

/* Number input step buttons */
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button {{
    color: {TEXT_PRIMARY} !important;
    border-color: {INPUT_BORDER} !important;
    background: {INPUT_BG} !important;
}}


/* ─────────────────────────────────────────────────────────────
   5. MAIN AREA — SELECT / DROPDOWN
   ───────────────────────────────────────────────────────────── */

.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
    background: {INPUT_BG} !important;
    border-color: {INPUT_BORDER} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] span,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="singleValue"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="placeholder"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] input {{
    color: {INPUT_TEXT} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg {{
    fill: {TEXT_SECONDARY} !important;
}}

/* Multiselect tags / pills */
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] {{
    background: {TAG_BG} !important;
    border: none !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] span {{
    color: {TAG_TEXT} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg {{
    fill: {TAG_TEXT} !important;
}}


/* ─────────────────────────────────────────────────────────────
   6. DROPDOWN POPOVER / MENU (appears on click)
   ───────────────────────────────────────────────────────────── */

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[data-baseweb="list"],
[data-baseweb="list"] ul {{
    background: {DROPDOWN_BG} !important;
    background-color: {DROPDOWN_BG} !important;
    border-color: {INPUT_BORDER} !important;
}}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[data-baseweb="list"] li {{
    color: {DROPDOWN_TEXT} !important;
    background: transparent !important;
}}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[data-baseweb="list"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"],
[data-baseweb="menu"] li[aria-selected="true"],
[data-baseweb="list"] li[aria-selected="true"] {{
    background: {DROPDOWN_HOVER} !important;
}}
/* Dropdown option text */
[data-baseweb="popover"] li span,
[data-baseweb="menu"] li span,
[data-baseweb="list"] li span {{
    color: {DROPDOWN_TEXT} !important;
}}


/* ─────────────────────────────────────────────────────────────
   7. HELP TEXT & TOOLTIPS
   ───────────────────────────────────────────────────────────── */

.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon,
.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon svg,
.stApp [data-testid="stMainBlockContainer"] [data-testid="tooltipHoverTarget"],
.stApp small {{
    color: {TEXT_MUTED} !important;
    fill: {TEXT_MUTED} !important;
}}


/* ─────────────────────────────────────────────────────────────
   8. METRIC CARDS
   ───────────────────────────────────────────────────────────── */

div[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px 20px;
}}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label p {{
    color: {METRIC_LABEL} !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600 !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {METRIC_VALUE} !important;
    font-weight: 700 !important;
}}


/* ─────────────────────────────────────────────────────────────
   9. SIDEBAR (always dark regardless of mode)
   ───────────────────────────────────────────────────────────── */

[data-testid="stSidebar"] {{
    background: {SB_BG} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 2rem 1.5rem !important;
}}

/* Sidebar: all text */
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
    color: {SB_TEXT} !important;
}}

/* Sidebar: labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p {{
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {SB_LABEL} !important;
    margin-bottom: 2px !important;
}}

/* Sidebar: text inputs */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {{
    background: {SB_INPUT_BG} !important;
    border: 1px solid {SB_INPUT_BORDER} !important;
    color: {SB_INPUT_TEXT} !important;
    border-radius: 8px !important;
    caret-color: {SB_INPUT_TEXT} !important;
}}
[data-testid="stSidebar"] .stTextInput input::placeholder {{
    color: {SB_PLACEHOLDER} !important;
}}

/* Sidebar: number input buttons */
[data-testid="stSidebar"] .stNumberInput button {{
    color: {SB_TEXT} !important;
    border-color: {SB_INPUT_BORDER} !important;
    background: {SB_INPUT_BG} !important;
}}

/* Sidebar: selects */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: {SB_INPUT_BG} !important;
    border-color: {SB_INPUT_BORDER} !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] [class*="singleValue"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"],
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    color: {SB_INPUT_TEXT} !important;
    fill: {SB_INPUT_TEXT} !important;
}}

/* Sidebar: multiselect pills */
[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: rgba(255,255,255,0.12) !important;
    border: none !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
    color: #ffffff !important;
    fill: #ffffff !important;
}}

/* Sidebar: tooltips */
[data-testid="stSidebar"] .stTooltipIcon,
[data-testid="stSidebar"] .stTooltipIcon svg {{
    color: rgba(255,255,255,0.35) !important;
    fill: rgba(255,255,255,0.35) !important;
}}

/* Sidebar: dividers */
[data-testid="stSidebar"] hr {{
    border-color: {SB_DIVIDER} !important;
    margin: 1.2rem 0 !important;
}}

/* Sidebar: checkbox */
[data-testid="stSidebar"] .stCheckbox [data-testid="stCheckbox"] {{
    color: {SB_TEXT} !important;
}}


/* ─────────────────────────────────────────────────────────────
   10. SIDEBAR BUTTONS
   ───────────────────────────────────────────────────────────── */

[data-testid="stSidebar"] .stButton > button {{
    background: #ffffff !important;
    color: #0e0e0e !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: #e0e0e0 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(255,255,255,0.1);
}}


/* ─────────────────────────────────────────────────────────────
   11. MAIN AREA BUTTONS
   ───────────────────────────────────────────────────────────── */

.stApp [data-testid="stMainBlockContainer"] .stButton > button {{
    background: {SURFACE} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease;
}}
.stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background: {SURFACE_HOVER} !important;
    border-color: {BORDER_FOCUS} !important;
    transform: translateY(-1px);
}}

/* Download buttons */
.stDownloadButton > button {{
    background: {ACCENT} !important;
    color: {ACCENT_INV} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease;
}}
.stDownloadButton > button:hover {{
    background: {ACCENT_HOVER} !important;
    transform: translateY(-1px);
}}


/* ─────────────────────────────────────────────────────────────
   12. STATUS WIDGET, SPINNER, ALERTS
   ───────────────────────────────────────────────────────────── */

[data-testid="stStatusWidget"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}
[data-testid="stStatusWidget"] p,
[data-testid="stStatusWidget"] span,
[data-testid="stStatusWidget"] div {{
    color: {TEXT_PRIMARY} !important;
}}
.stSpinner > div > span {{
    color: {TEXT_SECONDARY} !important;
}}


/* ─────────────────────────────────────────────────────────────
   13. DATAFRAME & TABLES
   ───────────────────────────────────────────────────────────── */

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    overflow: hidden;
}}


/* ─────────────────────────────────────────────────────────────
   14. DIVIDERS
   ───────────────────────────────────────────────────────────── */

.stApp hr {{
    border-color: {BORDER} !important;
}}


/* ─────────────────────────────────────────────────────────────
   15. CUSTOM HTML ELEMENTS
   ───────────────────────────────────────────────────────────── */

.app-header h1 {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: {TEXT_PRIMARY};
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
}}
.app-sub {{
    color: {TEXT_MUTED};
    font-size: 0.88rem;
    margin-bottom: 1rem;
}}
.section-hdr {{
    font-weight: 700;
    font-size: 0.95rem;
    color: {TEXT_PRIMARY};
    margin: 1.4rem 0 0.5rem;
}}
.empty-state {{
    text-align: center;
    padding: 6rem 2rem;
}}
.empty-state .icon {{
    font-size: 2.4rem;
    margin-bottom: 0.8rem;
    color: {TEXT_MUTED};
}}
.empty-state p {{
    font-size: 0.95rem;
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.6;
    color: {TEXT_MUTED};
}}
.empty-state b {{
    color: {TEXT_SECONDARY};
}}
.file-meta {{
    margin-top: 1rem;
    font-size: 0.8rem;
    color: {TEXT_MUTED};
    line-height: 1.5;
}}
.file-meta b {{
    color: {TEXT_SECONDARY};
}}

/* Summary card */
.summary-card {{
    background: {SUMMARY_BG};
    border: 1px solid {SUMMARY_BORDER};
    border-radius: 10px;
    padding: 1.5rem 1.8rem;
    margin-top: 0.8rem;
    line-height: 1.75;
    font-size: 0.91rem;
    color: {SUMMARY_TEXT};
}}
.summary-card p {{ color: {SUMMARY_TEXT} !important; }}
.summary-card li {{ color: {SUMMARY_TEXT} !important; margin-bottom: 0.2rem; }}
.summary-card ul {{ padding-left: 1.2rem; margin: 0.3rem 0; }}
.summary-card h1, .summary-card h2, .summary-card h3,
.summary-card h4, .summary-card h5, .summary-card strong {{
    color: {SUMMARY_HEADING} !important;
}}
.summary-card h4 {{
    margin: 1.1rem 0 0.3rem;
    font-size: 0.88rem;
    font-weight: 700;
}}
.summary-card h4:first-child {{ margin-top: 0; }}


/* ─────────────────────────────────────────────────────────────
   16. EXPANDER
   ───────────────────────────────────────────────────────────── */

[data-testid="stExpander"] {{
    border-color: {BORDER} !important;
    background: {SURFACE} !important;
    border-radius: 10px !important;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {{
    color: {TEXT_PRIMARY} !important;
}}
[data-testid="stExpander"] svg {{
    fill: {TEXT_SECONDARY} !important;
}}

</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>Play Store Reviews Scraper</h1>
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
            st.bar_chart(dist, color=CHART_COLOR, height=220)
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
        # Convert markdown to HTML for proper rendering
        try:
            html_summary = md_lib.markdown(st.session_state.summary_text)
        except Exception:
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
