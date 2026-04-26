import matplotlib
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na, overview_summary

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
