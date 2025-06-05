# GitLab Log MCP Server

GitLabのコミットハッシュに基づいてジョブログを取得することに特化したModel Context Protocol (MCP) サーバーです。現在のプロジェクトのコミットハッシュと一致するジョブを取得し、ジョブのコンソールログを取得します。

## 概要

このMCPサーバーは、GitLabのAPIを利用して以下の情報をAIアシスタントに提供します：

1. 現在のGitコミットに関連するGitLabジョブの一覧
2. 特定のジョブIDのコンソールログ

MCPの機能を使用することで、AIアシスタントはGitLabのジョブ情報を直接取得し、CI/CDのデバッグやエラー解析を支援できます。

## インストール

```bash
# uvのインストール
$ curl -LsSf https://astral.sh/uv/install.sh | sh

$ cd /path/to/this-mcp-server
# ライブラリのインストール
$ uv sync
```

## 準備

GitLabのアクセストークンが必要です。
アクセストークンはGitLabの設定→アクセストークンにて発行してください。
発行する際、`read_api` にチェックを入れてください。

## 機能

### 1. 現在のコミットのジョブ一覧取得 (`get_current_commit_jobs`)

現在のGitコミットに関連するすべてのGitLabジョブの一覧を取得します。

**出力**:
- ジョブ名、ID、ステージ、ステータス、パイプラインIDを含むジョブ一覧

### 2. ジョブのコンソールログ取得 (`get_job_log`)

指定したジョブIDのコンソールログを取得します。

**入力**:
- `job_id`: 取得したいジョブのID（数値）

**出力**:
- 指定したジョブの完全なコンソールログ


## AIアシスタントとの連携

AIアシスタント（Claude等）は、このMCPサーバーに対して以下の関数を呼び出すことができます：

- `get_current_commit_jobs()`: 現在のコミットに関連するジョブ一覧取得
- `get_job_log(job_id)`: 指定したジョブのコンソールログ取得

これらの関数は、現在のブランチやコミットに関連する情報を自動的に取得します。

## Claude for Desktopでの設定

`claude_desktop_config.json` に以下の設定を追加してください：

```json
{
    "mcpServers": {
        "gitlab-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/this-mcp-server",
                "run",
                "main.py"
            ],
            "env": {
                "GITLAB_URL": "your_gitlab_url",
                "GITLAB_PROJECT_NAME": "gitlab_project_name",
                "GITLAB_API_KEY": "your_gitlab_api_key",
                "GIT_REPO_PATH": "/path/to/git/repo"
            }
        }
    }
}
```

## Cursorでの設定

プロジェクトルートの `.cursor/mcp.json` に以下の設定を追加してください：

```json
{
    "mcpServers": {
        "gitlab-mcp": {
            "command": "env",
            "args": [
                "GITLAB_URL=your_gitlab_url",
                "GITLAB_PROJECT_NAME=gitlab_project_name",
                "GITLAB_API_KEY=your_gitlab_api_key",
                "GIT_REPO_PATH=/path/to/git/repo",
                "uv",
                "--directory",
                "/path/to/this-mcp-server",
                "run",
                "main.py"
            ]
        }
    }
}
```

注意：上記の設定例で、以下の値を適切に置き換えてください：
- `your_gitlab_api_key`: GitLab APIのアクセストークン
- `/path/to/git/repo`: ローカルGitリポジトリの絶対パス
- `/path/to/this-mcp-server`: このMCPサーバーのディレクトリの絶対パス
