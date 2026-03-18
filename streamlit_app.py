"""
Google Play Store Reviews Scraper — BII Internal Tool
Run:  streamlit run app.py
Deps: pip install streamlit google-play-scraper pandas
"""

import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="BII · Play Store Scraper",
    page_icon="📱",
    layout="wide",
)

# ── Full custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
    /* ── Reset & base ─────────────────────────────────────── */
    .block-container {
        padding: 1.5rem 2.5rem 2rem !important;
        max-width: 1200px;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #002D64 0%, #001a3d 100%);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] label {
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.85;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #fff !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255,255,255,0.45) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    [data-testid="stSidebar"] .stButton > button {
        background: #E60028 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.02em;
        transition: all 0.2s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #c40022 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(230,0,40,0.35);
    }
    .stDownloadButton > button {
        background: #002D64 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s;
    }
    .stDownloadButton > button:hover {
        background: #001a3d !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,45,100,0.3);
    }

    /* ── Metric cards ─────────────────────────────────────── */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e8ecf2;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,45,100,0.06);
    }
    div[data-testid="stMetric"] label {
        color: #6b7a90 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #002D64 !important;
        font-weight: 700 !important;
    }

    /* ── Header area ──────────────────────────────────────── */
    .hero-bar {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.3rem;
    }
    .hero-bar img { height: 32px; }
    .hero-bar h1 {
        font-family: Arial, sans-serif;
        color: #002D64;
        font-size: 1.6rem;
        margin: 0;
        font-weight: 700;
    }
    .hero-sub {
        color: #6b7a90;
        font-size: 0.92rem;
        margin-bottom: 1.2rem;
    }

    /* ── Dataframe ────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #e8ecf2;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Bar chart recolor ────────────────────────────────── */
    .stBarChart { margin-top: -0.5rem; }

    /* ── Empty state ──────────────────────────────────────── */
    .empty-state {
        text-align: center;
        padding: 5rem 2rem;
        color: #9aa8bc;
    }
    .empty-state .icon { font-size: 3rem; margin-bottom: 0.8rem; }
    .empty-state p { font-size: 1rem; max-width: 380px; margin: 0 auto; line-height: 1.6; }

    /* ── Section header ───────────────────────────────────── */
    .section-hdr {
        font-family: Arial, sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #002D64;
        margin: 1.2rem 0 0.6rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="hero-bar">
    <img src="https://biifund.com/images/bii-logo.svg" alt="BII">
    <h1>Play Store Reviews Scraper</h1>
</div>
<p class="hero-sub">Pull, preview, and export Google Play reviews for any app.</p>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.image("https://biifund.com/images/bii-logo.svg", width=120)
    st.markdown("#### Scrape Settings")
    st.divider()

    app_id = st.text_input(
        "APP ID",
        placeholder="com.example.app",
        help="From the Play Store URL: play.google.com/store/apps/details?id=**com.example.app**",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        country = st.text_input("COUNTRY", value="in", help="ISO alpha-2 code")
    with col_b:
        count = st.number_input("REVIEWS", min_value=1, max_value=10000, value=200, step=50)

    sort_order = st.selectbox("SORT BY", ["Most Relevant", "Newest"])

    filter_score = st.multiselect(
        "STAR FILTER",
        options=[1, 2, 3, 4, 5],
        default=[],
        help="Leave empty for all ratings",
    )

    st.divider()
    scrape = st.button("🚀  Start Scraping", use_container_width=True)

# ── Scraping logic ───────────────────────────────────────────
SORT_MAP = {"Most Relevant": Sort.MOST_RELEVANT, "Newest": Sort.NEWEST}

if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.meta = {}

if scrape:
    if not app_id.strip():
        st.error("Enter an App ID to continue.")
        st.stop()

    sort_val = SORT_MAP[sort_order]
    filter_val = filter_score if filter_score else None

    with st.status(f"Scraping **{app_id}** · {country.upper()} · {count} reviews", expanded=True) as status:
        try:
            all_reviews = []
            batch_size = min(count, 200)
            token = None

            while len(all_reviews) < count:
                remaining = count - len(all_reviews)
                fetch_count = min(batch_size, remaining)

                st.write(f"Fetching batch… ({len(all_reviews)}/{count})")

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

    # ── Build dataframe ──────────────────────────────────────
    df = pd.DataFrame(all_reviews)

    keep = [
        "userName", "score", "at", "content",
        "thumbsUpCount", "reviewCreatedVersion", "replyContent", "repliedAt",
    ]
    keep = [c for c in keep if c in df.columns]
    df = df[keep]

    rename = {
        "userName": "User",
        "score": "Rating",
        "at": "Date",
        "content": "Review",
        "thumbsUpCount": "Helpful",
        "reviewCreatedVersion": "App Version",
        "replyContent": "Dev Reply",
        "repliedAt": "Reply Date",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M")
    if "Reply Date" in df.columns:
        df["Reply Date"] = pd.to_datetime(df["Reply Date"]).dt.strftime("%Y-%m-%d %H:%M")

    if filter_val and len(filter_val) > 1:
        df = df[df["Rating"].isin(filter_val)]

    st.session_state.df = df
    st.session_state.meta = {"app_id": app_id, "country": country}


# ── Display results ──────────────────────────────────────────
df = st.session_state.df

if df is not None and not df.empty:
    meta = st.session_state.meta

    # ── Metrics row ──────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    avg = df["Rating"].mean() if "Rating" in df.columns else 0
    m1.metric("Total Reviews", f"{len(df):,}")
    m2.metric("Avg Rating", f"{avg:.2f} ⭐")
    m3.metric("5-Star", f"{(df['Rating'] == 5).sum():,}" if "Rating" in df.columns else "—")
    m4.metric("1-Star", f"{(df['Rating'] == 1).sum():,}" if "Rating" in df.columns else "—")

    # ── Two-column layout: chart + download ──────────────────
    chart_col, action_col = st.columns([3, 1])

    with chart_col:
        st.markdown('<div class="section-hdr">📊 Rating Distribution</div>', unsafe_allow_html=True)
        if "Rating" in df.columns:
            dist = df["Rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
            st.bar_chart(dist, color="#002D64", height=220)

    with action_col:
        st.markdown('<div class="section-hdr">⬇️ Export</div>', unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode("utf-8")
        fname = f"{meta.get('app_id','app')}_{meta.get('country','xx')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        st.download_button(
            label="📥  Download CSV",
            data=csv,
            file_name=fname,
            mime="text/csv",
            use_container_width=True,
        )
        st.caption(f"`{fname}`")
        st.markdown(f"""
        <div style="margin-top:1rem; font-size:0.8rem; color:#6b7a90; line-height:1.5;">
            <b>{len(df):,}</b> rows · <b>{len(df.columns)}</b> cols<br>
            {f'{len(csv)/1024:.0f} KB' }
        </div>
        """, unsafe_allow_html=True)

    # ── Data table ───────────────────────────────────────────
    st.markdown('<div class="section-hdr">📋 Reviews</div>', unsafe_allow_html=True)
    st.dataframe(
        df,
        use_container_width=True,
        height=500,
        column_config={
            "Rating": st.column_config.NumberColumn(format="%d ⭐"),
            "Helpful": st.column_config.NumberColumn(format="%d 👍"),
            "Review": st.column_config.TextColumn(width="large"),
        },
    )

else:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📱</div>
        <p>Enter an <b>App ID</b> in the sidebar and hit <b>Start Scraping</b> to pull reviews.</p>
    </div>
    """, unsafe_allow_html=True)
