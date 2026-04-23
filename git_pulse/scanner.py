import os
from pathlib import Path


class RepoScanner:
    def __init__(self, root: Path, ignored_folders: list[str] | None = None, max_depth: int = 5):
        self.root = Path(root)
        self.ignored = set(ignored_folders or [])
        self.max_depth = max_depth

    def _scan(self, path: Path, depth: int):
        if depth > self.max_depth:
            return
        try:
            with os.scandir(path) as entries:
                has_git = False
                subdirs = []
                for entry in entries:
                    if entry.name == ".git" and entry.is_dir():
                        has_git = True
                    elif entry.is_dir() and entry.name not in self.ignored and not entry.name.startswith("."):
                        subdirs.append(Path(entry.path))
                if has_git:
                    yield path
                else:
                    for subdir in subdirs:
                        yield from self._scan(subdir, depth + 1)
        except PermissionError:
            pass

    def scan(self) -> list[Path]:
        return sorted(self._scan(self.root, depth=0))
