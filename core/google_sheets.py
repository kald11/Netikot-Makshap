import time
from datetime import datetime

from config.settings import Config
import gspread
from utils.utils import columns_to_rows_array, array_to_df
from utils.parse_site import convert_to_sites_array
import os


class GoogleSheets:

    def __init__(self):
        self.config = Config().get_config()
        # Resolve the service account path dynamically
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        service_account_path = os.path.join(base_dir, self.config["google_sheets"]["service_account_path"])
        connection = gspread.service_account(
            filename=service_account_path)
        spread_sheet = connection.open(self.config["google_sheets"]["spreadsheet_name"])
        self.input_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["input"]["worksheet_name"])
        self.output_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["output"]["worksheet_name"])

    def get_data(self):

        columns_indexes = self._convert_column_names_to_indexes(self.input_worksheet,
                                                                self.config["google_sheets"]["input"][
                                                                    "desired_column_names"])
        columns = [self.input_worksheet.col_values(col) for col in columns_indexes]
        rows = columns_to_rows_array(columns)
        df = array_to_df(rows)
        sites = convert_to_sites_array(df)
        self.append_previous_unknowns(sites)
        return sites

    def get_row(self, row_number):
        columns_indexes = self._convert_column_names_to_indexes(self.config["google_sheets"]["desired_column_names"])
        columns = [self.input_worksheet.col_values(col)[0] for col in columns_indexes]
        row_data = self.input_worksheet.row_values(row_number)
        row_data = [columns, [row_data[i - 1] for i in columns_indexes]]
        df = array_to_df(row_data)
        return convert_to_sites_array(df)[0]

    def _convert_column_names_to_indexes(self, worksheet, column_names):
        headers = worksheet.row_values(1)
        return [headers.index(name) + 1 for name in column_names if name in headers]

    def get_columns_values(self, columns_indexes):
        return [self.input_worksheet.col_values(col)[1:] for col in columns_indexes]

    def upload_data(self, data, start_time):
        start_cell = "A2"
        # self.output_worksheet.update(start_cell, data)
        end_time = datetime.now()
        time_difference = str(end_time - datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")).split(".")[0]
        self.output_worksheet.update("P2:R2", [[start_time, end_time.strftime("%Y-%m-%d %H:%M:%S"), time_difference]])

    def append_previous_unknowns(self, devices):
        columns_indexes = self._convert_column_names_to_indexes(self.output_worksheet,
                                                                self.config["google_sheets"]["output"][
                                                                    "desired_column_names"])
        ids, unknowns_morning, unknowns_evening = (
            self.output_worksheet.col_values(col)[1:] for col in columns_indexes
        )
        for index, camera_id in enumerate(ids):
            for device in devices:
                if device.site.camera_id == "אווירה":
                    break
                elif camera_id == device.site.camera_id:
                    device.unknowns["morning"] = unknowns_morning[index]
                    device.unknowns["night"] = unknowns_evening[index]
                    break
