import pandas as pd
import common


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


def get_bin_edges(instrument: str, sex: str, hand: str) -> pd.DataFrame:

    background = common.load_background()
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


def get_calculated_values(
    input: pd.Series, instrument: str, sex: str, hand: str
) -> pd.DataFrame:

    bin_edges = get_bin_edges(instrument, sex, hand)

    output = pd.DataFrame()
    for index, measurement in input.items():
        if index in bin_edges.index:
            bin = return_wagner_decile(bin_edges.loc[index], measurement)
            output.loc[index, "bin"] = bin

    if not output.empty:
        output["bin"] = output["bin"].astype(int)

    return output
