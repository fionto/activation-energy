from pathlib import Path
from datetime import datetime
import pickle


raw_dataset_path = Path(__file__).parent / 'data' / 'E14_FS'
save_path = raw_dataset_path / 'iv_curves_E14FS.pkl'

with open(save_path, 'rb') as f:
    data = pickle.load(f)
    print(type(data))
    print(data)