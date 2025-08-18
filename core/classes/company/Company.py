from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import pytz
import requests

from utils.network_helpers import ping
from utils.utils import datetime_format


class Company(ABC):
    def __init__(self, company_name, site, index, unknown_morning, unknown_night):
        self.site = site
        self.session = requests.Session()
        self.username = self.site.config["project_setup"]["username"]
        self.password = self.site.nvr.password
        self.camera_password = self.site.camera.password
        self.company_name = company_name
        self.timeout = self.site.config["project_setup"]["times"]["timeout_ping"]
        self.flags = {"login_ok": False, "login_camera_ok": False, "is_camera_ping": False, "is_nvr_ping": False}
        self.captures = {"num_captures": "", "last_time_captures": "","playback": "", "num_captures_per_day": ""}
        self.times = {"check_time": "", "current_camera_time": "", "current_nvr_time": "",
                      "is_camera_synchronized": "Unknown error occurred", "is_nvr_synchronized": "Unknown error occurred"}
        self.unknowns = {"morning": unknown_morning, "night": unknown_night}
        self.error_message = ""
        self.index = index + 2
        self.ftp_1_status = ""
        self.ftp_2_status = ""
        self.example_picture = ""
        self.live_view = False

    def ping_camera(self):
        is_cam_ping = ping(self, comp="camera")
        self.flags["is_camera_ping"] = is_cam_ping

    def ping_nvr(self):
        is_nvr_ping = ping(self, comp="nvr")
        self.flags["is_nvr_ping"] = is_nvr_ping

    def define_check_time(self):
        format_str = self.site.config["project_setup"]["format_datetime"]
        current_time = datetime.now(pytz.timezone("Asia/Jerusalem")).strftime(format_str)
        self.times["check_time"] = current_time

    def compare_between_dates(self, type):
        match type:
            case "camera":
                if not self.flags["login_camera_ok"]:
                    self.times['is_camera_synchronized'] = "אין אפשרות להיכנס למצלמה"
                    return
            case "nvr":
                if not self.flags["login_ok"]:
                    self.times['is_nvr_synchronized'] = "אין אפשרות להיכנס לnvr"
                    return

        if self.times[f"current_{type}_time"] == "" or self.times["check_time"] == "":
            self.times[f"is_{type}_synchronized"] = f'couldnt access {type} time'

        time_diff = self.site.config["project_setup"]["times"]["check_minutes_diff"]
        camera_time = datetime_format(self.times[f"current_{type}_time"])
        current_time = datetime_format(self.times["check_time"])
        diff = abs(camera_time - current_time)

        self.times[f"is_{type}_synchronized"] = diff < timedelta(minutes=time_diff)

    @abstractmethod
    def get_captures(self, type):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass
