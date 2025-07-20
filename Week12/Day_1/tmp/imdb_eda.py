import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv('https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv')

# 1. Data Overview & Quality Assessment

def data_overview(df):
    # Dataset shape
    print("Dataset Shape:", df.shape)
    
    # Column types and basic info
    print("\nData Types:")
    print(df.dtypes)
    
    print("\nFirst five rows:")
    print(df.head())
    
    print("\nDataFrame info:")
    df.info()

    # Missing values analysis
    missing_values = df.isnull().sum()
    print("\nMissing Values Analysis:")
    print(missing_values)
    
    # Visualization of missing values
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title('Missing Values Heatmap')
    plt.savefig('missing_values_heatmap.png')
    plt.close()
    
    # Statistical summary of numerical variables
    print("\nStatistical Summary:")
    print(df.describe())

    # Data quality issues
    observations = []
    if df.isnull().sum().sum() > 0:
        observations.append("There are missing values in the dataset.")
    if df.duplicated().sum() > 0:
        observations.append("There are duplicate entries in the dataset.")
    
    if len(observations) > 0:
        print("\nData Quality Issues:")
        for obs in observations:
            print("-", obs)
    else:
        print("\nNo significant data quality issues detected.")

# Run data overview function
data_overview(df)