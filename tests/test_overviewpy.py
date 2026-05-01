import warnings
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from overviewpy.overviewpy import overview_tab, overview_na, overview_summary, overview_plot, overview_overlap, overview_heat, overview_crossplot, overview_latex

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


def test_overview_heat_returns_axes():
    """Test that overview_heat returns a matplotlib Axes object."""
    data = {
        'id': ['RWA', 'RWA', 'GAB', 'GAB', 'FRA'],
        'year': [2020, 2021, 2020, 2021, 2020],
    }
    df = pd.DataFrame(data)
    ax = overview_heat(df, 'id', 'year', show_plot=False)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close('all')


def test_overview_heat_absolute_counts():
    """Test cell values reflect absolute observation counts."""
    data = {
        'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB'],
        'year': [2020, 2020, 2021, 2020, 2021],
    }
    df = pd.DataFrame(data)
    ax = overview_heat(df, 'id', 'year', show_plot=False)
    # Extract the image data from imshow
    img = ax.images[0]
    data_array = img.get_array()
    # pivot is sorted by id: GAB row 0, RWA row 1; cols sorted: 2020, 2021
    assert data_array[0, 0] == 1  # GAB/2020
    assert data_array[0, 1] == 1  # GAB/2021
    assert data_array[1, 0] == 2  # RWA/2020
    assert data_array[1, 1] == 1  # RWA/2021
    plt.close('all')


def test_overview_heat_percentage():
    """Test cell values are percentages when perc=True."""
    data = {
        'id': ['RWA', 'RWA', 'GAB'],
        'year': [2020, 2021, 2020],
    }
    df = pd.DataFrame(data)
    ax = overview_heat(df, 'id', 'year', perc=True, exp_total=2, show_plot=False)
    img = ax.images[0]
    data_array = img.get_array()
    # GAB/2020 = 1/2*100 = 50.0
    assert data_array[0, 0] == pytest.approx(50.0)
    plt.close('all')


def test_overview_heat_perc_requires_exp_total():
    """Test that perc=True without exp_total raises ValueError."""
    df = pd.DataFrame({'id': ['A'], 'year': [2020]})
    with pytest.raises(ValueError, match="exp_total"):
        overview_heat(df, 'id', 'year', perc=True, show_plot=False)


def test_overview_crossplot():
    """Test that overview_crossplot returns an Axes with a scatter and two threshold lines."""
    data = {
        'id': ['A', 'A', 'B', 'B', 'C'],
        'year': [2000, 2001, 2000, 2001, 2000],
        'gdp': [10000, 30000, 20000, 50000, 5000],
        'population': [100, 200, 300, 250, 150],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'population', 25000, 200, show_plot=False)

    assert isinstance(ax, matplotlib.axes.Axes)
    assert len(ax.collections) == 1, "Expected one scatter collection"
    assert len(ax.lines) == 2, "Expected two threshold lines (vline + hline)"
    assert ax.get_xlabel() == "Condition 1"
    assert ax.get_ylabel() == "Condition 2"


def test_overview_crossplot_custom_axis_labels():
    """Test that custom axis labels are applied."""
    data = {
        'id': ['A', 'B'],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200,
                            xaxis="GDP", yaxis="Population", show_plot=False)

    assert ax.get_xlabel() == "GDP"
    assert ax.get_ylabel() == "Population"


def test_overview_crossplot_with_label():
    """Test that label=True annotates points."""
    data = {
        'id': ['A', 'B'],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200,
                            label=True, show_plot=False)

    assert len(ax.texts) == 2, "Expected one annotation per point"


def test_overview_crossplot_aggregates_duplicates():
    """Test that duplicate (id, time) rows are aggregated by mean."""
    data = {
        'id': ['A', 'A'],
        'year': [2000, 2000],
        'gdp': [10000, 30000],
        'pop': [100, 200],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200, show_plot=False)

    offsets = ax.collections[0].get_offsets()
    assert len(offsets) == 1, "Duplicates should be aggregated into one point"
    assert offsets[0][0] == pytest.approx(20000.0)
    assert offsets[0][1] == pytest.approx(150.0)


