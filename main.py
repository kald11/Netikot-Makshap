from core.google_sheets import GoogleSheets
from core.services import NetikotService
def main():
    camera_array = GoogleSheets().get_data()
    service = NetikotService(camera_array)
    service.ping_cameras()
    service.get_camera_data()



if __name__ == "__main__":
    main()
