<h1 align="center">Play Store Reviews Scraper</h1>

<p align="center">
  A lightweight Streamlit app that pulls, previews, and exports Google Play Store reviews.<br>
</p>

---

## What it does

- Scrapes up to 10,000 reviews for any Google Play app
- Filter by country, star rating, and sort order
- View summary metrics (avg rating, distribution) in-app
- One-click CSV export

## Quick start

```bash
# Clone
git clone https://github.com/aw-bii/Play_Store_Reviews_Scraper.git
cd Play_Store_Reviews_Scraper

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select this repo → set `app.py` as the main file
4. Hit **Deploy**

You'll get a public URL like `https://your-app.streamlit.app`. Set to invite-only under **Settings → Sharing** to restrict access to the team.

## Usage

| Field        | Example              | Description                          |
|--------------|----------------------|--------------------------------------|
| App ID       | `com.spotify.music`  | From the Play Store URL (`?id=...`)  |
| Country      | `in`                 | ISO 3166-1 alpha-2 code              |
| Reviews      | `500`                | Number of reviews to fetch (1–10000) |
| Sort By      | `Newest`             | Most Relevant or Newest              |
| Star Filter  | `1, 2`               | Optional — leave empty for all       |

## Dependencies

| Package              | Purpose                    |
|----------------------|----------------------------|
| `streamlit`          | Web UI                     |
| `google-play-scraper`| Play Store data extraction |
| `pandas`             | Data handling & CSV export |

## License

Internal tool — not for public distribution.
