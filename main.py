import pandas as pd
from datetime import datetime
from pathlib import Path
from models import Measurement, Metadata, Elaborations, Dataset
from constants import ColumnNames
import utils
import loaders
import processes

# Building the Path object starting from where the script resides:
# the script is located at the project folder root
# the measurement (data) directory is located in a subfolder
raw_dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'
raw_dataset_csv = '20260417_084545_UH70FS_P4E-2torr_T020C_BA.txt'
raw_dataset_path = raw_dataset_dir / raw_dataset_csv

extracted_dataset = loaders.load_dataset_csv(raw_dataset_path)

print(extracted_dataset.report())