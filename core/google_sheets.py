import sys
import time
from datetime import datetime

from config.settings import Config
import gspread
from utils.utils import columns_to_rows_array, array_to_df
from utils.parse_site import convert_to_sites_array, convert_to_sites_array_test
import os


class GoogleSheets:

    def __init__(self):
        self.config = Config().get_config()
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        service_account_path = os.path.join(base_dir,
                                            self.config["google_sheets"]["service_account_path"])
        connection = gspread.service_account(
            filename=service_account_path)
        spread_sheet = connection.open(self.config["google_sheets"]["spreadsheet_name"])
        self.input_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["input"]["worksheet_name"])
        self.input_worksheet_test = spread_sheet.worksheet(self.config["google_sheets"]["input"]["worksheet_name_test"])
        self.output_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["output"]["worksheet_name"])
        self.output_worksheet_test = spread_sheet.worksheet(self.config["google_sheets"]["output"]["worksheet_name_test"])
        self.daily_worksheet = spread_sheet.worksheet("הרכשות יומי")
        self.modem_worksheet = spread_sheet.worksheet("modem")

    def get_data(self):
        col_names = self.config["google_sheets"]["input"]["desired_column_names"]
        columns = (
                [self.input_worksheet.col_values(i) for i in
                 self._convert_column_names_to_indexes(self.input_worksheet, col_names)]
                + [self.output_worksheet.col_values(i) for i in
                   self._convert_column_names_to_indexes(self.output_worksheet, col_names[-2:])]
        )
        rows = columns_to_rows_array(columns)
        df = array_to_df(rows)
        sites = convert_to_sites_array(df)
        # self.append_previous_unknowns(sites)
        return sites

    def get_data_test(self):
        col_names = self.config["google_sheets"]["input"]["desired_column_names_test"]
        columns = (
                [self.input_worksheet_test.col_values(i) for i in
                 self._convert_column_names_to_indexes(self.input_worksheet_test, col_names)]
                + [self.output_worksheet_test.col_values(i) for i in
                   self._convert_column_names_to_indexes(self.output_worksheet_test, col_names[-2:])]
        )
        rows = columns_to_rows_array(columns)
        df = array_to_df(rows)
        sites = convert_to_sites_array_test(df)
        return sites

    def get_modem_data(self):
        col_names = self.config["google_sheets"]["input"]["modem_columns"]
        columns = ([self.modem_worksheet.col_values(i) for i in
                 self._convert_column_names_to_indexes(self.modem_worksheet, col_names)])
        rows = columns_to_rows_array(columns)
        return array_to_df(rows)


    def get_row(self, row_number):
        columns_indexes = self._convert_column_names_to_indexes(self.input_worksheet,
                                                                self.config["google_sheets"]["input"][
                                                                    "desired_column_names"])
        columns = [self.input_worksheet.col_values(col)[0] for col in columns_indexes]
        row_data = self.input_worksheet.row_values(row_number)
        row_data = [columns, [row_data[i - 1] for i in columns_indexes]]
        df = array_to_df(row_data)
        return convert_to_sites_array(df)[0]

    def get_ptz_array(self):
        arr = self.get_data()
        return [item for item in arr if item.site.camera_id != "אווירה"]

    def _convert_column_names_to_indexes(self, worksheet, column_names):
        headers = worksheet.row_values(1)
        return [headers.index(name) + 1 for name in column_names if name in headers]

    def get_columns_values(self, columns_indexes):
        return [self.input_worksheet.col_values(col)[1:] for col in columns_indexes]

    def upload_data(self, data, start_time):
        start_cell = "A2"
        self.output_worksheet.update(start_cell, data)
        end_time = datetime.now()
        time_difference = \
            str(end_time - datetime.strptime(start_time, self.config["project_setup"]["format_datetime"])).split(".")[0]
        self.output_worksheet.update("AE2:AG2", [
            [start_time, end_time.strftime(self.config["project_setup"]["format_datetime"]), time_difference]])

    def upload_data_test(self, data, start_time):
        start_cell = "A2"
        self.output_worksheet_test.update(start_cell, data)
        end_time = datetime.now()
        time_difference = \
            str(end_time - datetime.strptime(start_time, self.config["project_setup"]["format_datetime"])).split(".")[0]
        self.output_worksheet_test.update("AE2:AG2", [
            [start_time, end_time.strftime(self.config["project_setup"]["format_datetime"]), time_difference]])

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

    def upload_daily_data(self, data):
        start_cell = "A2"
        self.daily_worksheet.update(start_cell, data)
