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

# ── Theme tokens ─────────────────────────────────────────────
if dark:
    T_BG          = "#0e0e0e"
    T_SURFACE     = "#1a1a1a"
    T_BORDER      = "#2a2a2a"
    T_TEXT        = "#e0e0e0"
    T_TEXT_SEC    = "#aaaaaa"
    T_TEXT_MUTED  = "#777777"
    T_ACCENT      = "#ffffff"
    T_ACCENT_INV  = "#111111"
    T_CHART       = "#999999"
    T_INPUT_BG    = "#1e1e1e"
    T_INPUT_BR    = "#3a3a3a"
    T_INPUT_TEXT  = "#e0e0e0"
    T_LABEL       = "#bbbbbb"
    T_PLACEHOLDER = "#666666"
    T_HELP        = "#888888"
    T_METRIC_LBL  = "#999999"
    T_METRIC_VAL  = "#e0e0e0"
    T_SUCCESS_BG  = "#1a2e1a"
    T_SUCCESS_TX  = "#88cc88"
    T_WARNING_BG  = "#2e2a1a"
    T_WARNING_TX  = "#ccbb66"
    T_ERROR_BG    = "#2e1a1a"
    T_ERROR_TX    = "#cc6666"
    T_SUMMARY_BG  = "#161616"
    T_SUMMARY_BR  = "#2a2a2a"
    T_SUMMARY_TX  = "#cccccc"
    T_SUMMARY_H   = "#e0e0e0"
    T_PILL_BG     = "#333333"
    T_PILL_TX     = "#e0e0e0"
