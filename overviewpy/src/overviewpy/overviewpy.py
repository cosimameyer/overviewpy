import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def _combine_years(years):
    if years.isnull().all() or len(years) == 1:
        return str(int(years.iloc[0].year))
    else:
        first_year = years.iloc[0].year
        last_year = years.iloc[-1].year
        if last_year - first_year == len(years) - 1:
            return str(first_year) + '-' + str(last_year)
        else:
            return str(int(years.iloc[0].year))

def overview_tab(df, id, time):

    df2 = df.dropna(subset=['id']).copy()
    if len(df2) != len(df):
        print("There is a missing value in your id variable. The missing value is automatically deleted.")
        
    df_no_dup = df2.filter(items=[id, time]).drop_duplicates()
    if len(df_no_dup) == len(df2):
      df['time'] = pd.to_datetime(df['time'], format='%Y')  # Convert 'time' column to datetime with year format

      # Sort the DataFrame by 'id' and 'time' columns
      df.sort_values(['id', 'time'], inplace=True)

      # Calculate the time differences in years within each group
      df['consecutive_years'] = df.groupby('id')['time'].diff().dt.days / 365

      # Create a function to combine consecutive years as 'YYYY-YYYY'

      # Convert consecutive years to the desired format
      df['years'] = df.groupby('id')['time'].apply(_combine_years)

      return df
    else:
        print("There are some duplicates. Make sure to aggregate first.")
            

def overview_na(df):
    return df.isna().sum().plot(kind="bar")