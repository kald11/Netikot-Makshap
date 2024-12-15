import pandas as pd


# ----------------------- Arrays and df functions -----------------------
def columns_to_rows_array(columns):
    return [list(row) for row in zip(*columns)]


def array_to_df(data):
    return pd.DataFrame(data[1:], columns=data[0])
