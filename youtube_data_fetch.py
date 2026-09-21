import os

import pandas as pd
from googleapiclient.discovery import build

# ----------------------------
# 1. Configuration
# ----------------------------
API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("Please set the environment variable YOUTUBE_API_KEY first.")

KEYWORDS = [
    "南海トラフ シミュレーション",
    "緊急地震速報 シミュレーション",
    "地震速報 シミュレーション",
    "南海トラフ 緊急地震速報",
    "南海トラフ巨大地震 シミュレーション",
    "架空 緊急地震速報",
    "架空 地震速報",
    "地震 再現",
    "地震 MAD",
    "緊急地震速報 再現",
    "地震速報 架空" 
]

youtube = build("youtube", "v3", developerKey=API_KEY)

# ----------------------------
# 2. Get YouTube category map
# ----------------------------
def get_category_map():
    try:
        categories = youtube.videoCategories().list(
            part="snippet",
            regionCode="US"
        ).execute()
        return {
            item["id"]: item["snippet"]["title"]
            for item in categories.get("items", [])
        }
    except Exception as exc:
        print("Failed to get category mapping:", exc)
        return {}


CATEGORY_MAP = get_category_map()


# ----------------------------
# 3. Video type classification
# ----------------------------
def classify_video(title: str) -> str:
    title = (title or "").lower()
    if any(word in title for word in ["教程", "教学", "入门", "基础", "learn", "course", "training"]):
        return "Tutorial"
    if any(word in title for word in ["评测", "测评", "对比", "review", "推荐"]):
        return "Review/Recommendation"
    if any(word in title for word in ["新闻", "热点", "更新", "analysis"]):
        return "News/Info"
    if any(word in title for word in ["直播", "live", "实况"]):
        return "Live"
    if any(word in title for word in ["实战", "项目", "案例", "demo", "实践"]):
        return "Practical/Case"
    return "Other"


# ----------------------------
# 4. Search videos by keyword
# ----------------------------
def search_videos_by_keyword(keyword: str, max_results: int = 50):
    items = []
    next_page_token = None

    while len(items) < max_results:
        request = youtube.search().list(
            q=keyword,
            part="snippet",
            type="video",
            maxResults=min(50, max_results - len(items)),
            order="viewCount",
            pageToken=next_page_token,
        )
        data = request.execute()
        items.extend(data.get("items", []))
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return items[:max_results]


# ----------------------------
# 5. Get video details
# ----------------------------
def get_video_details(video_ids):
    if not video_ids:
        return []

    request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids),
    )
    response = request.execute()
    return response.get("items", [])


# ----------------------------
# 6. Process one keyword
# ----------------------------
def analyze_keyword(keyword: str):
    search_results = search_videos_by_keyword(keyword, max_results=50)
    video_ids = []
    seen = set()

    for item in search_results:
        video_id = item.get("id", {}).get("videoId")
        if video_id and video_id not in seen:
            seen.add(video_id)
            video_ids.append(video_id)

    details = get_video_details(video_ids)
    rows = []

    for item in details:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item.get("id", "")

        published_at = snippet.get("publishedAt", "")
        category_id = snippet.get("categoryId", "unknown")
        title = snippet.get("title", "")
        channel_title = snippet.get("channelTitle", "")

        rows.append({
            "keyword": keyword,
            "video_id": video_id,
            "title": title,
            "channel_title": channel_title,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "published_at": published_at,
            "year": pd.to_datetime(published_at, errors="coerce").year if published_at else None,
            "category_id": category_id,
            "category_name": CATEGORY_MAP.get(category_id, "Unknown category"),
            "video_type": classify_video(title),
            "view_count": int(stats.get("viewCount", 0) or 0),
            "like_count": int(stats.get("likeCount", 0) or 0),
            "comment_count": int(stats.get("commentCount", 0) or 0),
        })

    return pd.DataFrame(rows)


# ----------------------------
# 7. Fetch all data only once
# ----------------------------
def fetch_all_data(keywords=None):
    keyword_list = keywords or KEYWORDS
    dfs = []

    for keyword in keyword_list:
        df = analyze_keyword(keyword)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        raise ValueError("No video data found. Please check the API key and keywords.")

    all_df = pd.concat(dfs, ignore_index=True)
    all_df = all_df.drop_duplicates(subset=["video_id"], keep="first").reset_index(drop=True)

    if "published_at" in all_df.columns:
        all_df["published_at"] = pd.to_datetime(all_df["published_at"], errors="coerce")
        all_df["year"] = all_df["published_at"].dt.year
        all_df["month"] = all_df["published_at"].dt.to_period("M").astype(str)

    return all_df


# ----------------------------
# 8. Build yearly summaries
# ----------------------------
def build_yearly_summary(all_df):
    yearly_summary = pd.DataFrame()
    keyword_year_summary = pd.DataFrame()

    if "year" in all_df.columns:
        yearly_summary = (
            all_df.groupby("year", as_index=False)
            .agg(
                video_count=("title", "count"),
                total_views=("view_count", "sum"),
                total_likes=("like_count", "sum"),
                total_comments=("comment_count", "sum"),
            )
            .sort_values("year")
        )

        keyword_year_summary = (
            all_df.groupby(["year", "keyword"], as_index=False)
            .agg(
                video_count=("title", "count"),
                total_views=("view_count", "sum"),
                total_likes=("like_count", "sum"),
                total_comments=("comment_count", "sum"),
            )
            .sort_values(["year", "keyword"])
        )

    return yearly_summary, keyword_year_summary


# ----------------------------
# 9. Print summary reports
# ----------------------------
def print_summary(all_df, yearly_summary=None, keyword_year_summary=None):
    print("=== Total video count ===")
    print(len(all_df))

    print("\n=== Count by keyword ===")
    print(all_df["keyword"].value_counts())

    print("\n=== Count by category ===")
    print(all_df["category_name"].value_counts().head(10))

    print("\n=== Count by video type ===")
    print(all_df["video_type"].value_counts())

    if yearly_summary is not None and not yearly_summary.empty:
        print("\n=== Yearly summary ===")
        print(yearly_summary)

        print("\n=== Keyword and yearly summary ===")
        print(keyword_year_summary)

    print("\n=== Top 10 videos by views ===")
    top_videos = all_df.sort_values("view_count", ascending=False)[
        ["keyword", "title", "channel_title", "published_at", "view_count", "like_count", "comment_count", "video_url"]
    ].head(10)
    print(top_videos)

    if "month" in all_df.columns:
        trend = all_df.groupby("month", as_index=False)["view_count"].sum()
        trend = trend.sort_values("month")
        print("\n=== Monthly view trend ===")
        print(trend)

    all_df.to_csv("youtube_keyword_analysis.csv", index=False)

    if yearly_summary is not None and not yearly_summary.empty:
        yearly_summary.to_csv("youtube_yearly_summary.csv", index=False)
        keyword_year_summary.to_csv("youtube_keyword_year_summary.csv", index=False)

    print("\nSaved: youtube_keyword_analysis.csv")
    if yearly_summary is not None and not yearly_summary.empty:
        print("Saved: youtube_yearly_summary.csv")
        print("Saved: youtube_keyword_year_summary.csv")

    return top_videos
