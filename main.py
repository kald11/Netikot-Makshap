from core.google_sheets import GoogleSheets
from core.services import NetikotService

gs = GoogleSheets()
camera_array = gs.get_data()
service = NetikotService(camera_array)
service.ping()
service.login_cameras()


def main_captures():
    service.get_camera_data()


def main_unknowns_check():
    service.unknowns()


if __name__ == "__main__":
    main_unknowns_check()
    main_captures()
    results_array = service.get_results()
    gs.upload_data(data=results_array)
