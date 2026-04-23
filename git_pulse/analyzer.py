import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoStatus:
    path: Path
    branch: str
    last_commit_hash: str
    last_commit_message: str
    last_commit_author: str
    last_commit_date: str
    is_dirty: bool
    uncommitted_count: int


def _run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip()


def analyze_repo(repo_path: Path) -> RepoStatus:
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path) or "unknown"

    last_hash = _run(["git", "log", "-1", "--format=%h"], repo_path) or "-"
    last_message = _run(["git", "log", "-1", "--format=%s"], repo_path) or "-"
    last_author = _run(["git", "log", "-1", "--format=%an"], repo_path) or "-"
    last_date = _run(["git", "log", "-1", "--format=%cr"], repo_path) or "-"

    status_output = _run(["git", "status", "--porcelain"], repo_path)
    is_dirty = bool(status_output)
    uncommitted_count = len(status_output.splitlines()) if status_output else 0

    return RepoStatus(
        path=repo_path,
        branch=branch,
        last_commit_hash=last_hash,
        last_commit_message=last_message,
        last_commit_author=last_author,
        last_commit_date=last_date,
        is_dirty=is_dirty,
        uncommitted_count=uncommitted_count,
    )
