from config.settings import Config

class SiteTest:
    def __init__(
        self,
        check_time,
        nvr_time,
        camera_time,
        unknowns_night,
        unknowns_morning,
        error_reason,
        playback,
        num_captures,
        overall_ping,
        ping_nvr,
        ping_camera,
        company,
        camera_id,
        camera_number,
        ip_address,
        site_name,
        brigade,
        latitude,
        longitude,
        modem_status,
        example_picture,
        ftp2,
        ftp1,
        problems,
        proper,
        model_nvr,
        nvr_time_sync
    ):
        self.check_time = check_time
        self.nvr_time = nvr_time
        self.camera_time = camera_time
        self.unknowns_night = unknowns_night
        self.unknowns_morning = unknowns_morning
        self.error_reason = error_reason
        self.playback = playback
        self.num_captures = num_captures
        self.overall_ping = overall_ping
        self.ping_nvr = ping_nvr
        self.ping_camera = ping_camera
        self.company = company
        self.camera_id = camera_id
        self.camera_number = camera_number
        self.ip_address = ip_address
        self.site_name = site_name
        self.brigade = brigade
        self.latitude = latitude
        self.longitude = longitude
        self.modem_status = modem_status
        self.example_picture = example_picture
        self.ftp2 = ftp2
        self.ftp1 = ftp1
        self.problems = problems
        self.proper = proper
        self.model_nvr = model_nvr
        self.nvr_time_sync = nvr_time_sync

    def to_dict(self):
        return {
            "check_time": self.check_time,
            "nvr_time": self.nvr_time,
            "camera_time": self.camera_time,
            "unknowns_night": self.unknowns_night,
            "unknowns_morning": self.unknowns_morning,
            "error_reason": self.error_reason,
            "playback": self.playback,
            "num_captures": self.num_captures,
            "overall_ping": self.overall_ping,
            "ping_nvr": self.ping_nvr,
            "ping_camera": self.ping_camera,
            "company": self.company,
            "camera_id": self.camera_id,
            "camera_number": self.camera_number,
            "ip_address": self.ip_address,
            "site_name": self.site_name,
            "brigade": self.brigade,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "modem_status": self.modem_status,
            "example_picture": self.example_picture,
            "ftp2": self.ftp2,
            "ftp1": self.ftp1,
            "problems": self.problems,
            "proper": self.proper,
            "model_nvr": self.model_nvr,
            "nvr_time_sync": self.nvr_time_sync,
        }

