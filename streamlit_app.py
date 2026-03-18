"""
Google Play Store Reviews Scraper
Bertelsmann Corporate Design
Run:  streamlit run play-store-scraper.py
Deps: pip install streamlit google-play-scraper pandas openpyxl requests markdown pycountry
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

try:
    import pycountry
    COUNTRIES = {c.name: c.alpha_2.lower() for c in sorted(pycountry.countries, key=lambda c: c.name)}
except ImportError:
    COUNTRIES = {
        "India": "in", "United States": "us", "United Kingdom": "gb", "Germany": "de",
        "France": "fr", "Canada": "ca", "Australia": "au", "Brazil": "br", "Japan": "jp",
        "South Korea": "kr", "Indonesia": "id", "Mexico": "mx", "Spain": "es", "Italy": "it",
        "Netherlands": "nl", "Turkey": "tr", "Saudi Arabia": "sa", "United Arab Emirates": "ae",
        "Singapore": "sg", "Malaysia": "my", "Thailand": "th", "Vietnam": "vn", "Philippines": "ph",
        "Nigeria": "ng", "South Africa": "za", "Kenya": "ke", "Egypt": "eg", "Pakistan": "pk",
        "Bangladesh": "bd", "Sri Lanka": "lk", "Nepal": "np",
    }

COUNTRY_NAMES = list(COUNTRIES.keys())
DEFAULT_COUNTRY_IDX = COUNTRY_NAMES.index("India") if "India" in COUNTRY_NAMES else 0

st.set_page_config(
    page_title="Play Store Reviews Scraper",
    page_icon="★",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ────────────────────────────────────────────
for key, default in [
    ("df", None), ("meta", {}),
    ("summary_text", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════
# BERTELSMANN DESIGN TOKENS
# ══════════════════════════════════════════════════════════════

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

BG            = "#ffffff"
SURFACE       = "#f5f6f8"
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
CARD_BG       = "#f5f6f8"
CARD_BR       = "#e8ecf0"
CARD_LABEL    = BE_GRAY_5
CARD_VALUE    = BE_BLUE
SUMMARY_BG    = "#f5f6f8"
SUMMARY_BR    = "#e8ecf0"
SUMMARY_TX    = BE_GRAY
SUMMARY_H     = BE_BLUE
SB_BG         = BE_BLUE


# ══════════════════════════════════════════════════════════════
# STYLESHEET
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>

/* === FONTS — Arial (Bertelsmann screen) === */
*, *::before, *::after {{
    font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif !important;
}}

/* === PAGE === */
.stApp {{ background: {BG} !important; }}
.block-container {{ padding: 2.5rem 3.5rem 3rem !important; max-width: 1120px; }}

/* === FIXED SIDEBAR === */
[data-testid="stSidebar"] {{
    background: {SB_BG} !important;
    min-width: 320px !important; max-width: 320px !important;
    transform: none !important; transition: none !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding: 2.2rem 1.6rem !important; }}

/* Hide ALL collapse controls */
button[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNav"],
.stApp button[kind="headerNoPadding"],
.stApp [data-testid="stHeader"] button {{
    display: none !important; visibility: hidden !important;
    width: 0 !important; height: 0 !important;
    overflow: hidden !important; position: absolute !important;
    pointer-events: none !important;
}}
/* Also hide the top-left hamburger on mobile */
[data-testid="stHeader"] {{
    display: none !important;
}}

/* === GLOBAL TEXT === */
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

/* === LABELS — no uppercase === */
.stApp [data-testid="stMainBlockContainer"] label,
.stApp [data-testid="stMainBlockContainer"] label p,
.stApp [data-testid="stMainBlockContainer"] label span,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"],
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] span,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label span,
.stApp [data-testid="stMainBlockContainer"] .stCheckbox label p {{
    color: {TEXT_2} !important;
    text-transform: none !important;
}}

/* === INPUTS (main) === */
.stApp [data-testid="stMainBlockContainer"] .stTextInput input,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input,
.stApp [data-testid="stMainBlockContainer"] .stTextArea textarea {{
    background: {INPUT_BG} !important; color: {INPUT_TX} !important;
    border: 1px solid {INPUT_BR} !important; border-radius: 4px !important;
    padding: 0.5rem 0.75rem !important; font-size: 0.88rem !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input:focus,
.stApp [data-testid="stMainBlockContainer"] .stNumberInput input:focus {{
    border-color: {INPUT_FOCUS} !important; box-shadow: 0 0 0 2px {INPUT_FOCUS}33 !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stTextInput input::placeholder {{ color: {INPUT_PH} !important; }}
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button {{
    color: {TEXT_2} !important; border-color: {INPUT_BR} !important; background: {INPUT_BG} !important;
}}

/* === SELECT (main) === */
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
    background: {INPUT_BG} !important; border-color: {INPUT_BR} !important; border-radius: 4px !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] span,
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="singleValue"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] [class*="placeholder"],
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] input {{
    color: {INPUT_TX} !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg {{ fill: {TEXT_3} !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] {{
    background: {TAG_BG} !important; border: none !important; border-radius: 3px !important;
}}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] span {{ color: {TAG_TX} !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg {{ fill: {TAG_TX} !important; }}

/* === DROPDOWN POPOVER === */
[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="menu"], [data-baseweb="menu"] ul,
[data-baseweb="list"], [data-baseweb="list"] ul {{
    background: {DROP_BG} !important; border-color: {INPUT_BR} !important; border-radius: 4px !important;
}}
[data-baseweb="popover"] li, [data-baseweb="menu"] li, [data-baseweb="list"] li {{
    color: {DROP_TX} !important; background: transparent !important; padding: 0.45rem 0.75rem !important;
}}
[data-baseweb="popover"] li:hover, [data-baseweb="menu"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"], [data-baseweb="menu"] li[aria-selected="true"] {{
    background: {DROP_HOVER} !important;
}}
[data-baseweb="popover"] li span, [data-baseweb="menu"] li span {{ color: {DROP_TX} !important; }}

/* === TOOLTIPS === */
.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon,
.stApp [data-testid="stMainBlockContainer"] .stTooltipIcon svg,
.stApp small {{ color: {TEXT_3} !important; fill: {TEXT_3} !important; }}

/* === METRIC CARDS === */
div[data-testid="stMetric"] {{
    background: {CARD_BG}; border: 1px solid {CARD_BR}; border-radius: 4px; padding: 18px 22px;
}}
div[data-testid="stMetric"]:hover {{ box-shadow: 0 2px 12px rgba(0,45,100,0.05); }}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] label p {{
    color: {CARD_LABEL} !important; font-size: 0.72rem !important;
    letter-spacing: 0.04em; font-weight: 600 !important;
    text-transform: none !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {CARD_VALUE} !important; font-weight: 700 !important; font-size: 1.5rem !important;
}}

/* === SIDEBAR TEXT & INPUTS === */
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
    color: #ffffff !important;
}}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] label p {{
    font-weight: 600 !important; font-size: 0.75rem !important;
    letter-spacing: 0.04em;
    color: {BE_BLUE_2} !important;
    text-transform: none !important;
}}

/* Sidebar inputs — white text on semi-transparent bg */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {{
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    color: #ffffff !important;
    border-radius: 4px !important;
    padding: 0.5rem 0.75rem !important; font-size: 0.88rem !important;
    caret-color: #ffffff !important;
}}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {{
    border-color: {BE_BLUE_2} !important;
    box-shadow: 0 0 0 2px rgba(175,190,210,0.25) !important;
}}
[data-testid="stSidebar"] .stTextInput input::placeholder {{
    color: rgba(175,190,210,0.6) !important;
}}
[data-testid="stSidebar"] .stNumberInput button {{
    color: #ffffff !important; border-color: rgba(255,255,255,0.22) !important;
    background: rgba(255,255,255,0.12) !important; border-radius: 3px !important;
}}

/* Sidebar selects */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.22) !important;
    border-radius: 4px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] [class*="singleValue"],
[data-testid="stSidebar"] [data-baseweb="select"] [class*="placeholder"],
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    color: #ffffff !important; fill: #ffffff !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: rgba(255,255,255,0.15) !important; border: none !important; border-radius: 3px !important;
}}
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] svg {{ color: #fff !important; fill: #fff !important; }}
[data-testid="stSidebar"] .stTooltipIcon,
[data-testid="stSidebar"] .stTooltipIcon svg {{ color: rgba(255,255,255,0.35) !important; fill: rgba(255,255,255,0.35) !important; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.12) !important; margin: 1.4rem 0 !important; }}

/* Sidebar checkbox alignment fix */
[data-testid="stSidebar"] .stCheckbox {{
    display: flex !important; align-items: center !important;
}}
[data-testid="stSidebar"] .stCheckbox > label {{
    display: flex !important; align-items: center !important; gap: 0.5rem !important;
}}

/* === SIDEBAR BUTTON — Be Red CTA === */
[data-testid="stSidebar"] .stButton > button {{
    background: {BE_RED} !important; color: #ffffff !important;
    border: none !important; border-radius: 980px !important;
    padding: 0.6rem 1.4rem !important; font-weight: 700 !important;
    font-size: 0.85rem !important; letter-spacing: 0.02em;
    text-transform: none !important;
    transition: all 0.15s ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {BE_RED_2} !important; box-shadow: 0 2px 10px rgba(230,0,40,0.3);
}}

/* === MAIN BUTTONS — generic secondary === */
.stApp [data-testid="stMainBlockContainer"] .stButton > button {{
    background: {SURFACE} !important; color: {TEXT_1} !important;
    border: 1px solid {BE_GRAY_3} !important; border-radius: 4px !important;
    font-weight: 600 !important; padding: 0.4rem 1rem !important;
    font-size: 0.82rem !important; text-transform: none !important;
}}
.stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
    background: {BE_GRAY_2} !important;
}}

/* === DOWNLOAD + SUMMARY BUTTONS — Be Blue pill === */
.stDownloadButton > button,
.stDownloadButton button[kind="primary"],
.stDownloadButton button[kind="secondary"],
.stDownloadButton button[data-testid="stBaseButton-primary"],
.stDownloadButton button[data-testid="stBaseButton-secondary"],
.blue-pill .stButton > button {{
    background: {BE_BLUE} !important; color: #ffffff !important;
    border: none !important; border-radius: 980px !important;
    font-weight: 600 !important; padding: 0.5rem 1.2rem !important;
    font-size: 0.85rem !important; text-transform: none !important;
    transition: all 0.15s ease;
}}
.stDownloadButton > button:hover,
.stDownloadButton button[kind="primary"]:hover,
.stDownloadButton button[kind="secondary"]:hover,
.blue-pill .stButton > button:hover {{
    background: {BE_BLUE_5} !important;
    box-shadow: 0 2px 10px rgba(0,45,100,0.2);
}}

/* === STATUS — fixed, no collapse === */
[data-testid="stStatusWidget"] {{
    background: {SURFACE} !important; border: 1px solid {BORDER} !important;
    border-radius: 4px !important; transition: none !important;
}}
[data-testid="stStatusWidget"] * {{ transition: none !important; animation: none !important; }}
[data-testid="stStatusWidget"] p, [data-testid="stStatusWidget"] span,
[data-testid="stStatusWidget"] div {{ color: {TEXT_1} !important; }}
[data-testid="stStatusWidget"] summary {{ pointer-events: none !important; cursor: default !important; }}
[data-testid="stStatusWidget"] summary svg {{ display: none !important; }}
.stSpinner > div > span {{ color: {TEXT_2} !important; }}

/* === DATAFRAME === */
[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 4px; overflow: hidden; }}

/* === DIVIDERS === */
.stApp hr {{ border-color: {BORDER_SUB} !important; }}

/* === SVG ICONS === */
.stApp [data-testid="stMainBlockContainer"] svg {{ fill: {TEXT_2} !important; color: {TEXT_2} !important; }}
.stApp [data-testid="stMainBlockContainer"] svg path {{ fill: {TEXT_2} !important; }}
[data-testid="stSidebar"] svg, [data-testid="stSidebar"] svg path {{ fill: #ffffff !important; color: #ffffff !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] svg path {{ fill: {TEXT_3} !important; }}
[data-testid="stSidebar"] [data-baseweb="select"] svg path {{ fill: #ffffff !important; }}
.stApp [data-testid="stMainBlockContainer"] .stNumberInput button svg path {{ fill: {TEXT_2} !important; }}
[data-testid="stSidebar"] .stNumberInput button svg path {{ fill: #ffffff !important; }}
.stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] svg path {{ fill: {TAG_TX} !important; }}
[data-testid="stStatusWidget"] svg path {{ fill: {TEXT_2} !important; }}

/* Blue pill button icon override */
.blue-pill .stButton > button svg, .blue-pill .stButton > button svg path {{
    fill: #ffffff !important; color: #ffffff !important;
}}
.stDownloadButton > button svg, .stDownloadButton > button svg path {{
    fill: #ffffff !important; color: #ffffff !important;
}}

/* === CUSTOM HTML === */
.app-header h1 {{
    color: {BE_BLUE}; font-size: 2rem; font-weight: 700; margin: 0;
    letter-spacing: -0.02em; line-height: 1.15;
}}
.app-sub {{
    color: {TEXT_3}; font-size: 0.92rem; margin-top: 0.4rem; margin-bottom: 2rem;
}}
.section-hdr {{
    font-weight: 700; font-size: 1.05rem; color: {BE_BLUE};
    margin: 2rem 0 0.7rem; letter-spacing: -0.01em;
}}
.empty-state {{ text-align: center; padding: 8rem 2rem; }}
.empty-state .icon {{ font-size: 2.4rem; margin-bottom: 1rem; color: {TEXT_3}; }}
.empty-state p {{ font-size: 0.95rem; max-width: 360px; margin: 0 auto; line-height: 1.7; color: {TEXT_3}; }}
.empty-state b {{ color: {TEXT_2}; }}
.file-meta {{ margin-top: 0.8rem; font-size: 0.78rem; color: {TEXT_3}; font-weight: 500; }}
.file-meta b {{ color: {TEXT_2}; font-weight: 600; }}

/* Summary card */
.summary-card {{
    background: {SUMMARY_BG}; border: 1px solid {SUMMARY_BR}; border-radius: 4px;
    padding: 1.6rem 1.8rem; margin-top: 0.8rem; line-height: 1.75; font-size: 0.9rem; color: {SUMMARY_TX};
}}
.summary-card p {{ color: {SUMMARY_TX} !important; }}
.summary-card li {{ color: {SUMMARY_TX} !important; margin-bottom: 0.2rem; }}
.summary-card ul, .summary-card ol {{ padding-left: 1.2rem; margin: 0.3rem 0 0.6rem; }}
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
    <h1>Play Store Reviews Scraper</h1>
</div>
<p class="app-sub">Pull, preview, and export Google Play reviews for any app.</p>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### Input")
    st.divider()

    app_id = st.text_input(
        "App id", placeholder="com.example.app",
        help="From the Play Store URL: play.google.com/store/apps/details?id=com.example.app",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        country_name = st.selectbox("Country", options=COUNTRY_NAMES, index=DEFAULT_COUNTRY_IDX)
    with col_b:
        count = st.number_input("Reviews", min_value=1, max_value=10000, value=200, step=50)

    country_code = COUNTRIES.get(country_name, "in")

    sort_order = st.selectbox("Sort by", ["Newest", "Most Relevant"])
    filter_score = st.multiselect("Star filter", options=[1, 2, 3, 4, 5], default=[], help="Leave empty for all ratings")
    include_version = st.checkbox("Include app version column", value=False)

    st.divider()
    scrape = st.button("Start scraping", use_container_width=True)


# ── Scraping ─────────────────────────────────────────────────
SORT_MAP = {"Most Relevant": Sort.MOST_RELEVANT, "Newest": Sort.NEWEST}

if scrape:
    if not app_id.strip():
        st.error("Enter an App ID to continue."); st.stop()
    st.session_state.summary_text = None
    sort_val = SORT_MAP[sort_order]
    filter_val = filter_score if filter_score else None

    with st.status(f"Scraping {app_id}  ·  {country_name}  ·  {count} reviews", expanded=True) as status:
        try:
            all_reviews, batch_size, token = [], min(count, 200), None
            while len(all_reviews) < count:
                fetch_count = min(batch_size, count - len(all_reviews))
                st.write(f"Fetching batch... ({len(all_reviews)}/{count})")
                result, token = reviews(
                    app_id, lang="en", country=country_code, sort=sort_val,
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
        st.warning("No reviews found. Check the App ID and country."); st.stop()

    df = pd.DataFrame(all_reviews)
    keep = [c for c in ["userName", "score", "content", "at", "reviewCreatedVersion"] if c in df.columns]
    df = df[keep]
    df.rename(columns={"userName": "User", "score": "Rating", "content": "Review", "at": "Date", "reviewCreatedVersion": "App Version"}, inplace=True)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M")
    if filter_val and len(filter_val) > 1:
        df = df[df["Rating"].isin(filter_val)]
    st.session_state.df = df
    st.session_state.meta = {"app_id": app_id, "country": country_code, "country_name": country_name}


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

    # ── 1. Metrics (with NPS instead of 1-star count) ────────
    total = len(df)
    avg = df["Rating"].mean() if "Rating" in df.columns else 0
    five_star = int((df["Rating"] == 5).sum()) if "Rating" in df.columns else 0

    # NPS: promoters = 5★, detractors = 1–3★
    if "Rating" in df.columns and total > 0:
        promoters = (df["Rating"] == 5).sum()
        detractors = (df["Rating"] <= 3).sum()
        nps = round(((promoters - detractors) / total) * 100)
    else:
        nps = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total reviews", f"{total:,}")
    m2.metric("Avg rating", f"{avg:.2f} ★")
    m3.metric("5-star", f"{five_star:,}")
    m4.metric("NPS", f"{nps:+d}", help="Net Promoter Score: Promoters (5★) minus Detractors (1–3★), as a percentage of total reviews")

    # ── 2. AI Summary ────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">AI summary</div>', unsafe_allow_html=True)

    st.markdown('<div class="blue-pill">', unsafe_allow_html=True)
    summarize_clicked = st.button("Summarize reviews", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    if summarize_clicked:
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

    # ── 3. Export ────────────────────────────────────────────
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

    # ── 4. Reviews table ─────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">Reviews</div>', unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True, height=480,
                 column_config={"Rating": st.column_config.NumberColumn(format="%d ★"),
                                "Review": st.column_config.TextColumn(width="large")})

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">★</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
