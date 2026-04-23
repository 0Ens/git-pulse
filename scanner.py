import os
import subprocess
from typing import Generator


class RepoScanner:
    def __init__(self, root: str, max_depth: int = 5):
        self.root = os.path.abspath(root)
        self.max_depth = max_depth

    def _scan(self, path: str, depth: int) -> Generator[str, None, None]:
        if depth > self.max_depth:
            return
        try:
            with os.scandir(path) as entries:
                has_git = False
                subdirs = []
                for entry in entries:
                    if entry.name == ".git" and entry.is_dir():
                        has_git = True
                    elif entry.is_dir() and not entry.name.startswith("."):
                        subdirs.append(entry.path)
                if has_git:
                    yield path
                else:
                    for subdir in subdirs:
                        yield from self._scan(subdir, depth + 1)
        except PermissionError:
            pass

    def _run(self, cmd: list[str], cwd: str) -> str:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def scan(self) -> dict[str, dict]:
        repos = {}
        for repo_path in self._scan(self.root, depth=0):
            status = self._run(["git", "status", "--short"], repo_path)
            repos[repo_path] = {
                "branch": self._run(["git", "branch", "--show-current"], repo_path),
                "status": status,
                "dirty": bool(status),
            }
        return repos


if __name__ == "__main__":
    import sys
    import json

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    scanner = RepoScanner(root)
    result = scanner.scan()
    print(json.dumps(result, indent=2, ensure_ascii=False))