def test_overview_crossplot_drops_na_id():
    """Test that NaN id values are dropped."""
    data = {
        'id': ['A', np.nan],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200, show_plot=False)

    offsets = ax.collections[0].get_offsets()
    assert len(offsets) == 1, "NaN id rows should be dropped"


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


def test_overview_overlap_bar():
    """Tests that overview_overlap returns Axes for plot_type='bar'."""
    dat1 = pd.DataFrame({"id": ["RWA", "RWA", "GAB", "FRA", "BEL"]})
    dat2 = pd.DataFrame({"id": ["RWA", "GAB", "GAB", "ARG"]})

    ax = overview_overlap(dat1, dat2, dat1_id="id", dat2_id="id", show_plot=False)

    assert isinstance(ax, matplotlib.axes.Axes), "Expected a matplotlib Axes"


def test_overview_overlap_venn():
    """Tests that overview_overlap returns Axes for plot_type='venn'."""
    dat1 = pd.DataFrame({"id": ["RWA", "RWA", "GAB", "FRA"]})
    dat2 = pd.DataFrame({"id": ["RWA", "GAB", "ARG"]})

    ax = overview_overlap(dat1, dat2, dat1_id="id", dat2_id="id", plot_type="venn", show_plot=False)

    assert isinstance(ax, matplotlib.axes.Axes), "Expected a matplotlib Axes"


def test_overview_overlap_custom_names():
    """Tests that custom dataset names are accepted without error."""
    dat1 = pd.DataFrame({"country": ["RWA", "GAB"]})
    dat2 = pd.DataFrame({"country": ["GAB", "FRA"]})

    ax = overview_overlap(
        dat1, dat2,
        dat1_id="country",
        dat2_id="country",
        dat1_name="Survey A",
        dat2_name="Survey B",
        show_plot=False,
    )

    assert isinstance(ax, matplotlib.axes.Axes)


def test_overview_overlap_invalid_plot_type():
    """Tests that an invalid plot_type raises ValueError."""
    dat1 = pd.DataFrame({"id": ["RWA"]})
    dat2 = pd.DataFrame({"id": ["GAB"]})

    with pytest.raises(ValueError, match="plot_type must be"):
        overview_overlap(dat1, dat2, dat1_id="id", dat2_id="id", plot_type="pie")


def test_overview_crossplot():
    """Test that overview_crossplot returns an Axes with a scatter and two threshold lines."""
    data = {
        'id': ['A', 'A', 'B', 'B', 'C'],
        'year': [2000, 2001, 2000, 2001, 2000],
        'gdp': [10000, 30000, 20000, 50000, 5000],
        'population': [100, 200, 300, 250, 150],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'population', 25000, 200, show_plot=False)

    assert isinstance(ax, matplotlib.axes.Axes)
    assert len(ax.collections) == 1, "Expected one scatter collection"
    assert len(ax.lines) == 2, "Expected two threshold lines (vline + hline)"
    assert ax.get_xlabel() == "Condition 1"
    assert ax.get_ylabel() == "Condition 2"
    plt.close('all')


def test_overview_crossplot_custom_axis_labels():
    """Test that custom axis labels are applied."""
    data = {
        'id': ['A', 'B'],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200,
                            xaxis="GDP", yaxis="Population", show_plot=False)

    assert ax.get_xlabel() == "GDP"
    assert ax.get_ylabel() == "Population"
    plt.close('all')


def test_overview_crossplot_with_label():
    """Test that label=True annotates points."""
    data = {
        'id': ['A', 'B'],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200,
                            label=True, show_plot=False)

    assert len(ax.texts) == 2, "Expected one annotation per point"
    plt.close('all')


def test_overview_crossplot_aggregates_duplicates():
    """Test that duplicate (id, time) rows are aggregated by mean."""
    data = {
        'id': ['A', 'A'],
        'year': [2000, 2000],
        'gdp': [10000, 30000],
        'pop': [100, 200],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200, show_plot=False)

    offsets = ax.collections[0].get_offsets()
    assert len(offsets) == 1, "Duplicates should be aggregated into one point"
    assert offsets[0][0] == pytest.approx(20000.0)
    assert offsets[0][1] == pytest.approx(150.0)
    plt.close('all')


