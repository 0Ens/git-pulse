from pathlib import Path


def find_git_repos(root: Path, ignored_folders: list[str]) -> list[Path]:
    """Recursively find all git repositories under root, skipping ignored folders."""
    repos = []
    ignored_set = set(ignored_folders)

    def _walk(directory: Path):
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return

        if (directory / ".git").is_dir():
            repos.append(directory)
            return  # don't recurse into nested repos

        for entry in entries:
            if entry.is_dir() and entry.name not in ignored_set and not entry.name.startswith("."):
                _walk(entry)

    _walk(root)
    return sorted(repos)
