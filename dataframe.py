from pathlib import Path
import pickle
# data analysis
import pandas as pd


raw_dataset_path = Path(__file__).parent / 'data' / 'E14_FS'
save_path = raw_dataset_path / 'iv_curves_E14FS.pkl'


with open(save_path, 'rb') as f:
    datasets = pickle.load(f)

    first_curve = datasets[0]['data']

    # Convert to DataFrame (best for analysis)
    df = pd.DataFrame(first_curve)

    # Quick peek at the DataFrame.
    # By default, it shows the first 5 rows
    print(df.head())
    
    # quick way to get the dimensions of a DataFrame 
    # (number_of_rows, number_of_columns)
    print(f"\nData shape: {df.shape}") 
    
    print(f"Voltage range: {df['Voltage'].min():.0f} to {df['Voltage'].max():.0f} V")