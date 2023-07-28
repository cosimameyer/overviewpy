# Data Summarizer

## Purpose
Provide simple data summarization and exploration of an input data file.

## Usage

### Requirements
- Python 3.9+

####  Packages
- pandas
- jinja2

### Invocation
```
usage: data-file-summarizer [-h] [-d DELIMITER] [-t {csv}] [-o {file,stdout}] datafile

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

### Output

The default output is created as an HTML file in the same directory as the datafile passed in. The output file will be
named with the stem of the datafile name and `-summary.html`. For example, if your datafile is named `magicdata.csv`,
the output file would be `magicdata-summary.html`

The output file will list, at the top, some summary information about the number of rows and columns in the file.

Below that frontmatter is a table listing, for each included column in the file:

1. The column name
2. The number of non-null/empty values for that column
3. The number of unique non-null values for that column
4. A set of 5 example values found in that column.
