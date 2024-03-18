import pytest
from handprofil import load_plot_section_config


def test_load_plot_section_config():

    section = load_plot_section_config()

    assert isinstance(section, list)
