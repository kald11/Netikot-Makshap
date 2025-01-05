from utils.utils import use_thread


class NetikotService:

    def __init__(self, cameras_array):
        self.cameras_array = cameras_array

    def ping_cameras(self):
        def worker(camera):
            is_camera_ping = camera.ping_camera()
            is_nvr_ping = camera.ping_nvr()

            camera.is_camera_ping = is_camera_ping
            camera.is_nvr_ping = is_nvr_ping

        use_thread(self.cameras_array, worker)

    def get_camera_data(self):
        def worker(camera):
            camera.get_captures()
            camera.get_current_time()

        use_thread(self.cameras_array, worker)
        
