import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


class Overview:
    """

    """

    def __init__(self, df: pd.DataFrame, id: str|None, time: str|None):
        """
        If df is dataframe, take it as is. If it's a path, open the file.
        """
        self.df = df
        self.id = id
        self.time = time

    def overview_tab(self):
        """
        Generates a tabular overview of the sample (and returns a data frame).
        The general sample plots a two-column table that provides information on an
        id in the left column and a the time frame on the right column.

        Args:
            df (pd.DataFrame): Input data frame
            id (str): Identifies the id column (for instance, country)
            time (str): Identifies the time column (for instance, years)

        Returns:
            pd.DataFrame: Returns a reduced data frame that shows a cohesive
            overview of the data frame
        """
        df2 = self.df.dropna(subset=[self.id]).copy()
        if len(df2) != len(self.df):
            print("There is at least one missing value in your id variable. The missing value is automatically deleted.")

        df_no_dup = df2.filter(items=[self.id, self.time]).drop_duplicates()

        if len(df_no_dup) == len(df2):
            df_sorted = df_no_dup.sort_values([self.id, self.time])

            # Group the DataFrame by the ID column
            grouped = df_sorted.groupby(self.id)

            # Initialize the combined column
            self.df['time_frame'] = df_no_dup[self.time].astype(str)

            # Check if numbers within each group are consecutive and combine them
            for group_name, group_df in grouped:
                numbers = group_df[self.time].tolist()

                combined_str = ""

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

        else:
            print("There are some duplicates. Make sure to aggregate first.")

    def overview_na(self, show_plot: bool = True) -> matplotlib.axes.Axes:
        """Plots an overview of missing values by variable.

        Args:
            show_plot: bool
                Flag for if the plot should be show or just generated. Defaults to True.

        Returns:
            matplotlib.axes.Axes: Bar plot visualizing the number of missing values per variable
        """
        ax = self.df.isna().sum().plot(kind="barh")
        ax.set_xlabel("Count")
        ax.set_ylabel("Columns")
        plt.title("Missing Values Overview")

        if show_plot:
            plt.show()

        return ax


def overview_tab(df: pd.DataFrame, id: str, time: str) -> pd.DataFrame:
    """
    Accessor method for Overview.overview_tab.

    Implemented to maintain backward compatability with version 0.1.0, but should be considered deprecated.

    Args:
        df (pd.DataFrame): Input data frame
        id (str): Identifies the id column (for instance, country)
        time (str): Identifies the time column (for instance, years)

    Returns:
        pd.DataFrame: Returns a reduced data frame that shows a cohesive
        overview of the data frame
    """
    return Overview(df, id, time).overview_tab()


def overview_na(df: pd.DataFrame, show_plot: bool = True) -> matplotlib.axes.Axes:
    """
    Accessor method for the Overview.overview_na().

    Implemented to maintain backward compatability with version 0.1.0, but should be considered deprecated.

    Args:
        df (pd.DataFrame): Input data frame

    Returns:
        matplotlib.axes.Axes: Bar plot visualizing the number of missing values per variable
    """
    return Overview(df, None, None).overview_na(show_plot)
