import pandas as pd
import pathlib


_EXTENSION_TO_FILETYPE = {
    '.csv': 'csv',
    '.tsv': 'csv',
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.xlsm': 'excel',
    '.ods': 'excel',
    '.fwf': 'fwf',
}


class Summarizer:

    @staticmethod
    def _infer_filetype(datafile: pathlib.Path) -> str:
        filetype = _EXTENSION_TO_FILETYPE.get(datafile.suffix.lower())
        if filetype is None:
            raise ValueError(f"Cannot infer filetype from extension {datafile.suffix!r}. Pass filetype explicitly.")
        return filetype

    @staticmethod
    def _read_datafile(datafile: pathlib.Path, filetype: str, delimiter=',') -> pd.DataFrame:
        if filetype == 'csv':
            delimiter = '\t' if datafile.suffix.lower() == '.tsv' else delimiter
            try:
                df = pd.read_csv(datafile, delimiter=delimiter)
            except pd.errors.ParserError as err:
                print(f'Unable to parse file {datafile.name}: {err}')
                df = None
            except UnicodeDecodeError:
                print('Unable to decode file as UTF-8. Retrying with ISO-8859-1.')
                df = pd.read_csv(datafile, delimiter=delimiter, encoding='ISO-8859-1')
        elif filetype == 'excel':
            df = pd.read_excel(datafile)
        elif filetype == 'fwf':
            df = pd.read_fwf(datafile)
        else:
            raise ValueError(f"Unrecognized filetype: {filetype!r}")

        return df

    def __init__(self, datafile: pathlib.Path, filetype: str | None = None, delimiter=','):
        self.filename = datafile.name
        self.file_location = datafile.parent
        resolved_filetype = filetype or Summarizer._infer_filetype(datafile)
        self.df = Summarizer._read_datafile(datafile, resolved_filetype, delimiter)
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
