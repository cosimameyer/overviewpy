import warnings
import matplotlib
import matplotlib.colors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd
from datetime import date


def _consecutive_segments(numbers: list) -> list[list]:
    """Split a sorted list of numbers into groups of consecutive values."""
    if not numbers:
        return []
    segments = []
    current = [numbers[0]]
    for i in range(1, len(numbers)):
        if numbers[i] == numbers[i - 1] + 1:
            current.append(numbers[i])
        else:
            segments.append(current)
            current = [numbers[i]]
    segments.append(current)
    return segments


class Overview:
    def __init__(self, df: pd.DataFrame, id_col: str | None, time: str | None):
        self.df = df
        self.id_col = id_col
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
        df_no_id_na = self.df.dropna(subset=[self.id_col]).copy()
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

        df_no_dup = df_clean.filter(items=[self.id_col, self.time]).drop_duplicates().copy()

        if len(df_no_dup) != len(df_clean):
            warnings.warn("There are some duplicates. We aggregate the data before proceeding.", UserWarning, stacklevel=2)

        df_sorted = df_no_dup.sort_values([self.id_col, self.time])
        grouped = df_sorted.groupby(self.id_col)

        for _, group_df in grouped:
            numbers = group_df[self.time].tolist()
            parts = []
            for seg in _consecutive_segments(numbers):
                parts.append(f'{seg[0]}-{seg[-1]}' if len(seg) > 1 else str(seg[0]))
            df_no_dup.loc[group_df.index, 'time_frame'] = ', '.join(parts)

        return df_no_dup[[self.id_col, 'time_frame']].sort_values([self.id_col]).drop_duplicates()

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

    def overview_crosstab(
        self,
        cond1: str,
        cond2: str,
        threshold1: float,
        threshold2: float,
    ) -> pd.DataFrame:
        """Sorts a dataset conditionally into a 2x2 cross table based on two conditions.

        If duplicate (id, time) pairs exist, conditions are aggregated using the mean.

        Args:
            cond1: Column name for the first condition.
            cond2: Column name for the second condition.
            threshold1: Threshold for cond1.
            threshold2: Threshold for cond2.

        Returns:
            pd.DataFrame: 2x2 DataFrame where each cell lists id (time_frame) entries.
        """
        df = self.df.dropna(subset=[self.id_col]).copy()
        if len(df) != len(self.df):
            warnings.warn(
                "There is a missing value in your id variable. The missing value is automatically deleted.",
                UserWarning,
                stacklevel=2,
            )

        if len(df[[self.id_col, self.time]].drop_duplicates()) != len(df):
            df = (
                df.groupby([self.id_col, self.time])[[cond1, cond2]]
                .mean()
                .reset_index()
            )

        df["_c1"] = (df[cond1] >= threshold1).astype(int)
        df["_c2"] = (df[cond2] >= threshold2).astype(int)

        quadrants = {
            "part1": df[(df["_c1"] == 1) & (df["_c2"] == 1)][[self.id_col, self.time]],
            "part2": df[(df["_c1"] == 0) & (df["_c2"] == 1)][[self.id_col, self.time]],
            "part3": df[(df["_c1"] == 1) & (df["_c2"] == 0)][[self.id_col, self.time]],
            "part4": df[(df["_c1"] == 0) & (df["_c2"] == 0)][[self.id_col, self.time]],
        }

        def _fmt(qdf: pd.DataFrame) -> str:
            if qdf.empty:
                return ""
            tab = Overview(qdf.reset_index(drop=True), self.id_col, self.time).overview_tab()
            return ", ".join(f"{row[self.id_col]} ({row['time_frame']})" for _, row in tab.iterrows())

        parts = {k: _fmt(v) for k, v in quadrants.items()}

        return pd.DataFrame(
            [[parts["part1"], parts["part2"]], [parts["part3"], parts["part4"]]],
            columns=[f"{cond1} >= {threshold1}", f"{cond1} < {threshold1}"],
            index=[f"{cond2} >= {threshold2}", f"{cond2} < {threshold2}"],
        )

    def overview_markdown(
        self,
        title: str = "Time and scope of the sample",
        id_label: str = "Sample",
        time_label: str = "Time frame",
        file_path: str | None = None,
    ) -> str:
        """Generates a Markdown table from overview_tab output.

        Args:
            title: Heading displayed above the table.
            id_label: Header for the id column (default: "Sample").
            time_label: Header for the time frame column (default: "Time frame").
            file_path: If provided, writes the output to this path as a .md file.

        Returns:
            str: Markdown-formatted string with a heading and table.
        """
        tab = self.overview_tab()
        lines = [
            f"## {title}",
            "",
            f"| {id_label} | {time_label} |",
            "|---|---|",
        ]
        for _, row in tab.iterrows():
            lines.append(f"| {row.iloc[0]} | {row.iloc[1]} |")

        output = "\n".join(lines)

        if file_path is not None:
            with open(file_path, "w") as f:
                f.write(output)

        return output

    def overview_crossplot(
        self,
        cond1: str,
        cond2: str,
        threshold1: float,
        threshold2: float,
        xaxis: str = "Condition 1",
        yaxis: str = "Condition 2",
        label: bool = False,
        color: bool = False,
        dot_size: float = 20,
        fontsize: float = 8,
        show_plot: bool = True,
    ) -> matplotlib.axes.Axes:
        """Plots a scatter of two conditions split by their thresholds.

        Observations are aggregated to (id, time) means before plotting.
        Vertical and horizontal lines mark the thresholds, dividing the
        plot into four quadrants.

        Args:
            cond1: Column name of the first condition (x-axis).
            cond2: Column name of the second condition (y-axis).
            threshold1: Threshold for cond1, drawn as a vertical line.
            threshold2: Threshold for cond2, drawn as a horizontal line.
            xaxis: X-axis label. Defaults to "Condition 1".
            yaxis: Y-axis label. Defaults to "Condition 2".
            label: Whether to annotate each point with its id-time label. Defaults to False.
            color: Whether to color points by quadrant. Defaults to False.
            dot_size: Marker size passed to scatter. Defaults to 20.
            fontsize: Font size for labels when label is True. Defaults to 8.
            show_plot: Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.axes.Axes: Scatter plot with threshold lines.
        """
        agg = (
            self.df.dropna(subset=[self.id_col])
            .groupby([self.id_col, self.time])[[cond1, cond2]]
            .mean()
            .reset_index()
        )
        agg["_grp"] = (
            (agg[cond1] >= threshold1).astype(int) * 2
            + (agg[cond2] >= threshold2).astype(int)
        )

        _, ax = plt.subplots()

        scatter_kw: dict = {"alpha": 0.5, "s": dot_size}
        if color:
            scatter_kw["c"] = [f"C{g}" for g in agg["_grp"]]
        ax.scatter(agg[cond1], agg[cond2], **scatter_kw)

        ax.axvline(x=threshold1, color="black")
        ax.axhline(y=threshold2, color="black")
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)

        if label:
            labels = agg[self.id_col].astype(str) + " (" + agg[self.time].astype(str) + ")"
            for (x, y, txt) in zip(agg[cond1], agg[cond2], labels):
                ax.annotate(txt, (x, y), fontsize=fontsize)

        if show_plot:
            plt.show()

        return ax

    def overview_heat(
        self,
        perc: bool = False,
        exp_total: int | None = None,
        xaxis: str = "Time frame",
        yaxis: str = "Sample",
        col_low: str = "#dceaf2",
        col_high: str = "#2A5773",
        label: bool = True,
        show_plot: bool = True,
    ) -> matplotlib.axes.Axes:
        """Plots a heat map of observation counts (or percentages) per time-scope-unit.

        Args:
            perc: If False (default), shows absolute count per cell. If True, shows percentage.
            exp_total: Expected total observations per time unit (denominator for percentages).
                Required when perc=True.
            xaxis: X-axis label. Defaults to "Time frame".
            yaxis: Y-axis label. Defaults to "Sample".
            col_low: Hex color for the lowest value. Defaults to "#dceaf2".
            col_high: Hex color for the highest value. Defaults to "#2A5773".
            label: If True (default), display values inside each cell.
            show_plot: Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.axes.Axes: Heat map of coverage across time-scope-units.

        Raises:
            ValueError: If perc=True but exp_total is not provided.
        """
        if perc and exp_total is None:
            raise ValueError("exp_total must be provided when perc=True.")

        counts = (
            self.df.groupby([self.id_col, self.time])
            .size()
            .reset_index(name="n")
        )

        if perc:
            counts["n"] = counts["n"] / exp_total * 100

        pivot = (
            counts.pivot(index=self.id_col, columns=self.time, values="n")
            .fillna(0)
            .sort_index()
        )

        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "overview_heat", [col_low, col_high]
        )

        _, ax = plt.subplots()
        ax.imshow(pivot.values, cmap=cmap, aspect="auto")

        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)

        if label:
            threshold = (pivot.values.max() + pivot.values.min()) / 2
            for i in range(len(pivot.index)):
                for j in range(len(pivot.columns)):
                    val = pivot.values[i, j]
                    text = f"{val:.1f}%" if perc else str(int(val))
                    color = "white" if val >= threshold else "black"
                    ax.text(j, i, text, ha="center", va="center", color=color, fontsize=8)

        if show_plot:
            plt.show()

        return ax

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
        _, ax = plt.subplots()
        ax.barh(sorted_result["variable"].astype(str), sorted_result[x])
        ax.set_xlabel(xaxis)
        ax.set_ylabel(yaxis)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(left=False, bottom=False)
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
        cols = [self.id_col, self.time]
        if color is not None:
            cols.append(color)

        dat_red = (
            self.df[cols]
            .dropna(subset=[self.id_col, self.time])
            .drop_duplicates()
            .sort_values([self.id_col, self.time])
            .reset_index(drop=True)
        )

        ids_sorted = sorted(dat_red[self.id_col].unique(), key=str)

        if color is not None:
            color_vals = sorted(dat_red[color].dropna().unique(), key=str)
            cmap = matplotlib.colormaps.get_cmap("tab10").resampled(max(len(color_vals), 1))
            color_map = {v: cmap(i) for i, v in enumerate(color_vals)}

        fig, ax = plt.subplots()

        for y_pos, id_val in enumerate(ids_sorted):
            id_data = dat_red[dat_red[self.id_col] == id_val].sort_values(self.time)
            times = id_data[self.time].tolist()

            for seg in _consecutive_segments(times):
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

        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
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
                bbox_to_anchor=(0.5, -0.2),
                ncol=len(color_vals),
                frameon=False,
            )
            fig.tight_layout()

        if show_plot:
            plt.show()

        return ax

    def overview_overlap(
        self,
        dat2: pd.DataFrame,
        dat2_id: str,
        dat1_name: str = "Data set 1",
        dat2_name: str = "Data set 2",
        plot_type: str = "bar",
        show_plot: bool = True,
    ) -> matplotlib.axes.Axes:
        """Plots the ID overlap between this data set and a second one.

        Args:
            dat2: Second data set to compare against.
            dat2_id: Column name of the ID variable in dat2.
            dat1_name: Label for this data set in the plot. Defaults to "Data set 1".
            dat2_name: Label for dat2 in the plot. Defaults to "Data set 2".
            plot_type: "bar" for a grouped bar chart, "venn" for a Venn diagram.
            show_plot: Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.axes.Axes: A plot visualising the overlap of the two data sets.

        Raises:
            ValueError: If plot_type is not "bar" or "venn".
        """
        if plot_type not in ("bar", "venn"):
            raise ValueError(f"plot_type must be 'bar' or 'venn', got {plot_type!r}")

        if plot_type == "bar":
            counts1 = self.df[self.id_col].value_counts().rename(dat1_name)
            counts2 = dat2[dat2_id].value_counts().rename(dat2_name)
            merged = pd.concat([counts1, counts2], axis=1).fillna(0).sort_index()

            ax = merged.plot(kind="bar", color=["#dceaf2", "#2A5773"], edgecolor="gray", width=0.7)
            ax.set_xlabel("Identifier")
            ax.set_ylabel("Count (absolute number of observations)")
            ax.set_title("Overlap of data sets")
            ax.legend([dat1_name, dat2_name])

            if show_plot:
                plt.show()
            return ax

        set1 = set(self.df[self.id_col].dropna())
        set2 = set(dat2[dat2_id].dropna())
        only1 = len(set1 - set2)
        only2 = len(set2 - set1)
        both = len(set1 & set2)

        _, ax = plt.subplots()
        ax.add_patch(mpatches.Circle((0.35, 0.5), 0.3, color="#dceaf2", alpha=0.9))
        ax.add_patch(mpatches.Circle((0.65, 0.5), 0.3, color="#2A5773", alpha=0.5))
        ax.text(0.2, 0.5, str(only1), ha="center", va="center", fontsize=14, fontweight="bold")
        ax.text(0.5, 0.5, str(both), ha="center", va="center", fontsize=14, fontweight="bold", color="white")
        ax.text(0.8, 0.5, str(only2), ha="center", va="center", fontsize=14, fontweight="bold")
        ax.text(0.25, 0.83, dat1_name, ha="center", va="center", fontsize=11)
        ax.text(0.75, 0.83, dat2_name, ha="center", va="center", fontsize=11)
        ax.set_xlim(0, 1)
        ax.set_ylim(0.1, 0.95)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Overlap of data sets")

        if show_plot:
            plt.show()
        return ax

    def overview_latex(
        self,
        obj: pd.DataFrame,
        title: str = "Time and scope of the sample",
        id_label: str = "Sample",
        time_label: str = "Time frame",
        crosstab: bool = False,
        cond1: str = "Condition 1",
        cond2: str = "Condition 2",
        save_out: bool = False,
        file_path: str | None = None,
        label: str = "tab:tab1",
        fontsize: str | None = None,
    ) -> str:
        """Generate a LaTeX table from an overview_tab or overview_crosstab result.

        Convenience wrapper around the standalone ``overview_latex`` function.
        For full documentation see ``overview_latex``.

        Args:
            obj: DataFrame returned by overview_tab or overview_crosstab (must have exactly 2 columns).
            title: Caption of the table.
            id_label: Header for the left column (ignored when crosstab=True).
            time_label: Header for the right column (ignored when crosstab=True).
            crosstab: If True, renders a cross-tabulation layout (obj must have exactly 2 rows).
            cond1: Label for the first condition (used when crosstab=True).
            cond2: Label for the second condition (used when crosstab=True).
            save_out: If True, write the LaTeX to file_path instead of printing.
            file_path: Destination .tex file path (required when save_out=True).
            label: LaTeX label for the table (e.g. "tab:tab1").
            fontsize: LaTeX font-size command without backslash (e.g. "small", "scriptsize").

        Returns:
            str: The generated LaTeX string.
        """
        return overview_latex(
            obj,
            title=title,
            id_label=id_label,
            time_label=time_label,
            crosstab=crosstab,
            cond1=cond1,
            cond2=cond2,
            save_out=save_out,
            file_path=file_path,
            label=label,
            fontsize=fontsize,
        )


