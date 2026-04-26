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

    def overview_na(self, show_plot: bool = True, relative: bool = False) -> matplotlib.axes.Axes:
        """Plots an overview of missing values by variable.

        Args:
            show_plot: Whether to display the plot. Defaults to True.
            relative: If True, shows percentage of missing values instead of absolute count.
                Defaults to False.

        Returns:
            matplotlib.axes.Axes: Horizontal bar plot of missing value counts or percentages,
                sorted in descending order.
        """
        na_counts = self.df.isna().sum()

        if relative:
            values = (na_counts / len(self.df) * 100).sort_values(ascending=True)
            xlabel = "Percentage (%)"
        else:
            values = na_counts.sort_values(ascending=True)
            xlabel = "Count"

        ax = values.plot(kind="barh")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Columns")
        plt.title("Missing Values Overview")

        if show_plot:
            plt.show()

        return ax

    def overview_plot(
        self,
        xaxis: str = "Time frame",
        yaxis: str = "Sample",
        asc: bool = True,
        color: str | None = None,
        dot_size: int = 2,
        show_plot: bool = True,
    ) -> matplotlib.axes.Axes:
        """Visualizes the presence of observations across id and time.

        Each id appears as a row; time is on the x-axis. Consecutive time periods are
        connected by a line; gaps produce separate disconnected point clusters.

        Args:
            xaxis: Label for the x-axis. Defaults to "Time frame".
            yaxis: Label for the y-axis. Defaults to "Sample".
            asc: If True, ids are displayed in ascending order from top to bottom.
                Defaults to True.
            color: Optional column name to color-code points by a third variable.
                Defaults to None.
            dot_size: Size of the plotted points. Defaults to 2.
            show_plot: Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.axes.Axes: The resulting timeline plot.
        """
        cols = [self.id, self.time]
        if color is not None:
            cols.append(color)

        dat_red = (
            self.df[cols]
            .dropna(subset=[self.id, self.time])
            .drop_duplicates()
            .sort_values([self.id, self.time])
            .reset_index(drop=True)
        )

        ids_sorted = sorted(dat_red[self.id].unique(), key=str)
        id_to_pos = {id_val: i for i, id_val in enumerate(ids_sorted)}

        if color is not None:
            color_vals = sorted(dat_red[color].dropna().unique(), key=str)
            cmap = matplotlib.colormaps.get_cmap("tab10").resampled(max(len(color_vals), 1))
            color_map = {v: cmap(i) for i, v in enumerate(color_vals)}

        fig, ax = plt.subplots()

        for id_val in ids_sorted:
            y_pos = id_to_pos[id_val]
            id_data = dat_red[dat_red[self.id] == id_val].sort_values(self.time)
            times = id_data[self.time].tolist()

            # Split into consecutive segments (gap > 1 breaks the line)
            segments = []
            current_seg = [times[0]]
            for i in range(1, len(times)):
                if times[i] == times[i - 1] + 1:
                    current_seg.append(times[i])
                else:
                    segments.append(current_seg)
                    current_seg = [times[i]]
            segments.append(current_seg)

            for seg in segments:
                ax.plot(seg, [y_pos] * len(seg), color="black", linewidth=1.5, zorder=1)
                if color is not None:
                    seg_data = id_data[id_data[self.time].isin(seg)]
                    point_colors = [color_map[c] for c in seg_data[color].tolist()]
                    ax.scatter(
                        seg,
                        [y_pos] * len(seg),
                        c=point_colors,
                        marker="s",
                        s=dot_size * 10,
                        zorder=2,
                    )
                else:
                    ax.scatter(
                        seg,
                        [y_pos] * len(seg),
                        color="black",
                        marker="s",
                        s=dot_size * 10,
                        zorder=2,
                    )

        ax.set_yticks(range(len(ids_sorted)))
        ax.set_yticklabels(ids_sorted)
        if asc:
            ax.invert_yaxis()

        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)
        ax.set_facecolor("white")
        fig.patch.set_facecolor("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(left=False)
        ax.xaxis.grid(True, color="grey", linestyle="--", alpha=0.7, zorder=0)
        ax.set_axisbelow(True)

        if color is not None:
            handles = [
                plt.Line2D(
                    [0], [0],
                    marker="s", color="w", markerfacecolor=color_map[v],
                    markersize=8, label=str(v),
                )
                for v in color_vals
            ]
            ax.legend(
                handles=handles,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.15),
                ncol=len(color_vals),
                frameon=False,
            )

        if show_plot:
            plt.show()

        return ax


def overview_tab(df: pd.DataFrame, id: str, time: int) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_tab. Deprecated since 0.2.0."""
    return Overview(df, id, time).overview_tab()


def overview_na(df: pd.DataFrame, show_plot: bool = True, relative: bool = False) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_na. Deprecated since 0.2.0."""
    return Overview(df, None, None).overview_na(show_plot, relative)


def overview_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a per-column summary of the data frame.

    Args:
        df (pd.DataFrame): Input data frame.

    Returns:
        pd.DataFrame: One row per column with non_null_count, unique_count, and sample_values.
    """
    return Overview(df, None, None).overview_summary()


def overview_plot(
    df: pd.DataFrame,
    id: str,
    time: str,
    xaxis: str = "Time frame",
    yaxis: str = "Sample",
    asc: bool = True,
    color: str | None = None,
    dot_size: int = 2,
    show_plot: bool = True,
) -> matplotlib.axes.Axes:
    """Visualizes the presence of observations across id and time.

    Args:
        df: Input data frame.
        id: Column name for the unit identifier (e.g. country code).
        time: Column name for the time variable (numeric, e.g. year).
        xaxis: Label for the x-axis. Defaults to "Time frame".
        yaxis: Label for the y-axis. Defaults to "Sample".
        asc: If True, ids are displayed in ascending order from top to bottom.
            Defaults to True.
        color: Optional column name to color-code points by a third variable.
            Defaults to None.
        dot_size: Size of the plotted points. Defaults to 2.
        show_plot: Whether to display the plot. Defaults to True.

    Returns:
        matplotlib.axes.Axes: The resulting timeline plot.
    """
    return Overview(df, id, time).overview_plot(
        xaxis=xaxis,
        yaxis=yaxis,
        asc=asc,
        color=color,
        dot_size=dot_size,
        show_plot=show_plot,
    )
