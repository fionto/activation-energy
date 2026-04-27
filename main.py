import pandas as pd
from datetime import datetime
from pathlib import Path
from models import Measurement, Metadata, Dataset
from constants import ColumnNames
import utils
import loaders

# Building the Path object starting from where the script resides:
# the script is located at the project folder root
# the measurement (data) directory is located in a subfolder
dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'
dataset_csv = '20260417_084545_UH70FS_P4E-2torr_T020C_BA.txt'
dataset_path = dataset_dir / dataset_csv

# Loading metadata (Metadata Object)
metadata = loaders.load_metadata_csv(dataset_path.name)
# Loading measurement (Measurement Object)
measurement = loaders.load_measurement_csv(dataset_path)

# I need a DataFrame (df) to use pandas' libraries
df = Measurement.to_dataframe(measurement)

print(metadata.summary())
print(df.head())