import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Index, SeriesSchema

import common

values_schema = SeriesSchema(
    int,
    index=Index(int)
)

attributes_schema = DataFrameSchema({
    "id": Column(int),
    "device": Column(str),
    "hand": Column(str),
    "description": Column(str),
    "unit": Column(str)
},
    index=Index(int))

data_and_attributes_schema = DataFrameSchema({
    "id": Column(int),
    "device": Column(str),
    "hand": Column(str),
    "description": Column(str),
    "unit": Column(str),
    "value": Column(int)
},
    index=Index(int))


@pa.check_io(binned_data=values_schema, plot_attributes=attributes_schema, out=data_and_attributes_schema)
def join_attributes_to_measurements(
    binned_data: pd.Series, plot_attributes=pd.DataFrame
) -> pd.DataFrame:

    binned_data.name = "value"
    return pd.merge(
        plot_attributes, binned_data, "inner", left_on="id", right_index=True
    )
