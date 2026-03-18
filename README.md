# Play Store Reviews Scraper

A lightweight Streamlit app that pulls, previews, and exports Google Play Store reviews — with an AI-powered summary feature.

---

## What it does

- Scrapes up to 10,000 reviews for any Google Play app
- Filter by country, star rating, and sort order
- View summary metrics and rating distribution (chart or table view)
- Export as CSV or XLSX
- One-click AI summary of reviews powered by Gemini

## Quick start

```bash
git clone https://github.com/aw-bii/Play_Store_Reviews_Scraper.git
cd Play_Store_Reviews_Scraper

pip install -r requirements.txt

streamlit run app.py
```

Opens at `http://localhost:8501`.

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** — select this repo — set `app.py` as the main file
4. Deploy

Set to invite-only under **Settings > Sharing** to restrict access.

## Usage

| Field         | Example             | Description                            |
|---------------|---------------------|----------------------------------------|
| App ID        | `com.spotify.music` | From the Play Store URL (`?id=...`)    |
| Country       | `in`                | ISO 3166-1 alpha-2 code                |
| Reviews       | `500`               | Number of reviews to fetch (1-10000)   |
| Sort By       | `Newest`            | Newest or Most Relevant                |
| Star Filter   | `1, 2`              | Optional — leave empty for all         |
| App Version   | checkbox            | Toggle to include version column       |

## Dependencies

| Package              | Purpose                    |
|----------------------|----------------------------|
| `streamlit`          | Web UI                     |
| `google-play-scraper`| Play Store data extraction |
| `pandas`             | Data handling and export   |
| `openpyxl`           | XLSX export                |
| `requests`           | Gemini API calls           |

## License

Internal tool — not for public distribution.
