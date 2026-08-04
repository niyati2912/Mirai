import os
from pathlib import Path

import pandas as pd
from github import Github
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "github"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# GitHub Client

github = Github(TOKEN)

# Repositories

REPOSITORIES = [
    "tensorflow/tensorflow",
    "pytorch/pytorch",
    "scikit-learn/scikit-learn",
    "microsoft/vscode",
    "huggingface/transformers",
    "langchain-ai/langchain",
    "openai/openai-python",
    "facebook/react",
    "nodejs/node",
    "kubernetes/kubernetes"
]


def download_repo(repo_name):

    print(f"\nDownloading {repo_name}")

    try:

        repo = github.get_repo(repo_name)

        data = {
            "Repository": repo.full_name,
            "Stars": repo.stargazers_count,
            "Forks": repo.forks_count,
            "Open_Issues": repo.open_issues_count,
            "Subscribers": repo.subscribers_count,
            "Language": repo.language,
            "Created_At": repo.created_at,
            "Updated_At": repo.updated_at,
            "Pushed_At": repo.pushed_at,
            "Watchers": repo.watchers_count,
            "Size_KB": repo.size,
            "Default_Branch": repo.default_branch,
        }

        df = pd.DataFrame([data])

        filename = repo.full_name.replace("/", "_") + ".csv"

        output = RAW_DIR / filename

        df.to_csv(output, index=False)

        print(f"Saved -> {output}")

    except Exception as e:

        print(f"Failed -> {repo_name}")
        print(e)



def main():

    print("=" * 60)
    print("MIRAI - GITHUB ETL")
    print("=" * 60)

    for repo in REPOSITORIES:

        download_repo(repo)

    print("\nFinished downloading GitHub datasets.")

if __name__ == "__main__":
    main()