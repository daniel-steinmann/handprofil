import pandas as pd

import common

def return_decile_plot_df(binned_data: pd.DataFrame) -> pd.DataFrame:
    attributes = common.load_attributes()
    return pd.merge(attributes, binned_data, "inner", left_on="id", right_index=True)
