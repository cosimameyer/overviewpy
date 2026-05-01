import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na, overview_summary, overview_plot



def test_overview_tab():
    """Tests output values and shape of overview_tab."""
    data = {
        'id_column': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'BEL', 'ARG'],
        'time': [2022, 2023, 2021, 2023, 2020, 2019, 2015, 2014, 2013, 2013, 2002],
    }
    df = pd.DataFrame(data)

    result = overview_tab(df, 'id_column', 'time')

    expected_ids = ['ARG', 'BEL', 'FRA', 'GAB', 'RWA']
    expected_frames = ['2002', '2013-2014', '2015, 2019', '2020, 2023', '2021-2023']

    assert result['id_column'].tolist() == expected_ids
    assert result['time_frame'].tolist() == expected_frames


def test_overview_tab_drops_na_in_time():
    """overview_tab drops rows where the time variable is NA and warns the user."""
    data = {
        'id_column': ['RWA', 'RWA', 'GAB', 'GAB'],
        'time': [2022, np.nan, 2020, 2021],
    }
    df = pd.DataFrame(data)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = overview_tab(df, 'id_column', 'time')

    assert result.shape == (2, 2)
    assert 'RWA' in result['id_column'].values
    assert any("time variable" in str(w.message) for w in caught)


def test_overview_tab_drops_na_in_id():
    """overview_tab drops rows where the id variable is NA and warns the user."""
    data = {
        'id_column': ['RWA', np.nan, 'GAB'],
        'time': [2022, 2021, 2020],
    }
    df = pd.DataFrame(data)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = overview_tab(df, 'id_column', 'time')

    assert result.shape == (2, 2)
    assert any("id variable" in str(w.message) for w in caught)


def _make_na_df():
    return pd.DataFrame({
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan, np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, 2019, np.nan, 2015, 2014, 2013, 2002],
    })


def test_overview_na_default():
    """Column-wise percentage plot (default behaviour)."""
    df_na = _make_na_df()
    fig = overview_na(df_na, show_plot=False).containers[0]
    assert isinstance(fig, matplotlib.container.BarContainer)
    assert len(fig.datavalues) == len(df_na.columns)


def test_overview_na_absolute():
    """Column-wise absolute count plot."""
    df_na = _make_na_df()
    ax = overview_na(df_na, show_plot=False, perc=False)
    assert ax.get_xlabel() == "Number of NA (total)"
    assert len(ax.containers[0].datavalues) == len(df_na.columns)


def test_overview_na_perc_xaxis():
    """Column-wise percentage plot has correct x-axis label."""
    df_na = _make_na_df()
    ax = overview_na(df_na, show_plot=False, perc=True)
    assert ax.get_xlabel() == "Number of NA (in %)"


def test_overview_na_yaxis_label():
    """Custom y-axis label is applied."""
    df_na = _make_na_df()
    ax = overview_na(df_na, show_plot=False, yaxis="My Variables")
    assert ax.get_ylabel() == "My Variables"


def test_overview_na_row_wise_plot():
    """Row-wise plot has one bar per row and y-axis label 'Observations'."""
    df_na = _make_na_df()
    ax = overview_na(df_na, show_plot=False, row_wise=True)
    assert ax.get_ylabel() == "Observations"
    assert len(ax.containers[0].datavalues) == len(df_na)


def test_overview_na_row_wise_absolute():
    """Row-wise absolute plot has correct x-axis label."""
    df_na = _make_na_df()
    ax = overview_na(df_na, show_plot=False, row_wise=True, perc=False)
    assert ax.get_xlabel() == "Number of NA (total)"


def test_overview_na_add():
    """add=True returns original DataFrame extended with na_count and percentage."""
    df_na = _make_na_df()
    result = overview_na(df_na, row_wise=True, add=True)
    assert isinstance(result, pd.DataFrame)
    assert "na_count" in result.columns
    assert "percentage" in result.columns
    assert len(result) == len(df_na)
    # row 3 (index 3): id=NaN, year=2023 → 1 NA out of 2 columns → 50 %
    assert result["na_count"].iloc[3] == 1
    assert result["percentage"].iloc[3] == 50.0


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
