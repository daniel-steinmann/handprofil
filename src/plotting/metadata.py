import pandas as pd

import common


def join_attributes_to_measurements(
    binned_data: pd.Series, plot_attributes=pd.DataFrame
) -> pd.DataFrame:

    binned_data.name = "value"
    return pd.merge(
        plot_attributes, binned_data, "inner", left_on="id", right_index=True
    )
