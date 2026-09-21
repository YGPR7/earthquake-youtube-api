# YouTube Keyword Analysis

This project collects YouTube video data for earthquake and emergency-alert related keywords, summarizes the results by year and keyword, and generates charts.

The search keywords are mainly Japanese terms related to:

- Nankai Trough earthquake simulations
- Emergency earthquake warnings
- Earthquake news and recreations
- Fictional earthquake-alert videos

## Requirements

- Python 3.9 or later
- A YouTube Data API v3 key

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install pandas matplotlib google-api-python-client
```

## API key

Set your YouTube API key in the `YOUTUBE_API_KEY` environment variable. In PowerShell, this sets it for the current terminal session:

```powershell
$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

Do not put the API key directly in a Python file or commit it to GitHub.

## Run the analysis

From the project folder, run:

```powershell
python api.py
```

The script searches up to 50 videos for each configured keyword, removes duplicate videos, prints summary statistics, and writes the output files listed below.

## Generated files

### CSV files

- `youtube_keyword_analysis.csv` - Detailed video-level data, including titles, channels, publication dates, views, likes, comments, and video URLs.
- `youtube_yearly_summary.csv` - Total video, view, like, and comment counts grouped by year.
- `youtube_keyword_year_summary.csv` - The same metrics grouped by year and keyword.

### Charts

- `youtube_yearly_metrics.png` - Yearly video, view, like, and comment metrics.
- `youtube_video_type.png` - Video type distribution based on title classification.
- `youtube_trend.png` - Monthly total view trend.

Running the script again refreshes these files with new API data.

## Project files

- `api.py` - Main entry point.
- `youtube_data_fetch.py` - YouTube API requests, classification, aggregation, and CSV export.
- `youtube_charts.py` - Chart generation.

## Notes

- YouTube API requests use quota, so repeated runs may consume your daily quota.
- View, like, and comment counts reflect the data returned at the time of collection and can change later.
- The default keyword list is defined in `youtube_data_fetch.py`.
