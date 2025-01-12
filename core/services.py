import time

from utils.parse_site import get_results_array
from utils.utils import use_thread


class NetikotService:

    def __init__(self, cameras_array):
        self.cameras_array = cameras_array

    def ping(self):
        print("-------------- Ping is starting -------------------")
        start = time.perf_counter()

        def worker(camera):
            camera.ping_camera()
            camera.ping_nvr()

        use_thread(self.cameras_array, worker)

        end = time.perf_counter()
        execution_time = end - start
        print(f"----------------------- Ping sites ends in {execution_time:.6f} seconds ------------------------------")

    def get_camera_data(self):
        self._login_cameras()
        self._get_captures()
        self._get_camera_time()

    def _login_cameras(self):
        def worker(camera):
            if camera.flags["is_nvr_ping"]:
                camera.try_login()

        use_thread(self.cameras_array, worker)

    def get_results(self):
        return get_results_array(self.cameras_array)

    def _get_captures(self):
        def worker(camera):
            if camera.flags["login_ok"]:
                camera.get_captures()

        use_thread(self.cameras_array, worker)

    def _get_camera_time(self):
        def worker(camera):
            if camera.flags["login_ok"]:
                camera.get_camera_time()

        use_thread(self.cameras_array, worker)
