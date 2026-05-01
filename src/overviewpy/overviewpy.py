import warnings
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


class Overview:
    def __init__(self, df: pd.DataFrame, id: str | None, time: str | None):
        self.df = df
        self.id = id
        self.time = time

    def overview_tab(self) -> pd.DataFrame:
        """Generates a tabular overview of the sample and returns a data frame.

        Collapses the time variable per id into compact ranges (e.g. "2013-2015,
        2019"). Rows where id or time is NA are dropped automatically and a
        ``UserWarning`` is raised for each affected variable.

        Returns:
            pd.DataFrame: Two-column frame with id and time_frame columns, one
            row per unique id.
        """
        df_no_id_na = self.df.dropna(subset=[self.id]).copy()
        if len(df_no_id_na) != len(self.df):
            warnings.warn(
                "There is at least one missing value in your id variable. The missing value is automatically deleted.",
                UserWarning,
                stacklevel=2,
            )

        df_clean = df_no_id_na.dropna(subset=[self.time]).copy()
        if len(df_clean) != len(df_no_id_na):
            warnings.warn(
                "There is at least one missing value in your time variable. The missing value is automatically deleted.",
                UserWarning,
                stacklevel=2,
            )

        df_no_dup = df_clean.filter(items=[self.id, self.time]).drop_duplicates().copy()

        if len(df_no_dup) != len(df_clean):
            warnings.warn("There are some duplicates. We aggregate the data before proceeding.", UserWarning, stacklevel=2)

        df_sorted = df_no_dup.sort_values([self.id, self.time])
        grouped = df_sorted.groupby(self.id)

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

    def overview_na(
        self,
        show_plot: bool = True,
        yaxis: str = "Variables",
        perc: bool = True,
        row_wise: bool = False,
        add: bool = False,
    ) -> matplotlib.axes.Axes | pd.DataFrame:
        """Plots an overview of missing values or augments the data frame with NA counts.

        Args:
            show_plot: Whether to display the plot. Defaults to True.
            yaxis: Y-axis label. Defaults to "Variables". Overridden to "Observations" when row_wise=True.
            perc: If True (default), plot shows percentage of NAs; if False, shows absolute counts.
            row_wise: If True, calculates NAs per row instead of per column. Defaults to False.
            add: If True (only used with row_wise=True), returns the original data frame with
                na_count and percentage columns appended instead of a plot. Defaults to False.

        Returns:
            matplotlib.axes.Axes when a plot is produced, or pd.DataFrame when add=True.
        """
        if row_wise:
            yaxis = "Observations"
            na_count = self.df.isna().sum(axis=1)
            total = len(self.df.columns)
            if add:
                return self.df.assign(
                    na_count=na_count.values,
                    percentage=na_count.values / total * 100,
                )
            result = pd.DataFrame({
                "variable": range(1, len(self.df) + 1),
                "na_count": na_count.values,
                "percentage": na_count.values / total * 100,
            })
        else:
            na_count = self.df.isna().sum()
            total = len(self.df)
            result = pd.DataFrame({
                "variable": na_count.index,
                "na_count": na_count.values,
                "percentage": na_count.values / total * 100,
            })

        x = "percentage" if perc else "na_count"
        xaxis = "Number of NA (in %)" if perc else "Number of NA (total)"
        return self._plot_na(result, x=x, yaxis=yaxis, xaxis=xaxis, show_plot=show_plot)

    def _plot_na(
        self,
        result: pd.DataFrame,
        x: str,
        yaxis: str,
        xaxis: str,
        show_plot: bool,
    ) -> matplotlib.axes.Axes:
        sorted_result = result.sort_values(x, ascending=True)
        fig, ax = plt.subplots()
        ax.barh(sorted_result["variable"].astype(str), sorted_result[x])
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        if show_plot:
            plt.show()
        return ax


def overview_tab(df: pd.DataFrame, id: str, time: int) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_tab. Deprecated since 0.2.0."""
    return Overview(df, id, time).overview_tab()


def overview_na(
    df: pd.DataFrame,
    show_plot: bool = True,
    yaxis: str = "Variables",
    perc: bool = True,
    row_wise: bool = False,
    add: bool = False,
) -> matplotlib.axes.Axes | pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_na. Deprecated since 0.2.0."""
    return Overview(df, None, None).overview_na(
        show_plot=show_plot, yaxis=yaxis, perc=perc, row_wise=row_wise, add=add
    )


def overview_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a per-column summary of the data frame.

    Args:
        df (pd.DataFrame): Input data frame.

    Returns:
        pd.DataFrame: One row per column with non_null_count, unique_count, and sample_values.
    """
    return Overview(df, None, None).overview_summary()
