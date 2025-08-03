import os
import datetime


class Logger:
    _instance = None
    _base_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../", "logs")

    def __init__(self):
        if Logger._instance is not None:
            return
        Logger._instance = self
        self._log_filenames = {}
        self._initialize_log_files()

    def _initialize_log_files(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        categories = self._get_categories()

        for category in categories:
            category_dir = os.path.join(self._base_log_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir, exist_ok=True)

            log_file_path = os.path.join(category_dir, f"{timestamp}.log")
            self._log_filenames[category] = log_file_path

            with open(log_file_path, "w", encoding="utf-8", errors="ignore") as log_file:
                log_file.write(f"--- {category.upper()} LOG ---\n")
                log_file.write(f"Log started at {timestamp}\n\n")

    def log(self, category, message):
        if category not in self._log_filenames:
            raise ValueError(f"Invalid log category: {category}")

        log_file_path = self._log_filenames[category]
        self._write_log(log_file_path, message)

    def _get_categories(self):
        return ["ping", "captures", "unknowns", "login", "camera time", "device info", "unexpected", "ftp", "live view",
                "playback"]

    def _write_log(self, file_path, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a", encoding="utf-8", errors="ignore") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")

    @staticmethod
    def get_instance():
        if Logger._instance is None:
            Logger()
        return Logger._instance
