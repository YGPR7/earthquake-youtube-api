from youtube_data_fetch import build_yearly_summary, fetch_all_data, print_summary
from youtube_charts import generate_charts


if __name__ == "__main__":
    all_df = fetch_all_data()
    yearly_summary, keyword_year_summary = build_yearly_summary(all_df)
    print_summary(all_df, yearly_summary, keyword_year_summary)
    generate_charts(all_df, yearly_summary)
