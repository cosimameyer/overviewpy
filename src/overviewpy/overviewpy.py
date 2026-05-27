import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


class Overview:
    def __init__(self, df: pd.DataFrame, id: str | None, time: str | None):
        self.df = df
        self.id = id
        self.time = time

    def overview_tab(self):
        """Generates a tabular overview of the sample and returns a data frame.

        Returns:
            pd.DataFrame: Reduced data frame with id and time_frame columns.
        """
        df2 = self.df.dropna(subset=[self.id]).copy()
        if len(df2) != len(self.df):
            print("There is at least one missing value in your id variable. The missing value is automatically deleted.")

        df_no_dup = df2.filter(items=[self.id, self.time]).drop_duplicates()

        if len(df_no_dup) != len(df2):
            print("There are some duplicates. We aggregate the data before proceeding.")

        df_sorted = df_no_dup.sort_values([self.id, self.time])
        grouped = df_sorted.groupby(self.id)
        self.df['time_frame'] = df_no_dup[self.time].astype(str)

        for _, group_df in grouped:
            numbers = group_df[self.time].tolist()

            if len(numbers) > 1:
                consecutive_ranges = []
                current_range = [numbers[0]]

                for i in range(1, len(numbers)):
                    if numbers[i] == numbers[i - 1] + 1:
                        current_range.append(numbers[i])
                    else:
                        if len(current_range) > 1:
                            consecutive_ranges.append(f'{current_range[0]}-{current_range[-1]}')
                        else:
                            consecutive_ranges.append(str(current_range[0]))
                        current_range = [numbers[i]]

                if len(current_range) > 1:
                    consecutive_ranges.append(f'{current_range[0]}-{current_range[-1]}')
                else:
                    consecutive_ranges.append(str(current_range[0]))

                combined_str = ', '.join(consecutive_ranges)
            else:
                combined_str = str(numbers[0])

            df_no_dup.loc[group_df.index, 'time_frame'] = combined_str

        return df_no_dup[[self.id, 'time_frame']].sort_values([self.id]).drop_duplicates()

    def overview_summary(self) -> pd.DataFrame:
        """Returns a per-column summary of the data frame.

        Returns:
            pd.DataFrame: One row per column with non_null_count, unique_count, and sample_values.
        """
        rows = []
        for col in self.df.columns:
            non_null = self.df[col].dropna()
            rows.append({
                'column': col,
                'non_null_count': non_null.count(),
                'unique_count': non_null.nunique(),
                'sample_values': list(non_null.unique()[:5]),
            })
        return pd.DataFrame(rows).set_index('column')

    def overview_na(self, show_plot: bool = True) -> matplotlib.axes.Axes:
        """Plots an overview of missing values by variable.

        Args:
            show_plot: Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.axes.Axes: Bar plot of missing value counts per column.
        """
        ax = self.df.isna().sum().plot(kind="barh")
        ax.set_xlabel("Count")
        ax.set_ylabel("Columns")
        plt.title("Missing Values Overview")

        if show_plot:
            plt.show()

        return ax


def overview_tab(df: pd.DataFrame, id: str, time: int) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_tab. Deprecated since 0.2.0."""
    return Overview(df, id, time).overview_tab()


def overview_na(df: pd.DataFrame, show_plot: bool = True) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_na. Deprecated since 0.2.0."""
    return Overview(df, None, None).overview_na(show_plot)


def overview_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a per-column summary of the data frame.

    Args:
        df (pd.DataFrame): Input data frame.

    Returns:
        pd.DataFrame: One row per column with non_null_count, unique_count, and sample_values.
    """
    return Overview(df, None, None).overview_summary()