def overview_crossplot(
    df: pd.DataFrame,
    id_col: str,
    time: str,
    cond1: str,
    cond2: str,
    threshold1: float,
    threshold2: float,
    xaxis: str = "Condition 1",
    yaxis: str = "Condition 2",
    label: bool = False,
    color: bool = False,
    dot_size: float = 20,
    fontsize: float = 8,
    show_plot: bool = True,
) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_crossplot. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_crossplot(
        cond1, cond2, threshold1, threshold2,
        xaxis, yaxis, label, color, dot_size, fontsize, show_plot,
    )


def overview_tab(df: pd.DataFrame, id_col: str, time: int) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_tab. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_tab()


def overview_crosstab(
    df: pd.DataFrame,
    id_col: str,
    time: str,
    cond1: str,
    cond2: str,
    threshold1: float,
    threshold2: float,
) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_crosstab. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_crosstab(cond1, cond2, threshold1, threshold2)


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


def overview_heat(
    df: pd.DataFrame,
    id_col: str,
    time: str,
    perc: bool = False,
    exp_total: int | None = None,
    xaxis: str = "Time frame",
    yaxis: str = "Sample",
    col_low: str = "#dceaf2",
    col_high: str = "#2A5773",
    label: bool = True,
    show_plot: bool = True,
) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_heat. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_heat(
        perc=perc,
        exp_total=exp_total,
        xaxis=xaxis,
        yaxis=yaxis,
        col_low=col_low,
        col_high=col_high,
        label=label,
        show_plot=show_plot,
    )