else:
    T_BG          = "#ffffff"
    T_SURFACE     = "#f8f8f8"
    T_BORDER      = "#e5e5e5"
    T_TEXT        = "#111111"
    T_TEXT_SEC    = "#555555"
    T_TEXT_MUTED  = "#999999"
    T_ACCENT      = "#111111"
    T_ACCENT_INV  = "#ffffff"
    T_CHART       = "#111111"
    T_INPUT_BG    = "#ffffff"
    T_INPUT_BR    = "#d0d0d0"
    T_INPUT_TEXT  = "#111111"
    T_LABEL       = "#333333"
    T_PLACEHOLDER = "#aaaaaa"
    T_HELP        = "#888888"
    T_METRIC_LBL  = "#888888"
    T_METRIC_VAL  = "#111111"
    T_SUCCESS_BG  = "#eaf7ea"
    T_SUCCESS_TX  = "#2e7d32"
    T_WARNING_BG  = "#fff8e1"
    T_WARNING_TX  = "#f57f17"
    T_ERROR_BG    = "#fdecea"
    T_ERROR_TX    = "#c62828"
    T_SUMMARY_BG  = "#f7f7f7"
    T_SUMMARY_BR  = "#e5e5e5"
    T_SUMMARY_TX  = "#222222"
    T_SUMMARY_H   = "#111111"
    T_PILL_BG     = "#e8e8e8"
    T_PILL_TX     = "#111111"

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ═══════════════════════════════════════════════════════
       BASE & BACKGROUND
       ═══════════════════════════════════════════════════════ */
    .stApp {{
        background: {T_BG} !important;
        color: {T_TEXT} !important;
    }}
    .block-container {{
        padding: 2rem 3rem 2.5rem !important;
        max-width: 1200px;
    }}

    /* ═══════════════════════════════════════════════════════
       GLOBAL TEXT — catch-all for main area
       ═══════════════════════════════════════════════════════ */
    .stApp p,
    .stApp span,
    .stApp li,
    .stApp td,
    .stApp th,
    .stApp label,
    .stApp .stMarkdown,
    .stApp .stMarkdown p,
    .stApp .stText,
    .stApp [data-testid="stText"],
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] p {{
        color: {T_TEXT} !important;
    }}

    /* ═══════════════════════════════════════════════════════
       MAIN AREA — labels, inputs, selects
       ═══════════════════════════════════════════════════════ */
    .stApp [data-testid="stMainBlockContainer"] label,
    .stApp [data-testid="stMainBlockContainer"] .stTextInput label,
    .stApp [data-testid="stMainBlockContainer"] .stNumberInput label,
    .stApp [data-testid="stMainBlockContainer"] .stSelectbox label,
    .stApp [data-testid="stMainBlockContainer"] .stMultiSelect label,
    .stApp [data-testid="stMainBlockContainer"] .stCheckbox label,
    .stApp [data-testid="stMainBlockContainer"] .stCheckbox label span,
    .stApp [data-testid="stMainBlockContainer"] .stRadio label {{
        color: {T_LABEL} !important;
    }}

    .stApp [data-testid="stMainBlockContainer"] .stTextInput input,
    .stApp [data-testid="stMainBlockContainer"] .stNumberInput input {{
        background: {T_INPUT_BG} !important;
        color: {T_INPUT_TEXT} !important;
        border: 1px solid {T_INPUT_BR} !important;
        border-radius: 8px !important;
    }}
    .stApp [data-testid="stMainBlockContainer"] .stTextInput input::placeholder {{
        color: {T_PLACEHOLDER} !important;
    }}

    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"],
    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div {{
        background: {T_INPUT_BG} !important;
        border-color: {T_INPUT_BR} !important;
        color: {T_INPUT_TEXT} !important;
    }}
    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] span,
    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="select"] div[class*="value"] {{
        color: {T_INPUT_TEXT} !important;
    }}

    /* Multiselect pills */
    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] {{
        background: {T_PILL_BG} !important;
    }}
    .stApp [data-testid="stMainBlockContainer"] [data-baseweb="tag"] span {{
        color: {T_PILL_TX} !important;
    }}

    /* Help text (? tooltips and captions) */
    .stApp [data-testid="stMainBlockContainer"] .stTooltipIcon,
    .stApp .stHelp,
    .stApp small {{
        color: {T_HELP} !important;
    }}

    /* ═══════════════════════════════════════════════════════
       SIDEBAR — always dark
       ═══════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {{
        background: #111111 !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding: 2rem 1.5rem !important;
    }}

    /* Sidebar: all text white */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] .stCheckbox label span {{
        color: #f0f0f0 !important;
    }}

    /* Sidebar: labels */
    [data-testid="stSidebar"] label {{
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.75;
        margin-bottom: 2px !important;
    }}

    /* Sidebar: inputs */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input {{
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stTextInput input::placeholder {{
        color: rgba(255,255,255,0.35) !important;
    }}
    /* Sidebar: number input buttons */
    [data-testid="stSidebar"] .stNumberInput button {{
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.18) !important;
        background: rgba(255,255,255,0.07) !important;
    }}

    /* Sidebar: selects */
    [data-testid="stSidebar"] [data-baseweb="select"],
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(255,255,255,0.18) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div[class*="value"],
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        color: #ffffff !important;
        fill: #ffffff !important;
    }}

    /* Sidebar: multiselect pills */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: rgba(255,255,255,0.15) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: #ffffff !important;
    }}

    /* Sidebar: help text */
    [data-testid="stSidebar"] .stTooltipIcon {{
        color: rgba(255,255,255,0.4) !important;
    }}

    /* Sidebar: dividers */
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.1) !important;
        margin: 1.2rem 0 !important;
    }}

    /* Sidebar: checkbox */
    [data-testid="stSidebar"] .stCheckbox label {{
        color: #f0f0f0 !important;
    }}

    /* ═══════════════════════════════════════════════════════
       SIDEBAR: PRIMARY BUTTON (always white-on-dark)
       ═══════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] .stButton > button {{
        background: #ffffff !important;
        color: #111111 !important;
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
        box-shadow: 0 4px 14px rgba(255,255,255,0.12);
    }}

    /* ═══════════════════════════════════════════════════════
       MAIN AREA BUTTONS
       ═══════════════════════════════════════════════════════ */
    .stApp [data-testid="stMainBlockContainer"] .stButton > button {{
        background: {T_SURFACE} !important;
        color: {T_TEXT} !important;
        border: 1px solid {T_BORDER} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.82rem !important;
        transition: all 0.15s ease;
    }}
    .stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
        background: {T_BORDER} !important;
        transform: translateY(-1px);
    }}

    /* Download buttons */
    .stDownloadButton > button {{
        background: {T_ACCENT} !important;
        color: {T_ACCENT_INV} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }}
    .stDownloadButton > button:hover {{
        opacity: 0.85;
        transform: translateY(-1px);
    }}

    /* ═══════════════════════════════════════════════════════
       METRIC CARDS
       ═══════════════════════════════════════════════════════ */
    div[data-testid="stMetric"] {{
        background: {T_SURFACE};
        border: 1px solid {T_BORDER};
        border-radius: 10px;
        padding: 16px 20px;
    }}
    div[data-testid="stMetric"] label {{
        color: {T_METRIC_LBL} !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {T_METRIC_VAL} !important;
        font-weight: 700 !important;
    }}

    /* ═══════════════════════════════════════════════════════
       STATUS / ALERTS
       ═══════════════════════════════════════════════════════ */
    [data-testid="stStatusWidget"] {{
        background: {T_SURFACE} !important;
        border-color: {T_BORDER} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stStatusWidget"] p,
    [data-testid="stStatusWidget"] span {{
        color: {T_TEXT} !important;
    }}
    .stAlert [data-testid="stNotification"] {{
        border-radius: 8px !important;
    }}

    /* ═══════════════════════════════════════════════════════
       DATAFRAME
       ═══════════════════════════════════════════════════════ */
    [data-testid="stDataFrame"] {{
        border: 1px solid {T_BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ═══════════════════════════════════════════════════════
       DIVIDERS
       ═══════════════════════════════════════════════════════ */
    .stApp hr {{
        border-color: {T_BORDER} !important;
    }}

    /* ═══════════════════════════════════════════════════════
       CUSTOM ELEMENTS
       ═══════════════════════════════════════════════════════ */
    .app-header h1 {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {T_TEXT};
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .app-sub {{
        color: {T_TEXT_MUTED};
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }}
    .section-hdr {{
        font-weight: 700;
        font-size: 0.95rem;
        color: {T_TEXT};
        margin: 1.4rem 0 0.5rem;
    }}
    .empty-state {{
        text-align: center;
        padding: 6rem 2rem;
    }}
    .empty-state .icon {{
        font-size: 2.4rem;
        margin-bottom: 0.8rem;
        color: {T_TEXT_MUTED};
    }}
    .empty-state p {{
        font-size: 0.95rem;
        max-width: 360px;
        margin: 0 auto;
        line-height: 1.6;
        color: {T_TEXT_MUTED};
    }}
    .empty-state b {{
        color: {T_TEXT_SEC};
    }}
    .file-meta {{
        margin-top: 1rem;
        font-size: 0.8rem;
        color: {T_TEXT_MUTED};
        line-height: 1.5;
    }}
    .file-meta b {{
        color: {T_TEXT_SEC};
    }}

    /* ── Summary card ─────────────────────────────────────── */
    .summary-card {{
        background: {T_SUMMARY_BG};
        border: 1px solid {T_SUMMARY_BR};
        border-radius: 10px;
        padding: 1.5rem 1.8rem;
        margin-top: 0.8rem;
        line-height: 1.75;
        font-size: 0.91rem;
        color: {T_SUMMARY_TX};
    }}
    .summary-card p {{
        color: {T_SUMMARY_TX} !important;
    }}
    .summary-card h1, .summary-card h2, .summary-card h3,
    .summary-card h4, .summary-card h5, .summary-card strong {{
        color: {T_SUMMARY_H} !important;
    }}
    .summary-card h4 {{
        margin: 1.1rem 0 0.3rem;
        font-size: 0.88rem;
        font-weight: 700;
    }}
    .summary-card h4:first-child {{ margin-top: 0; }}
    .summary-card ul {{ padding-left: 1.2rem; margin: 0.2rem 0; }}
    .summary-card li {{
        margin-bottom: 0.2rem;
        color: {T_SUMMARY_TX} !important;
    }}

    /* ═══════════════════════════════════════════════════════
       DROPDOWN MENUS (popover)
       ═══════════════════════════════════════════════════════ */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] ul {{
        background: {T_INPUT_BG} !important;
        border-color: {T_INPUT_BR} !important;
    }}
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li {{
        color: {T_INPUT_TEXT} !important;
        background: transparent !important;
    }}
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover {{
        background: {T_BORDER} !important;
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
            st.bar_chart(dist, color=T_CHART, height=220)
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
        st.markdown(
            f'<div class="summary-card">{st.session_state.summary_text}</div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">★</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start Scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
