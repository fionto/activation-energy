from pathlib import Path

raw_dataset_path = Path(__file__).parent / 'data' / 'E14_FS'

for file in raw_dataset_path.iterdir():
    if file.suffix == '.txt':
        print(file.name)