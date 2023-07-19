import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def _combine_years(years):
  min_year = min(years.dt.year)
  max_year = max(years.dt.year)
  if min_year == max_year:
    return str(min_year)
  else:
    return f"{str(min_year)}-{str(max_year)}"

def overview_tab(df, id, time):

    df2 = df.dropna(subset=['id']).copy()
    if len(df2) != len(df):
        print("There is a missing value in your id variable. The missing value is automatically deleted.")
        
    df_no_dup = df2.filter(items=[id, time]).drop_duplicates()
    
    if len(df_no_dup) == len(df2):
      df['time'] = pd.to_datetime(df['time'], format='%Y')  # Convert 'time' column to datetime with year format

      # Sort the DataFrame by 'id' and 'time' columns
      df.sort_values(['id', 'time'], inplace=True)

      overview = df.groupby('id')['time'].apply(_combine_years)

      return pd.DataFrame(overview).reset_index()

    else:
        print("There are some duplicates. Make sure to aggregate first.")
            

def overview_na(df):
    return df.isna().sum().plot(kind="bar")