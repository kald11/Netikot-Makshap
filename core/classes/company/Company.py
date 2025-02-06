from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import pytz
import requests

from utils.network_helpers import ping
from utils.utils import datetime_format


class Company(ABC):
    def __init__(self, company_name, site):
        self.site = site
        self.session = requests.Session()
        self.username = self.site.config["project_setup"]["username"]
        self.password = self.site.nvr.password
        self.company_name = company_name
        self.timeout = self.site.config["project_setup"]["times"]["timeout_ping"]
        self.flags = {"login_ok": False, "is_cam_ping": False, "is_nvr_ping": False}
        self.captures = {"num_captures": "", "last_time_captures": ""}
        self.times = {"check_time": "", "current_camera_time": "", "is_synchronized": False}
        self.unknowns = {"morning": "", "night": ""}
        self.error_message = ""

    def ping_camera(self):
        is_cam_ping = ping(self.site.prot, self.site.ip, self.site.camera.port)
        self.flags["is_cam_ping"] = is_cam_ping

    def ping_nvr(self):
        is_nvr_ping = ping(self.site.prot, self.site.ip, self.site.nvr.port)
        self.flags["is_nvr_ping"] = is_nvr_ping

    def define_check_time(self):
        format = self.site.config["project_setup"]["format_datetime"]
        current_time = datetime.now(pytz.timezone("Asia/Jerusalem")).strftime(format)
        self.times["check_time"] = current_time

    def compare_between_dates(self):
        if self.times["current_camera_time"] == "" or self.times["check_time"] == "":
            return
        time_diff = self.site.config["project_setup"]["times"]["check_minutes_diff"]
        camera_time = datetime_format(self.times["current_camera_time"])
        current_time = datetime_format(self.times["check_time"])
        diff = abs(camera_time - current_time)
        self.times["is_synchronized"] = diff < timedelta(minutes=time_diff)

    @abstractmethod
    def get_captures(self):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass
