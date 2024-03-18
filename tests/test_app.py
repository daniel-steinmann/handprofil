import pytest
from handprofil import summation, return_wagner_decile, load_plot_section_config


def test_summation():
    """
    Testing Summation function
    """
    assert summation(2, 10) == 12
    assert summation(3, 5) == 8
    assert summation(4, 6) == 10


@pytest.mark.parametrize(
    "value, expected",
    [(12, 3), (12.5, 4), (12.7, 5), (13, 6), (20, 19)],
)
def test_return_wagner_decile(value, expected):
    """
    Testing decile function
    """

    bin_edges = [11, 12.5, 13, 14, 15.3, 16, 17, 18, 19]

    result = return_wagner_decile(bin_edges, value)
    assert result == expected


def test_load_plot_section_config():

    section = load_plot_section_config()

    assert isinstance(section, list)
