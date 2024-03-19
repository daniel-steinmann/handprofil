import pandas as pd
import common
import pandera as pa
from pandera import Column, Index, DataFrameSchema, SeriesSchema

background_schema = DataFrameSchema({
    "instrument": Column(str),
    "sex": Column(str),
    "hand": Column(str),
    "id": Column(int),
    "bin_edge_1": Column(float),
    "bin_edge_2": Column(float),
    "bin_edge_3": Column(float),
    "bin_edge_4": Column(float),
    "bin_edge_5": Column(float),
    "bin_edge_6": Column(float),
    "bin_edge_7": Column(float),
    "bin_edge_8": Column(float),
    "bin_edge_9": Column(float),
},
    index=Index(int))

bin_edges_schema = DataFrameSchema({
    "bin_edge_1": Column(float),
    "bin_edge_2": Column(float),
    "bin_edge_3": Column(float),
    "bin_edge_4": Column(float),
    "bin_edge_5": Column(float),
    "bin_edge_6": Column(float),
    "bin_edge_7": Column(float),
    "bin_edge_8": Column(float),
    "bin_edge_9": Column(float),
},
    index=Index(int))  # Id is in Index


@pa.check_input(background_schema, "background")
@pa.check_output(bin_edges_schema)
def get_bin_edges(
    instrument: str, sex: str, hand: str, background: pd.DataFrame
) -> pd.DataFrame:

    assert instrument in background["instrument"].unique()
    assert hand in background["hand"].unique()
    assert sex in background["sex"].unique()

    background_filtered = background.query(
        "instrument == @instrument & sex == @sex & hand == @hand"
    ).set_index("id", drop=True)

    bin_edges = background_filtered[
        [
            "bin_edge_1",
            "bin_edge_2",
            "bin_edge_3",
            "bin_edge_4",
            "bin_edge_5",
            "bin_edge_6",
            "bin_edge_7",
            "bin_edge_8",
            "bin_edge_9",
        ]
    ]

    return bin_edges


measurement_schema = SeriesSchema(
    float,
    index=Index(int)
)

bin_schema = SeriesSchema(
    int,
    index=Index(int)
)


# @pa.check_io(measurements=measurement_schema, bin_edges=bin_edges_schema, out=bin_schema)
def measurements_to_bins(measurements: pd.Series, bin_edges: pd.DataFrame) -> pd.Series:

    output = pd.Series(dtype=pd.Int64Dtype)
    for index, measurement in measurements.items():
        if index in bin_edges.index:
            bin = return_wagner_decile(bin_edges.loc[index], measurement)
            output.loc[index] = bin

    return output


def return_wagner_decile(bin_edges: list, value: float) -> int:
    """Return custom decile bin.

    Returns bin position of value with respect to
    bin_edges. If value is equal to one of the bin
    edges, this is also a bin. Below the mapping between
    bins and edges (with monospace font):
    Edges:   1   2   3   4   5     6     7     8     9
    Bins:  1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
    """
    #   1   2   3   4   5     6     7     8     9
    # 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19

    assert len(bin_edges) == 9

    bin = 1
    for i, edge in enumerate(bin_edges):
        if value < edge:
            break
        if value == edge:
            bin = bin + 1
            break
        else:
            bin = bin + 2
    return bin
