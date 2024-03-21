from handprofil.utils import (
    load_attributes,
    load_background,
    load_meta_attributes,
    load_plot_section_config
)


def test_load_attributes():
    # Arrange
    # Act
    df = load_attributes()


def test_load_meta_attributes():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_meta_attributes()


def test_load_background():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_background()


def test_load_plot_section_config():

    section = load_plot_section_config()
