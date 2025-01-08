from core.google_sheets import GoogleSheets
from core.services import NetikotService

gs = GoogleSheets()


def main():
    camera_array = gs.get_data()
    service = NetikotService(camera_array)
    service.ping()
    service.get_camera_data()
    results_array = service.get_results()
    gs.upload_data(data=results_array)


if __name__ == "__main__":
    main()
