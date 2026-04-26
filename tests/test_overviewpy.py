import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na, overview_summary, overview_plot

matplotlib.use("Agg")


def test_overview_tab():
    """Tests shape of output of overview_tab"""
    data = {
        'id_column': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'BEL', 'ARG'],
        'time': [2022, 2023, 2021, 2023, 2020, 2019, 2015, 2014, 2013, 2013, 2002]
    }

    df = pd.DataFrame(data)

    expected = {
        'id_column': ['ARG', 'BEL', 'FRA', 'GAB', 'RWA'],
        'time': ['2002', '2013-2014', '2015, 2019', '2020, 2023', '2021-2023']
    }

    df_expected = pd.DataFrame(expected)

    df_actual = overview_tab(df, 'id_column', 'time')

    assert df_actual.shape == df_expected.shape, "DataFrame does not match the expected shape"


def test_overview_na():
    """Test plotting of missing values."""
    data_na = {
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan, np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, 2019, np.nan, 2015, 2014, 2013, 2002]
    }

    df_na = pd.DataFrame(data_na)

    fig = overview_na(df_na, show_plot=False).containers[0]
    assert isinstance(fig, matplotlib.container.BarContainer), "Wrong plot type"
    assert len(fig.datavalues) == len(df_na.columns), "Incorrect number of bars plotted"
    plt.close("all")


def test_overview_na_relative():
    """Test that relative=True produces percentage values between 0 and 100."""
    data_na = {
        'id': ['RWA', 'GAB', np.nan, np.nan],
        'year': [2022, 2023, np.nan, 2021],
    }
    df_na = pd.DataFrame(data_na)

    ax = overview_na(df_na, show_plot=False, relative=True)
    container = ax.containers[0]
    assert isinstance(container, matplotlib.container.BarContainer)
    for val in container.datavalues:
        assert 0.0 <= val <= 100.0, f"Percentage {val} out of range"
    assert ax.get_xlabel() == "Percentage (%)"
    plt.close("all")


def test_overview_summary():
    """Tests structure and content of overview_summary output."""
    data = {
        'id': ['RWA', 'GAB', np.nan],
        'year': [2022, 2023, 2021],
        'value': [1.0, np.nan, 3.0],
    }
    df = pd.DataFrame(data)
    result = overview_summary(df)

    assert list(result.index) == ['id', 'year', 'value'], "Index should be column names"
    assert list(result.columns) == ['non_null_count', 'unique_count', 'sample_values']
    assert result.loc['id', 'non_null_count'] == 2
    assert result.loc['year', 'unique_count'] == 3
    assert result.loc['value', 'non_null_count'] == 2


def test_overview_plot_returns_axes():
    """Test that overview_plot returns a matplotlib Axes object."""
    data = {
        'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA'],
        'year': [2020, 2021, 2022, 2020, 2021, 2019],
    }
    df = pd.DataFrame(data)
    ax = overview_plot(df, id='id', time='year', show_plot=False)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_overview_plot_axis_labels():
    """Test that axis labels are set correctly."""
    data = {
        'id': ['RWA', 'GAB'],
        'year': [2020, 2021],
    }
    df = pd.DataFrame(data)
    ax = overview_plot(df, id='id', time='year', xaxis="Year", yaxis="Country", show_plot=False)
    assert ax.get_xlabel() == "Year"
    assert ax.get_ylabel() == "Country"
    plt.close("all")


def test_overview_plot_drops_na():
    """Test that NaN values in id or time are excluded from the plot."""
    data = {
        'id': ['RWA', np.nan, 'GAB', 'FRA'],
        'year': [2020, 2021, np.nan, 2022],
    }
    df = pd.DataFrame(data)
    ax = overview_plot(df, id='id', time='year', show_plot=False)
    # Only 'RWA' (year=2020) and 'FRA' (year=2022) have valid id+time; 'GAB' has NaN time
    ytick_labels = [t.get_text() for t in ax.get_yticklabels()]
    assert 'RWA' in ytick_labels
    assert 'FRA' in ytick_labels
    assert 'GAB' not in ytick_labels
    plt.close("all")


def test_overview_plot_with_color():
    """Test that overview_plot works with the color parameter."""
    data = {
        'id': ['RWA', 'RWA', 'GAB', 'GAB'],
        'year': [2020, 2021, 2020, 2021],
        'regime': ['democracy', 'democracy', 'autocracy', 'autocracy'],
    }
    df = pd.DataFrame(data)
    ax = overview_plot(df, id='id', time='year', color='regime', show_plot=False)
    assert isinstance(ax, matplotlib.axes.Axes)
    # Legend should be present
    assert ax.get_legend() is not None
    plt.close("all")


def test_overview_plot_asc_order():
    """Test that asc=True inverts the y-axis relative to asc=False."""
    data = {
        'id': ['AAA', 'BBB', 'CCC'],
        'year': [2020, 2021, 2022],
    }
    df = pd.DataFrame(data)

    ax_asc = overview_plot(df, id='id', time='year', asc=True, show_plot=False)
    ax_desc = overview_plot(df, id='id', time='year', asc=False, show_plot=False)

    assert ax_asc.yaxis_inverted() != ax_desc.yaxis_inverted()
    plt.close("all")


def test_overview_plot_consecutive_segments():
    """Test that gaps in time produce separate visual segments (distinct scatter collections)."""
    data = {
        'id': ['RWA', 'RWA', 'RWA', 'RWA'],
        'year': [2000, 2001, 2005, 2006],  # gap between 2001 and 2005
    }
    df = pd.DataFrame(data)
    ax = overview_plot(df, id='id', time='year', show_plot=False)
    # Two consecutive segments → two scatter PathCollections and two Line2D segments
    scatter_collections = [c for c in ax.collections if hasattr(c, 'get_offsets')]
    assert len(scatter_collections) == 2, "Expected 2 scatter segments for a gap in time"
    plt.close("all")
