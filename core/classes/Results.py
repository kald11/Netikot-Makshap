class Results:
    def __init__(self, ):
        self.is_camera_ping = False
        self.is_nvr_ping = False
        self.is_captures = False
        self.num_captures = 0

    def get_results(self):
        return [self.is_camera_ping, self.is_nvr_ping, self.is_captures, self.num_captures]
