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

    # Assert
    assert df.index.name == "id"
    assert len(df.columns) == 4


def test_load_meta_attributes():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_meta_attributes()

    # Assert
    assert df.index.name == "id"
    assert len(df.columns) == 1


def test_load_background():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_background()

    # Assert
    assert len(df.columns) == 13


def test_load_plot_section_config():

    section = load_plot_section_config()

    assert isinstance(section, list)
