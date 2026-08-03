import os
from pathlib import Path
import asyncio

import pandas as pd
import asyncpraw
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

if not CLIENT_ID or not CLIENT_SECRET or not USER_AGENT:
    raise ValueError("Missing Reddit credentials in .env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "reddit"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Reddit Client
# ==========================================================

reddit = asyncpraw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

# ==========================================================
# Subreddits
# ==========================================================

SUBREDDITS = [
    "economics",
    "Economy",
    "stocks",
    "investing",
    "wallstreetbets",
    "jobs",
    "recruitinghell",
    "layoffs",
    "povertyfinance",
    "personalfinance",
]

POST_LIMIT = 500


async def download_subreddit(subreddit_name):

    print(f"\nDownloading r/{subreddit_name}")

    subreddit = await reddit.subreddit(subreddit_name)

    posts = []

    async for submission in subreddit.new(limit=POST_LIMIT):

        posts.append(
            {
                "id": submission.id,
                "title": submission.title,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "upvote_ratio": submission.upvote_ratio,
                "url": submission.url,
                "selftext": submission.selftext,
            }
        )

    df = pd.DataFrame(posts)

    output = RAW_DIR / f"{subreddit_name}.csv"

    df.to_csv(output, index=False)

    print(f"Saved -> {output}")


async def main():

    print("=" * 60)
    print("MIRAI - REDDIT ETL")
    print("=" * 60)

    for subreddit in SUBREDDITS:
        try:
            await download_subreddit(subreddit)

        except Exception as e:
            print(f"Failed -> {subreddit}")
            print(e)

    await reddit.close()

    print("\nFinished downloading Reddit datasets.")

if __name__ == "__main__":
    asyncio.run(main())