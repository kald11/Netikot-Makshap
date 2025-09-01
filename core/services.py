import time
from core.classes.networkComponents.Modem import try_login_modem_worker
from utils.parse_site import get_results_array, get_daily_results
from utils.utils import use_thread, build_index_map


class NetikotService:

    def __init__(self, cameras_array):
        self.cameras_array = cameras_array

    def ping(self):

        def worker(camera):
            camera.ping_camera()
            camera.ping_nvr()

        use_thread(self.cameras_array, worker)

    def get_camera_data(self, type=None):
        self.get_captures(type=type)
        self._get_camera_time()
        self._get_ftp_data()
        self.get_playback()

    def _get_ftp_data(self):
        def worker(camera):
            if camera.flags["login_ok"] and camera.company_name == "Hikvision":
                camera.ftp_status()

        use_thread(self.cameras_array, worker)

    def unknowns(self):
        def worker(camera):
            if camera.flags[
                "login_ok"] and camera.site.camera_id != "אווירה" and camera.site.camera_type != "נתיקות -טרמי" \
                    and camera.site.camera_type != "PTZ טרמי - נתיקות":
                camera.check_unknowns("morning")
                camera.check_unknowns("night")

        use_thread(self.cameras_array, worker)

    def login_cameras(self):
        def worker(camera):
            if camera.flags["is_nvr_ping"]:
                camera.try_login(type='nvr')
            if camera.flags["is_camera_ping"]:
                camera.try_login(type='camera')

        use_thread(self.cameras_array, worker)

    def live_view(self):
        def worker(camera):
            if camera.flags["is_nvr_ping"]:
                camera.check_live()

        use_thread(self.cameras_array, worker)

    def get_playback(self):
        sites_dict = self.get_connected_cameras_playback()
        self._assign_playback_channels(self.cameras_array, sites_dict)

        def worker(camera):
            if camera.flags["is_nvr_ping"] and camera.flags["login_ok"]:
                camera.check_playback()

        use_thread(self.cameras_array, worker)

    def get_connected_cameras_playback(self):
        ip_port_to_playback_cameras = {}

        def worker(camera):
            key = (camera.site.ip, camera.site.nvr.port)
            if camera.flags["is_nvr_ping"] and camera.company_name == "Hikvision" and key not in ip_port_to_playback_cameras:
                camera_playback = camera.check_amount_cameras_playback()
                ip_port_to_playback_cameras[key] = camera_playback

        use_thread(self.cameras_array, worker)
        return ip_port_to_playback_cameras

    def get_results(self):
        return get_results_array(self.cameras_array)

    def get_daily_results(self):
        return get_daily_results(self.cameras_array)

    def get_captures(self, type=None):
        def worker(camera):
            if camera.site.camera_id != "אווירה" and camera.site.camera_type != "נתיקות -טרמי" \
                    and camera.site.camera_type != "PTZ טרמי - נתיקות":
                camera.get_captures(type)

        use_thread(self.cameras_array, worker)

    def _get_camera_time(self):
        def worker(camera):
            camera.get_camera_time(type="nvr")
            camera.get_camera_time(type="camera")

        use_thread(self.cameras_array, worker)

    def _get_unknowns(self):
        def worker(camera):
            if camera.flags["login_ok"] and camera.site.camera_id != "אווירה":
                camera.check_unknowns("morning")
                camera.check_unknowns("night")

        use_thread(self.cameras_array, worker)

    def get_cameras_connected(self):
        def worker(camera):
            if camera.flags["login_ok"] and camera.site.camera_id != "אווירה" and camera.company_name == "hikvision":
                camera.check_amount_cameras_playback()

        use_thread(self.cameras_array, worker)

    def _assign_playback_channels(self, cameras, site_dict):
        grouped = self._group_cameras_by_site(cameras)

        for site_key, cam_list in grouped.items():
            index_list = site_dict.get(site_key, [])
            # if site_key[0] == '46.210.114.58':
            # x = 1
            if index_list is None:
                continue
            index_map = build_index_map(index_list)
            self._set_playback_channels_by_number(cam_list, index_map)

    def _group_cameras_by_site(self, cameras):
        grouped = {}
        for cam in cameras:
            if cam.company_name == "Hikvision":
                key = (cam.site.ip, cam.site.nvr.port)
                grouped.setdefault(key, []).append(cam)
        return grouped

    def _set_playback_channels_by_number(self, cams, index_map):
        for cam in cams:
            cam.playback_channel = index_map.get(int(cam.site.camera.number), 1)

    def modem_test(self):
        use_thread(self.cameras_array, try_login_modem_worker)

