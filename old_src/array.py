from pathlib import Path
import pickle
# data analysis
import numpy as np

raw_dataset_path = Path(__file__).parent / 'data' / 'E14_FS'
save_path = raw_dataset_path / 'iv_curves_E14FS.pkl'

with open(save_path, 'rb') as f:
    datasets = pickle.load(f)
    first_curve = datasets[0]

# Extract the arrays from the loaded file
V = np.array(first_curve['data']['Voltage']) # array from numpy
I = np.array(first_curve['data']['Current'])
sd = np.array(first_curve['data']['std_dev'])

print(f"Successfully loaded {V.shape[0]} data points.")
print(sd)