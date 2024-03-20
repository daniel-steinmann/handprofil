import pandas as pd
from handprofil.frontend import (
    split_reorder_plot_df_to_sections
)
from handprofil.utils import (
    load_plot_section_config
)


def test_split_plot_df_to_sections():
    input = pd.DataFrame(
        data={"values": [1, 1, 1, 1, 1, 1, 1]}, index=[1, 3, 21, 24, 39, 47, 81]
    )
    config = load_plot_section_config()
    output = split_reorder_plot_df_to_sections(input, config)

    assert len(output) == len(config)
    assert equal(output[0].index, [0, 1, 2])
    assert equal(output[0].id, [1, 3, 24])
    assert equal(output[1].id, [39])
    assert equal(output[2].id, [81, 21, 47])


def test_load_plot_section_config():
    config = load_plot_section_config()
    assert len(config) == 3


def equal(list_a: list, list_b: list) -> bool:
    if not len(list_a) == len(list_b):
        return False
    for index, item in enumerate(list_a):
        if item != list_b[index]:
            return False

    return True
