# overviewpy 


![PyPI](https://img.shields.io/pypi/v/overviewpy) [![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)
![CI/CD](https://github.com/cosimameyer/overviewpy/actions/workflows/ci-cd.yml/badge.svg) <img src='https://raw.githubusercontent.com/cosimameyer/overviewpy/main/docs/img/overviewpy.png' align="right" width="200px" />

overviewpy aims to make it easy to get an overview of a data set by displaying relevant sample information. 

## Installation

```bash
$ pip install overviewpy
```

## Usage

### Implemented Functions
The goal of `overviewpy` is to make it easy to get an overview of a data set by displaying relevant sample information. At the moment, there are the following functions:

- `overview_tab` generates a tabular overview of the sample (and returns a data frame). The general sample plots a two-column table that provides information on an id in the left column and a the time frame on the right column.
- `overview_na` plots an overview of missing values by variable (both by row and by column)
- `overview_summary` returns a per-column summary of any data frame (non-null count, unique count, sample values)
- `overview_plot` visualizes observation presence across id and time as a connected dot-plot

#### `overview_tab`

Generate some general overview of the data set using the time and scope
conditions with `overview_tab`. The resulting data frame collapses the time condition for each `id` by
taking into account potential gaps in the time frame.

Rows with missing values in either the `id` or `time` column are automatically
dropped and a `UserWarning` is raised for each affected variable.

```python
from overviewpy.overviewpy import Overview
import pandas as pd

data = {
       'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', \
        'FRA', 'BEL', 'BEL', 'ARG'],
       'year': [2022, 2023, 2021, 2023, 2020, 2019, 2015, \
        2014, 2013, 2002]
   }

df = pd.DataFrame(data)

overview = Overview(df=df, id='id', time='year')
df_overview = overview.overview_tab()
```

The output is a data frame with one row per id and a `time_frame` column that compresses consecutive years into ranges (e.g. `2021-2023`) and non-consecutive years as a comma-separated list (e.g. `2015, 2019`):

![overview_tab output](docs/img/overview_tab.png)

If your data contains missing values in `id` or `year`, they are silently
removed and you will see a warning — no extra preprocessing needed:

```python
import numpy as np

data_with_na = {
    'id': ['RWA', 'RWA', np.nan, 'GAB'],
    'year': [2022, np.nan, 2021, 2020],
}

df_na = pd.DataFrame(data_with_na)

# UserWarning: missing id and time values are dropped automatically
overview = Overview(df=df_na, id='id', time='year')
df_overview = overview.overview_tab()
```

#### `overview_na`

`overview_na` visualises missing values in your data. It returns a
horizontal bar plot showing the amount of missing data (NAs) for each variable,
sorted from most to least missing. By default it shows percentages (`perc=True`);
pass `perc=False` to display absolute counts instead. Switch to `row_wise=True`
for a per-observation view, or set `add=True` to append the NA statistics
directly to your data frame.

```python
from overviewpy.overviewpy import Overview
import pandas as pd
import numpy as np

data_na = {
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB',\
            'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan,  np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, \
            2019,  np.nan, 2015, 2014, 2013, 2002]
    }

df_na = pd.DataFrame(data_na)

ov_na = Overview(df=df_na, id='id', time='year')

# Default: column-wise, percentage
ov_na.overview_na()

# Absolute counts instead of percentage
ov_na.overview_na(perc=False)

# Custom y-axis label
ov_na.overview_na(yaxis="My Variables")

# Row-wise: one bar per observation
ov_na.overview_na(row_wise=True)

# Row-wise and augment the data frame with na_count and percentage columns
df_with_na = ov_na.overview_na(row_wise=True, add=True)
```

Column-wise output (default):

![overview_na column-wise](docs/img/overview_na_column.png)

Row-wise output:

![overview_na row-wise](docs/img/overview_na_row.png)

#### `overview_summary`

Use `overview_summary` to get a quick structured overview of any data frame:

```python
from overviewpy.overviewpy import Overview
import pandas as pd

df = pd.read_csv("mydata.csv")
overview = Overview(df=df, id=None, time=None)
overview.overview_summary()
```

This returns a data frame with one row per column containing `non_null_count`, `unique_count`, and `sample_values`:

![overview_summary output](docs/img/overview_summary.png)

#### `overview_plot`

`overview_plot` visualizes the presence of observations across the id and time
dimensions. Each id appears as a row; time is on the x-axis. Consecutive time
periods are connected by a line; gaps in coverage produce separate disconnected
clusters. Optionally color-code points by a third variable.

```python
from overviewpy.overviewpy import overview_plot
import pandas as pd

data = {
    'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', 'FRA', 'BEL', 'BEL', 'ARG'],
    'year': [2022, 2023, 2021, 2023, 2020, 2019, 2015, 2014, 2013, 2002]
}

df = pd.DataFrame(data)

overview_plot(df, id='id', time='year')
```

![overview_plot output](docs/img/overview_plot.png)

You can color-code the points by a third variable using the `color` parameter:

```python
# color-code points by a third variable
overview_plot(df, id='id', time='year', color='regime')
```

![overview_plot output with color](docs/img/overview_plot_color.png)

##### Command line

Alternatively, run the summarizer from the command line to generate an HTML report:

##### Invocation
```
usage: $ python -m overviewpy [-h] [-d DELIMITER] [-t {csv}] [-o {file,stdout}] datafile

positional arguments:
  datafile              The data file to read. Expects a path to a readable data file.

options:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        Define the character(s) which delimit the file. Defaults to ','.
  -t {csv,excel,fwf}, --filetype {csv,excel,fwf}
                        File type to parse the datafile with. Inferred from the file extension if omitted.
  -o {file,stdout}, --output-type {file,stdout}
                        Type of output desired. Defaults to creating an HTML file.
```

##### Output

The default output is created as an HTML file in the same directory as the datafile passed in. The output file will be
named with the stem of the datafile name and `-summary.html`. For example, if your datafile is named `magicdata.csv`,
the output file would be `magicdata-summary.html`

The output file will list, at the top, some summary information about the number of rows and columns in the file.

Below that frontmatter is a table listing, for each included column in the file:

1. The column name
2. The number of non-null/empty values for that column
3. The number of unique non-null values for that column
4. A set of 5 example values found in that column.

### Roadmap
`overviewpy` seeks to mirror the functionality of [`overviewR`](https://github.com/cosimameyer/overviewR) and will extend its features with the following functionality in the future:

-   `overview_crosstab` generates a cross table. The conditional column allows to disaggregate the overview table by specifying two conditions, hence resulting a 2x2 table. This way, it is easy to visualize the time and scope conditions as well as theoretical assumptions with examples from the data set.
-   `overview_latex` converts the output of both `overview_tab` and `overview_crosstab` into LaTeX code and/or directly into a .tex file.
-   `overview_crossplot` is an alternative to visualize a cross table (a way to present results from `overview_crosstab`)
-   `overview_heat` plots a heat map of your time line
-   `overview_overlap` plots comparison plots (bar graph and Venn diagram) to compare to data frames

## Contributing

Interested in contributing? Check out the [contributing guidelines](/CONTRIBUTING.md). Please note that this project is released with a [Code of Conduct](/CONDUCT.md). By contributing to this project, you agree to abide by its terms.

## License

`overviewpy` is licensed under the terms of the BSD 3-Clause license.

## Credits

`overviewpy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
