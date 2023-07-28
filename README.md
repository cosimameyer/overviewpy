# overviewpy <img src='https://raw.githubusercontent.com/cosimameyer/overviewpy/main/docs/img/overviewpy.png' align="right" width="200px" />



![PyPI](https://img.shields.io/pypi/v/overviewpy) [![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)
![CI/CD](https://github.com/cosimameyer/overviewpy/actions/workflows/ci-cd.yml/badge.svg)

overviewpy aims to make it easy to get an overview of a data set by displaying relevant sample information. 

## Installation

```bash
$ pip install overviewpy
```

## Usage

### Implemented Functions
The goal of `overviewpy` is to make it easy to get an overview of a data set by displaying relevant sample information. At the moment, there are the following functions:

- `overviewpy` provides a command line interface to get an overview of the contents of a data
    file as an HTML document.
- `overview_tab` generates a tabular overview of the sample (and returns a data frame). The general sample plots a two-column table that provides information on an id in the left column and a the time frame on the right column.
- `overview_na` plots an overview of missing values by variable (both by row and by column)

#### Summarization
##### Invocation
```
usage: $ python -m overviewpy [-h] [-d DELIMITER] [-t {csv}] [-o {file,stdout}] datafile

positional arguments:
  datafile              The data file to read. Expects a path to a readable data file.

options:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        Define the character(s) which delimit the file. Defaults to ','.
  -t {csv}, --filetype {csv}
                        The Pandas file type to parse the dataFile with. Defaults to 'csv'.
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

#### `overview_tab`

Generate some general overview of the data set using the time and scope
conditions with `overview_tab`. The resulting data frame collapses the time condition for each id by
taking into account potential gaps in the time frame.

```python
from overviewpy.overviewpy import overview_tab
import pandas as pd

data = {
       'id': ['RWA', 'RWA', 'RWA', 'GAB', 'GAB', 'FRA', \
        'FRA', 'BEL', 'BEL', 'ARG'],
       'year': [2022, 2023, 2021, 2023, 2020, 2019, 2015, \
        2014, 2013, 2002]
   }

df = pd.DataFrame(data)

df_overview = overview_tab(df=df, id='id', time='year')
```

#### `overview_na`

`overview_na` is a simple function that provides information about the
content of all variables in your data, not only the time and scope
conditions. It returns a horizontal ggplot bar plot that indicates the
amount of missing data (NAs) for each variable (on the y-axis). You can
choose whether to display the relative amount of NAs for each variable
in percentage (the default) or the total number of NAs.

```python
from overviewpy.overviewpy import overview_na
import pandas as pd
import numpy as np

data_na = {
        'id': ['RWA', 'RWA', 'RWA', np.nan, 'GAB', 'GAB',\
            'FRA', 'FRA', 'BEL', 'BEL', 'ARG', np.nan,  np.nan],
        'year': [2022, 2001, 2000, 2023, 2021, 2023, 2020, \
            2019,  np.nan, 2015, 2014, 2013, 2002]
    }

df_na = pd.DataFrame(data_na)

overview_na(df_na)

```

### Roadmap
`overviewpy` seeks to mirror the functionality of [`overviewR`](https://github.com/cosimameyer/overviewR) and will extend its features with the following functionality in the future:

-   `overview_crosstab` generates a cross table. The conditional column allows to disaggregate the overview table by specifying two conditions, hence resulting a 2x2 table. This way, it is easy to visualize the time and scope conditions as well as theoretical assumptions with examples from the data set.
-   `overview_latex` converts the output of both `overview_tab` and `overview_crosstab` into LaTeX code and/or directly into a .tex file.
-   `overview_plot` is an alternative to visualize the sample (a way to present results from `overview_tab`)
-   `overview_crossplot` is an alternative to visualize a cross table (a way to present results from `overview_crosstab`)
-   `overview_heat` plots a heat map of your time line
-   `overview_overlap` plots comparison plots (bar graph and Venn diagram) to compare to data frames

## Contributing

Interested in contributing? Check out the [contributing guidelines](/CONTRIBUTING.md). Please note that this project is released with a [Code of Conduct](/CONDUCT.md). By contributing to this project, you agree to abide by its terms.

## License

`overviewpy` is licensed under the terms of the BSD 3-Clause license.

## Credits

`overviewpy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
