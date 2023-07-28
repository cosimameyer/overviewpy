import pandas
import pathlib


class Summarizer:
    """
    """

    @staticmethod
    def _read_datafile(datafile: pathlib.Path, filetype='csv', delimiter=',') -> pandas.DataFrame:
        """Read the input datafile into a Pandas DataFrame.
        TODO: Support additional filetypes: Excel, fixed-width.

        :param datafile: pathlib.Path
        :param filetype: str
        :param delimiter: str
        :return: pandas.DataFrame
        """
        if filetype == 'csv':
            try:
                df = pandas.read_csv(datafile, delimiter=delimiter)
            except pandas.errors.ParserError as err:
                print(f'Unable to parse file {datafile.name}: {err}')
                df = None
            except UnicodeDecodeError:
                print('Unable to decode file as UTF-8. Retrying with ISO-8859-1.')
                df = pandas.read_csv(datafile, delimiter=delimiter, encoding='ISO-8859-1')
        else:
            raise ValueError(f"Unrecognized value for `type` argument: {type}")

        return df

    def __init__(self, datafile: pathlib.Path, filetype='csv', delimiter=','):
        self.filename = datafile.name
        self.file_location = datafile.parent
        self.df = Summarizer._read_datafile(datafile, filetype, delimiter)
        self.column_details = self._compile_column_details()

    def get_shape(self) -> tuple[int, int]:
        return self.df.shape

    def get_column_names(self) -> list[str]:
        return list(self.df.columns)

    def _get_details_for_column(self, column_name: str) -> dict:
        series = self.df[column_name]

        count_non_null = series.count()
        unique_non_null = series.dropna().unique()

        details = {
            'colName': column_name,
            'nonNullCount': count_non_null,
            'uniquesCount': len(unique_non_null),
            'sampleValues': unique_non_null[0:5],
        }

        return details

    def _compile_column_details(self):
        column_details = {}
        for c in self.get_column_names():
            column_details[c] = self._get_details_for_column(c)

        return column_details

    def get_summary(self):
        row_count, column_count = self.get_shape()

        summary = {
            'filename': self.filename,
            'rowCount': row_count,
            'columnCount': column_count,
            'columnDetails': list(self.column_details.values()),
        }

        return summary
