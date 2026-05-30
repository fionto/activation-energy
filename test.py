from pathlib import Path
import validators
import constants

# Building the Path object starting from where the script resides:
# the script is located at the project folder root
# the measurement (data) directory is located in a subfolder
#raw_dataset_csv = '20260417_084545_UH70FS_P4E-2torr_T020C_BA.txt'
#raw_dataset_path = raw_dataset_dir / raw_dataset_csv

directory_path = (Path(__file__).parent / 'data' / 'UH70-FS').resolve()
txt_files = sorted(directory_path.glob("*.txt"))


for f in txt_files:
    is_validated = validators.validate_filename(f.name, constants.FILENAME_PATTERN)
    print(f"{f.name} validation: {is_validated}")