from config.settings import Config
import gspread
from utils.utils import columns_to_rows_array, array_to_df, convert_to_sites_array
from pathlib import Path


class GoogleSheets:

    def __init__(self):
        self.config = Config().get_config()
        self.connection = gspread.service_account(
            filename=self.config["google_sheets"]["service_account_path"])
        spread_sheet = self.connection.open(self.config["google_sheets"]["spreadsheet_name"])
        self.worksheet = spread_sheet.worksheet(self.config["google_sheets"]["worksheet_name"])

    def get_data(self):
        columns_indexes = self.convert_column_names_to_indexes(self.config["google_sheets"]["desired_column_names"])
        columns = [self.worksheet.col_values(col) for col in columns_indexes]
        rows = columns_to_rows_array(columns)
        df = array_to_df(rows)
        return convert_to_sites_array(df)

    def convert_column_names_to_indexes(self, column_names):
        headers = self.worksheet.row_values(1)
        return [headers.index(name)+1 for name in column_names if name in headers]

    def get_columns_values(self, columns_indexes):
        return [self.worksheet.col_values(col)[1:] for col in columns_indexes]


