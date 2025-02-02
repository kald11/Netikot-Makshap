from core.google_sheets import GoogleSheets

gs = GoogleSheets()
site = gs.get_row(479)
site.flags["is_nvr_ping"] = True

site.try_login()
site.get_captures()