def overview_markdown(
    df: pd.DataFrame,
    id_col: str,
    time: str,
    title: str = "Time and scope of the sample",
    id_label: str = "Sample",
    time_label: str = "Time frame",
    file_path: str | None = None,
) -> str:
    """Backward-compatible accessor for Overview.overview_markdown. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_markdown(
        title=title,
        id_label=id_label,
        time_label=time_label,
        file_path=file_path,
    )


def overview_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible accessor for Overview.overview_summary. Deprecated since 0.2.0."""
    return Overview(df, None, None).overview_summary()


def overview_plot(
    df: pd.DataFrame,
    id_col: str,
    time: str,
    xaxis: str = "Time frame",
    yaxis: str = "Sample",
    asc: bool = True,
    color: str | None = None,
    dot_size: int = 2,
    show_plot: bool = True,
) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_plot. Deprecated since 0.2.0."""
    return Overview(df, id_col, time).overview_plot(
        xaxis=xaxis,
        yaxis=yaxis,
        asc=asc,
        color=color,
        dot_size=dot_size,
        show_plot=show_plot,
    )


def overview_overlap(
    dat1: pd.DataFrame,
    dat2: pd.DataFrame,
    dat1_id: str,
    dat2_id: str,
    dat1_name: str = "Data set 1",
    dat2_name: str = "Data set 2",
    plot_type: str = "bar",
    show_plot: bool = True,
) -> matplotlib.axes.Axes:
    """Backward-compatible accessor for Overview.overview_overlap. Deprecated since 0.2.0."""
    return Overview(dat1, dat1_id, None).overview_overlap(
        dat2,
        dat2_id=dat2_id,
        dat1_name=dat1_name,
        dat2_name=dat2_name,
        plot_type=plot_type,
        show_plot=show_plot,
    )


def overview_latex(
    obj: pd.DataFrame,
    title: str = "Time and scope of the sample",
    id_label: str = "Sample",
    time_label: str = "Time frame",
    crosstab: bool = False,
    cond1: str = "Condition 1",
    cond2: str = "Condition 2",
    save_out: bool = False,
    file_path: str | None = None,
    label: str = "tab:tab1",
    fontsize: str | None = None,
) -> str:
    """Generate a LaTeX table from an overview_tab or overview_crosstab result.

    Unlike other functions in this module, ``overview_latex`` is a standalone
    function rather than a method on ``Overview``, because it operates on the
    already-formatted output of ``overview_tab`` or ``overview_crosstab`` rather
    than on raw data. ``Overview.overview_latex`` delegates to this function.

    Args:
        obj: DataFrame returned by overview_tab or overview_crosstab (must have exactly 2 columns).
        title: Caption of the table.
        id_label: Header for the left column (ignored when crosstab=True).
        time_label: Header for the right column (ignored when crosstab=True).
        crosstab: If True, renders a cross-tabulation layout (obj must have exactly 2 rows).
        cond1: Label for the first condition (used when crosstab=True).
        cond2: Label for the second condition (used when crosstab=True).
        save_out: If True, write the LaTeX to file_path instead of printing.
        file_path: Destination .tex file path (required when save_out=True).
        label: LaTeX label for the table (e.g. "tab:tab1").
        fontsize: LaTeX font-size command without backslash (e.g. "small", "scriptsize").

    Returns:
        str: The generated LaTeX string.

    Raises:
        ValueError: If obj does not have exactly 2 columns, crosstab=True and obj does not have
            exactly 2 rows, or save_out=True without file_path.
    """
    if save_out and file_path is None:
        raise ValueError("file_path must be provided when save_out=True.")

    mat = obj.values

    if mat.shape[1] != 2:
        raise ValueError(
            "Data frame requires two columns that represent the time and scope "
            "dimension of the data. An overview_tab or overview_crosstab object is required."
        )

    if crosstab and mat.shape[0] != 2:
        raise ValueError(
            "A crosstab object must have exactly 2 rows (one per condition outcome)."
        )

    if not crosstab and mat.shape[0] == 2:
        warnings.warn(
            "Are you sure you want a table for time and scope conditions? "
            "For a crosstab, set crosstab=True.",
            UserWarning,
            stacklevel=2,
        )

    fontsize_mod = f"\\{fontsize}\n" if fontsize else ""
    today = date.today().isoformat()

    if not crosstab:
        output = (
            f"% Overview table generated in Python using overviewpy\n"
            f"% Table created on {today}\n"
            f"\\begin{{table}}[ht]\n"
            f" \\centering\n"
            f" \\caption{{{title}}}\n"
            f"\\label{{{label}}}\n"
            f"{fontsize_mod}"
            f"\\begin{{tabular}}{{ll}}\n"
            f" \\hline\n"
            f"{id_label} & {time_label} \\\\ \\hline\n"
        )
        output += "".join(f"{row[0]} & {row[1]} \\\\\n" for row in mat)
        output += "\\hline\n \\end{tabular}\n \\end{table}\n"
    else:
        output = (
            f"% Overview table generated in Python using overviewpy\n"
            f"% Table created on {today}\n"
            f"% Please add the following packages to your document preamble:\n"
            f"% \\usepackage{{multirow}}\n"
            f"% \\usepackage{{tabularx}}\n"
            f"% \\newcolumntype{{b}}{{X}}\n"
            f"% \\newcolumntype{{s}}{{>{{\\hsize=.5\\hsize}}X}}\n"
            f"\\begin{{table}}[ht]\n"
            f"\\caption{{{title}}}\n"
            f"\\label{{{label}}}\n"
            f"{fontsize_mod}"
            f"\\begin{{tabularx}}{{\\textwidth}}{{ssbb}}\n"
            f"\\hline & & \\multicolumn{{2}}{{c}}{{\\textbf{{{cond1}}}}} \\\\\n"
            f" & & \\textbf{{Fulfilled}} & \\textbf{{Not fulfilled}} \\\\\n"
            f" \\hline \\\\\n"
            f" \\multirow{{2}}{{*}}{{\\textbf{{{cond2}}}}}"
            f" & \\textbf{{Fulfilled}} &\n"
            f"{mat[0, 0]} & {mat[0, 1]}\\\\\n"
            f" \\\\ \\hline \\\\\n"
            f" & \\textbf{{Not fulfilled}} & "
            f"{mat[1, 0]} & {mat[1, 1]}\\\\\n"
            f"\\hline \\\\\n"
            f" \\end{{tabularx}}\n"
            f" \\end{{table}}\n"
        )

    if save_out:
        with open(file_path, "w") as f:
            f.write(output)

    return output
