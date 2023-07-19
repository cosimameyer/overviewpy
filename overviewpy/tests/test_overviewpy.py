import pandas as pd
from overviewpy.overviewpy import overview_tab

data = {
    'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG'],
    'time': [2022, 2023, 2021, 2023, 2020, 2019, 2015, 2014, 2013, 2002]
}

df = pd.DataFrame(data)

expected = {
    'id': ['ARG', 'BEL', 'FRA', 'FRA', 'GAB', 'GAB', 'RWA'],
    'time': ['2002', '2013-2014', '2015', '2019', '2020', '2023', '2021-2023']
}

df_expected = pd.DataFrame(expected)

df_actual = overview_tab(df, 'id', 'time')

assert df_actual.shape == df_expected.shape, "DataFrame does not match the expected shape"
