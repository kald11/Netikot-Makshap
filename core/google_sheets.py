import time

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
        self.input_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["input_worksheet_name"])
        self.output_worksheet = spread_sheet.worksheet(self.config["google_sheets"]["output_worksheet_name"])

    def get_data(self):
        print("-------------- Fetch Data is starting -------------------")
        start_time = time.perf_counter()
        columns_indexes = self._convert_column_names_to_indexes(self.config["google_sheets"]["desired_column_names"])
        columns = [self.input_worksheet.col_values(col) for col in columns_indexes]
        rows = columns_to_rows_array(columns)
        df = array_to_df(rows)
        sites = convert_to_sites_array(df)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"----------------------- Fetch Data ends in {execution_time:.6f} seconds ------------------------------")
        return sites

    def get_row(self, row_number):
        columns_indexes = self._convert_column_names_to_indexes(self.config["google_sheets"]["desired_column_names"])
        columns = [self.input_worksheet.col_values(col)[0] for col in columns_indexes]
        row_data = self.input_worksheet.row_values(row_number)
        row_data = [columns,[row_data[i-1] for i in columns_indexes]]
        df = array_to_df(row_data)
        return convert_to_sites_array(df)[0]

    def _convert_column_names_to_indexes(self, column_names):
        headers = self.input_worksheet.row_values(1)
        return [headers.index(name) + 1 for name in column_names if name in headers]

    def get_columns_values(self, columns_indexes):
        return [self.input_worksheet.col_values(col)[1:] for col in columns_indexes]

    def upload_data(self, data):
        start_cell = "A2"
        self.output_worksheet.update(start_cell, data)

