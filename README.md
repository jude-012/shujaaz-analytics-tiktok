# Shujaaz Kenya — Social Media Analytics Dashboard

Live analytics dashboard for @shujaazkenya covering YouTube, TikTok and Facebook.

## Live dashboard
**https://jude-012.github.io/shujaaz-analytics**

## How it works
- GitHub Actions runs `fetch.py` every day at **6am EAT**
- The script pulls fresh YouTube data and saves `shujaaz_videos.json`
- All HTML dashboards read the JSON files automatically
- TikTok and Facebook dashboards use exported CSV data (updated manually)

## Files

| File | What it is |
|---|---|
| `index.html` | YouTube analytics dashboard |
| `shujaaz_videos.json` | YouTube data — auto-updated daily |
| `tiktok_dashboard.html` | TikTok overview dashboard |
| `tiktok_data.json` | TikTok overview data |
| `tiktok_content_dashboard.html` | TikTok content/video dashboard |
| `tiktok_content.json` | TikTok content data |
| `tiktok_connect.html` | TikTok OAuth demo page |
| `fetch.py` | YouTube daily fetch script |
| `requirements.txt` | Python dependencies |
| `.github/workflows/daily-fetch.yml` | GitHub Actions schedule |

## One-time setup

### 1. Add YouTube API key
- Repo → **Settings → Secrets and variables → Actions**
- **New repository secret** → Name: `YOUTUBE_API_KEY` → paste your key

### 2. Enable GitHub Pages
- Repo → **Settings → Pages**
- Source: **Deploy from a branch** → Branch: `main` → folder: `/ (root)`
- Save

### 3. Run first fetch manually
- **Actions → Daily YouTube Fetch → Run workflow**

## TikTok OAuth setup (after production approval)
Edit `tiktok_connect.html` line 99 — replace `PASTE_YOUR_CLIENT_KEY_HERE` with your actual Client Key from developers.tiktok.com.
