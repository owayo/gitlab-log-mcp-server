#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from mcp.server.fastmcp import FastMCP

from src.utils.git_utils import get_current_commit_sha
from src.utils.gitlab_utils import (
    get_job_console_log,
    get_jobs_by_commit,
)

# Initialize MCP server
mcp = FastMCP("gitlab-mcp")


@mcp.tool()
def get_current_commit_jobs() -> str:
    """現在のコミットに関連するGitLabジョブの一覧を取得"""
    try:
        commit_sha = get_current_commit_sha()
        jobs = get_jobs_by_commit(commit_sha)

        if not jobs:
            return f"コミット {commit_sha[:8]} に関連するジョブが見つかりません。"

        job_list = []
        for job in jobs:
            status_emoji = {
                "success": "✅",
                "failed": "❌",
                "running": "🔄",
                "pending": "⏳",
                "canceled": "🚫",
                "skipped": "⏭️",
            }.get(job["status"], "❓")

            job_list.append(
                f"{status_emoji} **{job['name']}** (ID: {job['id']})\n"
                f"  - ステージ: {job['stage']}\n"
                f"  - ステータス: {job['status']}\n"
                f"  - パイプラインID: {job['pipeline_id']}"
            )

        return f"コミット {commit_sha[:8]} のジョブ一覧:\n\n" + "\n\n".join(job_list)
    except Exception as e:
        return f"エラー: {str(e)}"


@mcp.tool()
def get_job_log(job_id: int) -> str:
    """指定したジョブIDのコンソールログを取得"""
    try:
        log = get_job_console_log(job_id)
        return f"ジョブID #{job_id} のコンソールログ:\n```\n{log}\n```"
    except Exception as e:
        return f"エラー: {str(e)}"


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        mcp.run(transport="stdio")
    elif args[0] == "test" and len(args) >= 2:
        if args[1] == "commit-jobs":
            print(get_current_commit_jobs())
        elif args[1] == "job-log":
            if len(args) == 3:
                try:
                    job_id = int(args[2])
                    print(get_job_log(job_id))
                except ValueError:
                    print("無効なジョブIDです。数値を指定してください。")
            else:
                print("無効な引数です。使用方法: test job-log <job_id>")
        else:
            print("無効なテスト引数です。")
    else:
        print("""使用方法:
python main.py                           # MCPサーバーを起動
python main.py test commit-jobs          # 現在のコミットのジョブ一覧を取得
python main.py test job-log <job_id>     # 指定したジョブのログを取得
""")
