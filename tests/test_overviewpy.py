import warnings
import matplotlib
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na, overview_summary


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


def test_overview_na():
    """Test plotting of missing values."""
    data_na = {
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan,  np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, 2019,  np.nan, 2015, 2014, 2013, 2002]
    }

    df_na = pd.DataFrame(data_na)

    # Grab the first container instance from the returned matplotlib.Axes object and run assertions on it.
    fig = overview_na(df_na, show_plot=False).containers[0]
    assert isinstance(fig, matplotlib.container.BarContainer), \
           "Wrong plot type"
    assert len(fig.datavalues) == len(df_na.columns), \
        "Incorrect number of bars plotted"


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
