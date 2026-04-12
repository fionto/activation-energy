from pathlib import Path

# I build the Path object starting from where the script resides:
# The script is located at the project folder root 
# the measurement (data) directory is located in a subfolder
raw_dataset_path = Path(__file__).parent / 'data'
txt_file_path = raw_dataset_path / 'E14_FS' / '20260408_123516_E14FS_P4E-2mbar_T020C.txt'


KEY_VOLTAGE = 'Voltage'
KEY_CURRENT = 'Current'
KEY_STD = 'std_dev'


def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.
    Returns float('nan') if conversion fails, to allow error propagation.
    """
    try:
        return float(value_str.strip())
    except ValueError:
        return float("nan")
    

def parse_row(row_str: str) -> dict:
    """
    Parse a single CSV row string into a dictionary of numeric values.
    """
     
    fields = [f.strip() for f in row_str.split(',')]

    voltage_str, current_str, std_dev_str = fields[:3]

    return {
        KEY_VOLTAGE : _safe_float(voltage_str),
        KEY_CURRENT : _safe_float(current_str),
        KEY_STD : _safe_float(std_dev_str),
    }


def append_point(collection: dict[str, list[float]], reading: dict[str, float]) -> None:
    """
    Appends values from a single reading to the corresponding lists in a collection.
    """

    for key_r, val_r in reading.items():
        if key_r in collection and isinstance(collection[key_r], list):
            collection[key_r].append(val_r)
        else:
            collection[key_r] = [val_r]


def build_collection() -> dict:
    
    return {
        KEY_VOLTAGE : [],
        KEY_CURRENT : [],
        KEY_STD : [],
    }


def run_extraction(file_path: Path):

    collection = build_collection()

    with open(file_path, 'r', encoding='utf-8') as txt_data:
        
        header_line = next(txt_data)

        for raw_line in txt_data:
            raw_line = raw_line.strip()

            if not raw_line:
                continue
            
            append_point(collection, parse_row(raw_line))
    
    return collection

measurement = run_extraction(txt_file_path)

print(measurement)