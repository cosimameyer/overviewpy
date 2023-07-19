import matplotlib.pyplot as plt
import matplotlib.figure
import pandas as pd

def overview_tab(df: pd.DataFrame, id: str, time: str) -> pd.DataFrame:
    """Generates a tabular overview of the sample (and returns a data frame). 
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

    df2 = df.dropna(subset=['id']).copy()
    if len(df2) != len(df):
        print("There is at least one missing value in your id variable. The missing value is automatically deleted.")
        
    df_no_dup = df2.filter(items=[id, time]).drop_duplicates()
    
    if len(df_no_dup) == len(df2):
        df_sorted = df_no_dup.sort_values([id, time])
      
        # Group the DataFrame by the ID column
        grouped = df_sorted.groupby(id)
        
        # Initialize the combined column
        df['time_frame'] = df_no_dup[time].astype(str)
        
        # Check if numbers within each group are consecutive and combine them
        for group_name, group_df in grouped:
            numbers = group_df[time].tolist()

            combined_str = ""

            if len(numbers) > 1:
                consecutive_ranges = []
                current_range = [numbers[0]]

                for i in range(1, len(numbers)):
                    if numbers[i] == numbers[i-1] + 1:
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
            
        return df_no_dup[['id', 'time_frame']].sort_values([id]).drop_duplicates()

    else:
        print("There are some duplicates. Make sure to aggregate first.")
            
def overview_na(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """Plots an overview of missing values by variable.

    Args:
        df (pd.DataFrame): Input data frame

    Returns:
        matplotlib.figure.Figure: Bar plot visualizing the number of missing values per variable
    """
    ax = df.isna().sum().plot(kind="barh")
    ax.set_xlabel("Count")
    ax.set_ylabel("Columns")
    plt.title("Missing Values Overview")
    plt.show()