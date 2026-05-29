from pathlib import Path

# Building the Path object starting from where the script resides:
# the script is located at the project folder root
# the measurement (data) directory is located in a subfolder
#raw_dataset_csv = '20260417_084545_UH70FS_P4E-2torr_T020C_BA.txt'
#raw_dataset_path = raw_dataset_dir / raw_dataset_csv

directory_path = (Path(__file__).parent / 'data' / 'UH70-FS').resolve()

for p in directory_path.iterdir():
    print(p)