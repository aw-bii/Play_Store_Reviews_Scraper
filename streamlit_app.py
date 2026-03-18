"""
Google Play Store Reviews Scraper
Run:  streamlit run app.py
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

# ── Session state init ───────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.meta = {}
if "chart_mode" not in st.session_state:
    st.session_state.chart_mode = "chart"
if "summary_text" not in st.session_state:
    st.session_state.summary_text = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Theme tokens ─────────────────────────────────────────────
dark = st.session_state.dark_mode

t = {
    "bg":           "#0e0e0e" if dark else "#ffffff",
    "surface":      "#1a1a1a" if dark else "#fafafa",
    "surface_br":   "#2a2a2a" if dark else "#e5e5e5",
    "text":         "#e8e8e8" if dark else "#111111",
    "text_sec":     "#888888" if dark else "#888888",
    "text_muted":   "#666666" if dark else "#999999",
    "sidebar_bg":   "#111111" if dark else "#111111",
    "sidebar_text": "#f0f0f0" if dark else "#f0f0f0",
    "input_bg":     "rgba(255,255,255,0.08)" if dark else "rgba(255,255,255,0.08)",
    "input_br":     "rgba(255,255,255,0.15)" if dark else "rgba(255,255,255,0.15)",
    "accent":       "#ffffff" if dark else "#111111",
    "accent_inv":   "#111111" if dark else "#ffffff",
    "chart_color":  "#888888" if dark else "#111111",
    "card_shadow":  "none" if dark else "0 1px 3px rgba(0,0,0,0.04)",
    "summary_bg":   "#1a1a1a" if dark else "#f7f7f7",
    "summary_br":   "#2a2a2a" if dark else "#e8e8e8",
    "summary_text": "#d4d4d4" if dark else "#222222",
    "summary_h":    "#e8e8e8" if dark else "#111111",
    "metric_label": "#777777" if dark else "#888888",
    "metric_val":   "#e8e8e8" if dark else "#111111",
    "divider":      "#2a2a2a" if dark else "#eeeeee",
    "bar_label":    "#aaaaaa" if dark else "#555555",
}

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ── Base ─────────────────────────────────────────────── */
    .stApp {{
        background: {t['bg']} !important;
    }}
    .block-container {{
        padding: 2rem 3rem 2.5rem !important;
        max-width: 1200px;
    }}

    /* ── Global text override for dark mode ────────────────── */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {{
        color: {t['text']} !important;
    }}
    .stApp .stMarkdown p {{
        color: {t['text']} !important;
    }}

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: {t['sidebar_bg']} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {t['sidebar_text']} !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding: 2rem 1.5rem !important;
    }}
    [data-testid="stSidebar"] label {{
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.7;
        margin-bottom: 2px !important;
    }}
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {{
        background: {t['input_bg']} !important;
        border: 1px solid {t['input_br']} !important;
        color: #fff !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] .stTextInput input::placeholder {{
        color: rgba(255,255,255,0.35) !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.1) !important;
        margin: 1.2rem 0 !important;
    }}

    /* ── Sidebar primary button ────────────────────────────── */
    [data-testid="stSidebar"] .stButton > button {{
        background: #ffffff !important;
        color: #111111 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        transition: all 0.15s ease;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: #e0e0e0 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(255,255,255,0.15);
    }}

    /* ── Main area buttons ────────────────────────────────── */
    .stApp [data-testid="stMainBlockContainer"] .stButton > button {{
        background: {t['surface']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['surface_br']} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.82rem !important;
        transition: all 0.15s ease;
    }}
    .stApp [data-testid="stMainBlockContainer"] .stButton > button:hover {{
        background: {t['surface_br']} !important;
        transform: translateY(-1px);
    }}

    /* ── Download buttons ─────────────────────────────────── */
    .stDownloadButton > button {{
        background: {t['accent']} !important;
        color: {t['accent_inv']} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease;
    }}
    .stDownloadButton > button:hover {{
        opacity: 0.85;
        transform: translateY(-1px);
    }}

    /* ── Metric cards ─────────────────────────────────────── */
    div[data-testid="stMetric"] {{
        background: {t['surface']};
        border: 1px solid {t['surface_br']};
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: {t['card_shadow']};
    }}
    div[data-testid="stMetric"] label {{
        color: {t['metric_label']} !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {t['metric_val']} !important;
        font-weight: 700 !important;
    }}

    /* ── Header ───────────────────────────────────────────── */
    .app-header h1 {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {t['text']};
        font-size: 1.7rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .app-sub {{
        color: {t['text_muted']};
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }}

    /* ── Section headers ──────────────────────────────────── */
    .section-hdr {{
        font-weight: 700;
        font-size: 0.95rem;
        color: {t['text']};
        margin: 1.4rem 0 0.5rem;
    }}

    /* ── Dataframe ────────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border: 1px solid {t['surface_br']};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ── Divider ──────────────────────────────────────────── */
    .stApp hr {{
        border-color: {t['divider']} !important;
    }}

    /* ── Empty state ──────────────────────────────────────── */
    .empty-state {{
        text-align: center;
        padding: 6rem 2rem;
    }}
    .empty-state .icon {{
        font-size: 2.4rem;
        margin-bottom: 0.8rem;
        color: {t['text_muted']};
    }}
    .empty-state p {{
        font-size: 0.95rem;
        max-width: 360px;
        margin: 0 auto;
        line-height: 1.6;
        color: {t['text_muted']};
    }}

    /* ── Summary card ─────────────────────────────────────── */
    .summary-card {{
        background: {t['summary_bg']};
        border: 1px solid {t['summary_br']};
        border-radius: 10px;
        padding: 1.5rem 1.8rem;
        margin-top: 0.8rem;
        line-height: 1.75;
        font-size: 0.91rem;
        color: {t['summary_text']};
    }}
    .summary-card h1, .summary-card h2, .summary-card h3,
    .summary-card h4, .summary-card h5 {{
        color: {t['summary_h']} !important;
        margin: 1.1rem 0 0.3rem;
        font-size: 0.88rem;
        font-weight: 700;
    }}
    .summary-card h4:first-child {{ margin-top: 0; }}
    .summary-card ul {{ padding-left: 1.2rem; margin: 0.2rem 0; }}
    .summary-card li {{ margin-bottom: 0.2rem; color: {t['summary_text']}; }}
    .summary-card strong {{ color: {t['summary_h']}; }}

    /* ── Status widget ────────────────────────────────────── */
    [data-testid="stStatusWidget"] {{
        background: {t['surface']} !important;
        border: 1px solid {t['surface_br']} !important;
        border-radius: 10px !important;
    }}

    /* ── Checkbox and toggle styling ──────────────────────── */
    .stCheckbox label span {{
        color: {t['text']} !important;
    }}

    /* ── Theme toggle pill ────────────────────────────────── */
    .theme-toggle {{
        position: fixed;
        top: 14px;
        right: 20px;
        z-index: 9999;
    }}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
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

    # ── Theme toggle at bottom of sidebar ────────────────────
    st.divider()
    mode_label = "Switch to Light Mode" if dark else "Switch to Dark Mode"
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
            st.bar_chart(dist, color=t["chart_color"], height=220)
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

    dl1, dl2, _ = st.columns([0.15, 0.15, 0.7])
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
    st.markdown(f"""
    <div class="empty-state">
        <div class="icon">★</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start Scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
