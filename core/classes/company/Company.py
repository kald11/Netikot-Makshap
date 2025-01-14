from abc import ABC, abstractmethod


class Company(ABC):
    def __init__(self, company_name, site):
        self.site = site
        self.company_name = company_name
        self.flags = {"login_ok": False, "is_cam_ping": False, "is_nvr_ping": False}
        self.captures = {"num_captures": "", "last_time_captures": ""}
        self.times = {"check_time": "", "current_camera_time": "", "is_synchronized": False}
        self.unknown_percent_morning = 0.0
        self.unknown_percent_night = 0.0

    @abstractmethod
    def get_captures(self):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass
