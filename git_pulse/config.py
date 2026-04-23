import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".git-pulse" / "config.json"
DEFAULT_IGNORED = ["node_modules", ".git", "__pycache__", ".venv", "dist", "build"]


class ConfigManager:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._data: dict = {}
        self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._data = json.load(f)
        else:
            self._data = {"ignored_folders": DEFAULT_IGNORED.copy()}

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_ignored_folders(self) -> list[str]:
        return self._data.get("ignored_folders", [])

    def add_ignored_folder(self, folder: str) -> bool:
        """Returns False if folder was already in the list."""
        folders = self.get_ignored_folders()
        if folder in folders:
            return False
        folders.append(folder)
        self._data["ignored_folders"] = folders
        self.save()
        return True

    def remove_ignored_folder(self, folder: str) -> bool:
        """Returns False if folder was not in the list."""
        folders = self.get_ignored_folders()
        if folder not in folders:
            return False
        folders.remove(folder)
        self._data["ignored_folders"] = folders
        self.save()
        return True
