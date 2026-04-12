from pathlib import Path
from datetime import datetime
import pickle


# I build the Path object starting from where the script resides:
# The script is located at the project folder root 
# the measurement (data) directory is located in a subfolder
raw_dataset_path = Path(__file__).parent / 'data' / 'E14_FS'

# dumping in the same folder I am parsing
save_path = raw_dataset_path / 'iv_curves_E14FS.pkl'


KEY_VOLTAGE = 'Voltage'
KEY_CURRENT = 'Current'
KEY_STD = 'std_dev'
CELSIUS_TO_KELVIN = 273.15


def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.
    Returns float('nan') if conversion fails, to allow error propagation.
    """
    try:
        return float(value_str.strip())
    except ValueError:
        return float("nan")


def parse_filename(raw_filename: str) -> dict:
    """
    Parses a filename with the structure:
    YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE.txt
    
    Returns a dictionary with pressure in mbar and temperature in Kelvin.
    """
    filename = raw_filename.removesuffix(".txt")
    parts = filename.split('_')
    
    if len(parts) != 5:
        raise ValueError(
            f"Expected filename with 5 fields separated by '_', "
            f"got {len(parts)}: {raw_filename}"
        )
    
    date_str, time_str, sample_str, pressure_str, temperature_str = parts
    
    timestamp = datetime.fromisoformat(date_str + 'T' + time_str)
    pressure_mbar = _safe_float(pressure_str.removeprefix('P').removesuffix("mbar"))
    temperature_k = _safe_float(temperature_str.removeprefix('T').removesuffix('C')) + CELSIUS_TO_KELVIN
    
    return {
        'sample': sample_str,
        'timestamp': timestamp,
        'pressure_mbar': pressure_mbar,
        'temperature_k': temperature_k,
    }
    

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


def extract_curve_points(file_path: Path, measurement_data: dict):

    with open(file_path, 'r', encoding='utf-8') as txt_data:
        
        next(txt_data)

        for raw_line in txt_data:
            raw_line = raw_line.strip()

            if not raw_line:
                continue
            
            append_point(measurement_data, parse_row(raw_line))


def extract_from_dir(directory_path: Path):
    
    data_from_dir = []    
    
    for file in directory_path.iterdir():
        
        if file.suffix == '.txt':
            measurement_data = parse_filename(file.name)
            extract_curve_points(file, measurement_data)
            data_from_dir.append(measurement_data)

    return data_from_dir

# Save your data (your list of dictionaries)
with open(save_path, 'wb') as f:
    pickle.dump(extract_from_dir(raw_dataset_path), f)