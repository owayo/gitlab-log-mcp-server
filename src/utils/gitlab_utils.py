#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any, Dict, List

import gitlab
from gitlab.v4.objects import Project


# GitLab URLの取得
def get_gitlab_url() -> str:
    """
    環境変数からGitLabのURLを取得します。

    Returns:
        str: GitLabのURL

    Raises:
        ValueError: 環境変数が設定されていない場合
    """
    gitlab_url = os.environ.get("GITLAB_URL")
    if not gitlab_url:
        raise ValueError("GITLAB_URL環境変数が設定されていません。")
    return gitlab_url


# プロジェクトID
def get_gitlab_project_id() -> str:
    """
    環境変数からGitLabのプロジェクトIDを取得します。

    Returns:
        str: GitLabのプロジェクトID

    Raises:
        ValueError: 環境変数が設定されていない場合
    """
    project_id = os.environ.get("GITLAB_PROJECT_NAME")
    if not project_id:
        raise ValueError("GITLAB_PROJECT_NAME環境変数が設定されていません。")
    return project_id


def get_gitlab_client() -> gitlab.Gitlab:
    """
    GitLabクライアントを取得します。

    Returns:
        gitlab.Gitlab: GitLabクライアントインスタンス

    Raises:
        ValueError: GitLab APIキーが見つからない場合や接続に失敗した場合
    """
    # 環境変数からGitLab APIキーを取得
    gitlab_api_key = os.environ.get("GITLAB_API_KEY")

    if not gitlab_api_key:
        raise ValueError("GITLAB_API_KEY環境変数が設定されていません。")

    # GitLabのURLを取得
    gitlab_url = get_gitlab_url()

    # 接続方法を順番に試行
    connection_urls = [
        gitlab_url,
    ]

    last_error = None
    for url in connection_urls:
        try:
            gl = gitlab.Gitlab(url, private_token=gitlab_api_key)
            gl.auth()
            return gl
        except Exception as e:
            last_error = e
            continue

    # すべての接続方法が失敗した場合
    raise ValueError(f"GitLabへの接続に失敗しました: {str(last_error)}")


def get_gitlab_project() -> Project:
    """
    GitLabプロジェクトを取得します。

    Returns:
        Project: GitLabプロジェクトインスタンス

    Raises:
        ValueError: プロジェクトの取得に失敗した場合
    """
    try:
        gl = get_gitlab_client()
        project_id = get_gitlab_project_id()

        # プロジェクトIDを使用してプロジェクトを取得
        try:
            project = gl.projects.get(project_id)
            return project
        except gitlab.exceptions.GitlabGetError:
            # IDでの取得に失敗した場合は検索を試行
            projects = gl.projects.list(search=project_id)
            if projects:
                return projects[0]

            # 検索でも見つからない場合
            raise ValueError(f"プロジェクト '{project_id}' が見つかりません。")
    except ValueError as e:
        # 既存のValueErrorを再送出
        raise e
    except Exception as e:
        # その他の例外は新しいValueErrorでラップ
        raise ValueError(f"GitLabプロジェクトの取得に失敗しました: {str(e)}")


def get_jobs_by_commit(commit_sha: str) -> List[Dict[str, Any]]:
    """
    指定したコミットSHAに関連するジョブを取得します。

    Args:
        commit_sha (str): コミットSHA

    Returns:
        List[Dict[str, Any]]: ジョブのリスト

    Raises:
        ValueError: ジョブの取得に失敗した場合
    """
    try:
        project = get_gitlab_project()

        # コミットSHAに関連するパイプラインを検索
        pipelines = project.pipelines.list(sha=commit_sha)

        if not pipelines:
            return []

        jobs = []
        for pipeline in pipelines:
            # パイプラインのジョブを取得
            pipeline_jobs = project.pipelines.get(pipeline.id).jobs.list()
            for job in pipeline_jobs:
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "status": job.status,
                    "stage": job.stage,
                    "created_at": job.created_at,
                    "finished_at": getattr(job, "finished_at", None),
                    "pipeline_id": pipeline.id,
                    "commit_sha": commit_sha,
                }
                jobs.append(job_info)

        return jobs
    except Exception as e:
        raise ValueError(f"コミット {commit_sha} のジョブ取得に失敗しました: {str(e)}")


def get_job_console_log(job_id: int) -> str:
    """
    指定したジョブIDのコンソールログを取得します。

    Args:
        job_id (int): ジョブID

    Returns:
        str: ジョブのコンソールログ

    Raises:
        ValueError: ログの取得に失敗した場合
    """
    try:
        project = get_gitlab_project()

        # ジョブの詳細を取得
        job = project.jobs.get(job_id)

        # コンソールログを取得
        trace = job.trace()

        return trace
    except gitlab.exceptions.GitlabGetError:
        raise ValueError(f"ジョブID #{job_id} が見つかりません。")
    except Exception as e:
        raise ValueError(f"ジョブID #{job_id} のログ取得に失敗しました: {str(e)}")
