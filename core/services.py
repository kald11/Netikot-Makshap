import time

from utils.utils import use_thread, get_results_array


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

        results = get_results_array(self.cameras_array)
        end = time.perf_counter()
        execution_time = end - start
        print(f"----------------------- Fetch Data ends in {execution_time:.6f} seconds ------------------------------")
        return results

    def get_camera_data(self):
        def worker(camera):
            camera.get_captures()
            camera.get_current_time()

        use_thread(self.cameras_array, worker)
