from abc import ABC, abstractmethod
from utils.network_helpers import ping


class Company(ABC):
    def __init__(self, company_name, site):
        self.site = site
        self.company_name = company_name
        self.flags = {"login_ok": False, "is_cam_ping": False, "is_nvr_ping": False}
        self.captures = {"num_captures": "", "last_time_captures": ""}
        self.times = {"check_time": "", "current_camera_time": "", "is_synchronized": False}
        self.unknown_morning = ""
        self.unknown_night = ""
        self.error_message = ""

    def ping_camera(self):
        is_cam_ping = ping(self.site.prot, self.site.ip, self.site.camera.port)
        self.flags["is_cam_ping"] = is_cam_ping

    def ping_nvr(self):
        is_nvr_ping = ping(self.site.prot, self.site.ip, self.site.nvr.port)
        self.flags["is_nvr_ping"] = is_nvr_ping

    @abstractmethod
    def get_captures(self):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass
