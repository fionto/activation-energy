from pathlib import Path
from datetime import datetime
import pickle


raw_dataset_path = Path(__file__).parent / 'data' / 'UH70-FS'
save_path = raw_dataset_path / 'elaborated_UH70FS.pkl'

with open(save_path, 'rb') as f:
    data = pickle.load(f)

print(data[0])