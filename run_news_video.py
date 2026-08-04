import sys

from core.news_pipeline import create_video_from_url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python run_news_video.py <article_url>")

    output_path = create_video_from_url(sys.argv[1])
    print(f"Video created at {output_path}")
