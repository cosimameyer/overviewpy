import matplotlib
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na

def test_overview_tab():
    """Tests shape of output of overview_tab"""
    data = {
        'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG'],
        'time': [2022, 2023, 2021, 2023, 2020, 2019, 2015, 2014, 2013, 2002]
    }

    df = pd.DataFrame(data)

    expected = {
        'id': ['ARG', 'BEL', 'FRA', 'GAB', 'RWA'],
        'time': ['2002', '2013-2014', '2015, 2019', '2020, 2023', '2021-2023']
    }
    
    df_expected = pd.DataFrame(expected)

    df_actual = overview_tab(df, 'id', 'time')

    assert df_actual.shape == df_expected.shape, "DataFrame does not match the expected shape"
    

def test_overview_na():
    """Test plotting of missing values."""
    data_na = {
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan,  np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, 2019,  np.nan, 2015, 2014, 2013, 2002]
    }

    df_na = pd.DataFrame(data_na)

    # Grab the first container instance from the returned matplotlib.Axes object and run assertions on it.
    fig = overview_na(df_na).containers[0]
    assert isinstance(fig, matplotlib.container.BarContainer), \
           "Wrong plot type"
    assert len(fig.datavalues) == len(df_na.columns), \
        "Incorrect number of bars plotted"
