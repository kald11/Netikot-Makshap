from core.google_sheets import GoogleSheets


gs = GoogleSheets()
site = gs.get_row(4)
site.ping_nvr()
site.try_login(type="nvr")
site.ping_camera()
site.try_login(type="camera")

# site.flags["is_nvr_ping"] = site.ping_nvr()
# site.flags["is_camera_ping"] = site.ping_camera()
# site.flags["login_ok"] = site.try_login("nvr")
# site.flags["login_camera_ok"] = site.try_login("camera")

# site.get_device_info()
site.get_captures()
# site.get_camera_time("camera")
# site.get_camera_time("nvr")
# site.check_unknowns("morning")
# site.check_unknowns("night")

