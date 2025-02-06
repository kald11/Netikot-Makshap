import time

from utils.parse_site import get_results_array
from utils.utils import use_thread


class NetikotService:

    def __init__(self, cameras_array):
        self.cameras_array = cameras_array

    def ping(self):

        def worker(camera):
            camera.ping_camera()
            camera.ping_nvr()

        use_thread(self.cameras_array, worker)

    def get_camera_data(self):
        self._get_captures()
        self._get_camera_time()

    def unknowns(self):

        def worker(camera):
            if camera.flags[
                "login_ok"] and camera.site.camera_id != "אווירה" and camera.site.camera_type != "נתיקות -טרמי" \
                    and camera.site.camera_type != "PTZ טרמי - נתיקות" and camera.company_name == "Hikvision":
                camera.check_unknowns("morning")
                camera.check_unknowns("night")

        use_thread(self.cameras_array, worker)

    def login_cameras(self):
        def worker(camera):
            if camera.flags["is_nvr_ping"]:
                camera.try_login()

        use_thread(self.cameras_array, worker)

    def get_results(self):
        return get_results_array(self.cameras_array)

    def _get_captures(self):
        def worker(camera):
            if camera.site.camera_id != "אווירה" and camera.site.camera_type != "נתיקות -טרמי" \
                    and camera.site.camera_type != "PTZ טרמי - נתיקות":
                camera.get_captures()

        use_thread(self.cameras_array, worker)

    def _get_camera_time(self):
        def worker(camera):
            if camera.flags["login_ok"]:
                camera.get_camera_time()

        use_thread(self.cameras_array, worker)

    def _get_unknowns(self):
        def worker(camera):
            if camera.flags["login_ok"] and camera.site.camera_id != "אווירה":
                camera.check_unknowns("morning")
                camera.check_unknowns("night")

        use_thread(self.cameras_array, worker)
