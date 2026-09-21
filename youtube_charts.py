import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ----------------------------
# Plotting functions
# ----------------------------
def plot_yearly_metrics(yearly_summary):
    if yearly_summary is None or yearly_summary.empty:
        return

    year_trend = yearly_summary.sort_values("year")
    plt.figure(figsize=(14, 8))

    plt.subplot(2, 2, 1)
    plt.bar(year_trend["year"].astype(str), year_trend["video_count"], color="steelblue")
    plt.title("Videos per year")
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 2)
    plt.bar(year_trend["year"].astype(str), year_trend["total_views"], color="darkorange")
    plt.title("Total views per year")
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 3)
    plt.bar(year_trend["year"].astype(str), year_trend["total_likes"], color="forestgreen")
    plt.title("Total likes per year")
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 4)
    plt.bar(year_trend["year"].astype(str), year_trend["total_comments"], color="crimson")
    plt.title("Total comments per year")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig("youtube_yearly_metrics.png")
    print("Saved: youtube_yearly_metrics.png")


def plot_video_type_distribution(all_df):
    type_counts = all_df["video_type"].value_counts()
    plt.figure(figsize=(8, 6))
    type_counts.plot(kind="bar")
    plt.title("Video type distribution")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("youtube_video_type.png")
    print("Saved: youtube_video_type.png")


def plot_monthly_trend(all_df):
    if "month" not in all_df.columns:
        return

    trend = all_df.groupby("month", as_index=False)["view_count"].sum().sort_values("month")
    plt.figure(figsize=(12, 5))
    plt.plot(trend["month"].tolist(), trend["view_count"].tolist(), marker="o")
    plt.title("YouTube keyword view trend")
    plt.xlabel("Month")
    plt.ylabel("Views")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("youtube_trend.png")
    print("Saved: youtube_trend.png")


def generate_charts(all_df, yearly_summary=None):
    plot_yearly_metrics(yearly_summary)
    plot_video_type_distribution(all_df)
    plot_monthly_trend(all_df)
