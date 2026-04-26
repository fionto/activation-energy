from pathlib import Path
import datetime
import pickle

HEADERS = (
    "sample",
    "timestamp",
    "pressure_torr",
    "temperature_k",
    "alignment",
)

COL_WIDTH = 25
TABLE_FORMAT = ("{:<" + str(COL_WIDTH) + "}") * len(HEADERS)


raw_dataset_path = Path(__file__).parent / 'data' / 'UH70-FS'
save_path = raw_dataset_path / 'iv_curves_UH70FS.pkl'


def print_headers():
    # This aligns every column to a width of 15 characters
    print(TABLE_FORMAT.format(*HEADERS))


def print_row(row: dict):
    ordered_values = []

    for h in HEADERS:
        if not isinstance(row[h], datetime.date):
            ordered_values.append(row[h])
        else:
            ordered_values.append(row[h].strftime("%y-%m-%d %H:%M"))

    print(TABLE_FORMAT.format(*ordered_values))


def print_data(data: list[dict]):
    for row in data:
        values = row['metadata']
        print_row(values)
            

def main():
    print_headers()
    with open(save_path, 'rb') as f:
       data = pickle.load(f)
       print_data(data)

if __name__ == "__main__":
    main()