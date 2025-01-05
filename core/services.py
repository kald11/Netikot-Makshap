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
        def worker(camera):
            camera.get_captures()
            camera.get_current_time()

        use_thread(self.cameras_array, worker)
        
