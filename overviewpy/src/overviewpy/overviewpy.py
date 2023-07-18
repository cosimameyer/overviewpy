import matplotlib.pyplot as plt
import pandas as pd

def overview_tab(df, id, time):
    df2 = df.dropna(subset=['id']).copy()
    
    if len(df2) != len(df):
        print("There is a missing value in your id variable. The missing value is automatically deleted.")
        
    if len(df2) == len(df): 
        df_no_dup = df.filter(items=[id, time]).drop_duplicates()
        
        if len(df_no_dup) == len(df):
            df['time'] = pd.to_datetime(df['time'])  # Convert 'time' column to datetime if it's not already

            # Sort the DataFrame by 'id' and 'time' columns
            df.sort_values(['id', 'time'], inplace=True)

            # Calculate the time differences in years within each group
            df['consecutive_years'] = df.groupby('id')['time'].diff().dt.days / 365
            
            df['consecutive_years'] = df.groupby('id')['consecutive_years'].apply(lambda x: '-'.join(str(int(i)) for i in x.cumsum().fillna(0)))


            return df 
        else:
            print("There are some duplicates. Make sure to aggregate first.")
            

def overview_na(df):
    return df.isna().sum().plot(kind="bar")