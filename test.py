from pathlib import Path

# Building the Path object starting from where the script resides:
# the script is located at the project folder root
# the measurement (data) directory is located in a subfolder
#raw_dataset_csv = '20260417_084545_UH70FS_P4E-2torr_T020C_BA.txt'
#raw_dataset_path = raw_dataset_dir / raw_dataset_csv

raw_dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'

if not raw_dataset_dir.exists():
    # Using SystemExit is a clean way to quit with an error message
    raise SystemExit(f"Error: Directory not found at {raw_dataset_dir}")

if not raw_dataset_dir.is_dir():
    raise SystemExit(f"Error: {raw_dataset_dir} exists but is not a directory.")

csv_datasets = []

# filename starts with date, so it should be ordered chronologically
# the folder might contain other files, in the future should filter better
for file in sorted(raw_dataset_dir.glob("*.txt")):
    print(file.name)