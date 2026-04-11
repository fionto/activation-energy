from pathlib import Path


# costruisco Path partendo dal parent del percorso relativo allo script
# lo script è posizionato alla radice dove ci sono le cartelle delle misure
raw_dataset_path = Path(__file__).parent / 'E14_FS'
txt_file_path = raw_dataset_path / 'E14_FS_4E-2_675C_100426_164801.txt'


def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.

    This function handles whitespace stripping and catches conversion errors 
    gracefully to prevent pipeline crashes on dirty data.

    Args:
        value_str (str): The string value to convert (e.g., " 18.9 ", "").

    Returns:
        float: The converted floating-point number. If conversion fails 
            (e.g., empty string or non-numeric text), returns float('nan').
    """
    try:
        return float(value_str.strip())
    except ValueError:
        # I chose 'nan' instead of 0.0 because 'nan' propagates through math operations.
        return float("nan")


# In questa funzione voglio mantenere solamente Voltage, Current, Standard Deviation
def parse_row(row_str: str) -> dict | None:
    
    if not row_str or not row_str.strip():
        return None
    
    fields = [f.strip() for f in row_str.split(',')]

    voltage_str, current_str, std_dev_str = fields[:3]

    return {
        'voltage' : _safe_float(voltage_str),
        'current' : _safe_float(current_str),
        'std_dev' : _safe_float(std_dev_str),
    }


def build_collection():
    
    return {
        'voltage' : [],
        'current' : [],
        'std_dev' : [],
    }


def append_point(collection, single_reading):
    collection['voltage'].append(single_reading['voltage'])
    collection['current'].append(single_reading['current'])
    collection['std_dev'].append(single_reading['std_dev'])


def run_extraction(file_path: Path):

    collection = build_collection()

    with open(txt_file_path, 'r', encoding='utf-8') as txt_data:
        header_line = next(txt_data)

        for raw_line in txt_data:
            raw_line = raw_line.strip()

            if not raw_line:
                continue

            append_point(collection, parse_row(raw_line))
    
    return collection

measurement = run_extraction(txt_file_path)

print(measurement)