def test_overview_crossplot_drops_na_id():
    """Test that NaN id values are dropped."""
    data = {
        'id': ['A', np.nan],
        'year': [2000, 2000],
        'gdp': [10000, 50000],
        'pop': [100, 300],
    }
    df = pd.DataFrame(data)
    ax = overview_crossplot(df, 'id', 'year', 'gdp', 'pop', 25000, 200, show_plot=False)

    offsets = ax.collections[0].get_offsets()
    assert len(offsets) == 1, "NaN id rows should be dropped"
    plt.close('all')


@pytest.fixture
def tab_df():
    data = {
        'id_column': ['RWA', 'RWA', 'GAB', 'FRA', 'BEL'],
        'time': [2021, 2022, 2020, 2019, 2013],
    }
    return overview_tab(pd.DataFrame(data), 'id_column', 'time')


def test_overview_latex_returns_string(tab_df):
    result = overview_latex(tab_df)
    assert isinstance(result, str)


def test_overview_latex_contains_table_structure(tab_df):
    result = overview_latex(tab_df)
    assert r"\begin{table}" in result
    assert r"\begin{tabular}" in result
    assert r"\end{table}" in result
    assert r"\hline" in result


def test_overview_latex_default_headers(tab_df):
    result = overview_latex(tab_df)
    assert "Sample & Time frame" in result


def test_overview_latex_custom_headers(tab_df):
    result = overview_latex(tab_df, id="Country", time="Years")
    assert "Country & Years" in result


def test_overview_latex_custom_title_and_label(tab_df):
    result = overview_latex(tab_df, title="My Table", label="tab:mytab")
    assert r"\caption{My Table}" in result
    assert r"\label{tab:mytab}" in result


def test_overview_latex_fontsize(tab_df):
    result = overview_latex(tab_df, fontsize="small")
    assert r"\small" in result


def test_overview_latex_contains_data_rows(tab_df):
    result = overview_latex(tab_df)
    assert "BEL" in result
    assert "FRA" in result
    assert "GAB" in result
    assert "RWA" in result


def test_overview_latex_save_out(tab_df, tmp_path):
    out_file = tmp_path / "output.tex"
    overview_latex(tab_df, save_out=True, file_path=str(out_file))
    assert out_file.exists()
    content = out_file.read_text()
    assert r"\begin{table}" in content


def test_overview_latex_save_out_requires_file_path(tab_df):
    with pytest.raises(ValueError, match="file_path"):
        overview_latex(tab_df, save_out=True)


def test_overview_latex_two_row_tab_warns(tab_df):
    two_row = tab_df.head(2)
    with pytest.warns(UserWarning, match="crosstab"):
        overview_latex(two_row)


def test_overview_latex_rejects_wrong_column_count():
    bad_df = pd.DataFrame({'a': [1], 'b': [2], 'c': [3]})
    with pytest.raises(ValueError, match="two columns"):
        overview_latex(bad_df)


def test_overview_latex_crosstab_rejects_wrong_row_count():
    bad_df = pd.DataFrame({'col1': ["A", "B", "C"], 'col2': ["D", "E", "F"]})
    with pytest.raises(ValueError, match="exactly 2 rows"):
        overview_latex(bad_df, crosstab=True)


def test_overview_latex_crosstab_structure():
    crosstab_df = pd.DataFrame({
        'col1': ["Country A, Country B", "Country C"],
        'col2': ["Country D", "Country E, Country F"],
    })
    result = overview_latex(
        crosstab_df,
        crosstab=True,
        title="Cross-tab",
        cond1="GDP",
        cond2="Population",
    )
    assert r"\begin{tabularx}" in result
    assert r"\multicolumn" in result
    assert r"\multirow" in result
    assert "GDP" in result
    assert "Population" in result
    assert "Fulfilled" in result
    assert "Not fulfilled" in result
