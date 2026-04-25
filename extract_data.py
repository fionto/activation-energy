from pathlib import Path
from datetime import datetime
import pickle


# CONSTANTS
# METADATA: Information about the environment (Sample ID, Timestamp, P, T)
# contains geometric information on how the measurement was spatially performed 
# (Van Der Pauw alignement)
METADATA = "metadata" # container name
KEY_SAMPLE = "sample"
KEY_TIMESTAMP = "timestamp"
KEY_PRESSURE = "pressure_torr"
KEY_TEMPERATURE = "temperature_k"
KEY_GEOMETRY = 'alignment'
# DATA: Contains the arrays of measured values
DATA = "curves" # container name, could be more than 1 curve if Van Der Pauw
KEY_VOLTAGE = "Voltage"
KEY_CURRENT = "Current"
KEY_STD = "std_dev"

CELSIUS_TO_KELVIN = 273.15


# Building the Path object starting from where the script resides:
# the script is located at the project folder root 
# the measurement (data) directory is located in a subfolder
dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'

# Dumping in the same folder I am parsing
pickle_output_path = dataset_dir / 'iv_curves_UH70FS.pkl'


def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.
    Returns float('nan') if conversion fails, to allow error propagation.
    """
    try:
        return float(value_str.strip())
    except ValueError:
        return float("nan")


def check_alignment(alignment_str: str | None) -> str | None:
    if alignment_str is None:
        return None
    match alignment_str:
        case 'AB': return "horizontal"
        case 'BA': return "vertical"
        case _: 
            raise ValueError(f"Invalid VdP configuration: {alignment_str}")


def parse_filename(filename: str) -> dict:
    """
    Parses a measurement filename with the structure:

        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt

    where the Van der Pauw configuration suffix (AB or BA) is optional.

    Extracts metadata from the filename and returns a dictionary containing:
        - sample name
        - timestamp (as a datetime object)
        - pressure (in Torr)
        - temperature (in Kelvin)
        - configuration (str: 'AB', 'BA', or None if not present)

    """
    filename = filename.removesuffix(".txt") # only working from Python 3.9+
    parts = filename.split('_')
    
    if len(parts) not in {5, 6}:
        raise ValueError(
            f"Expected filename with 5 or 6 fields separated by '_', "
            f"got {len(parts)}: {filename}"
        )
    
    date_str, time_str, sample_str, pressure_str, temp_str, *extra = parts
    alignment_raw = extra[0] if extra else None
    alignment = check_alignment(alignment_raw)
    
    timestamp = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
    pressure_torr = _safe_float(pressure_str.removeprefix('P').removesuffix('torr'))
    temperature_k = _safe_float(temp_str.removeprefix('T').removesuffix('C')) + CELSIUS_TO_KELVIN 
    alignment = check_alignment(alignment_raw)
    
    return {
        KEY_SAMPLE : sample_str,
        KEY_TIMESTAMP : timestamp,
        KEY_PRESSURE : pressure_torr,
        KEY_TEMPERATURE : temperature_k,
        KEY_GEOMETRY : alignment,
    }
    

def parse_row(row_str: str) -> dict:
    """
    Parse a single CSV row string into a dictionary of numeric values.
    """
     
    csv_fields = [f.strip() for f in row_str.split(',')]

    # TODO: improve control of corrupted/malformed .csv files
    if len(csv_fields) < 3:
        raise ValueError(f"Malformed row: {row_str}")

    voltage_str, current_str, std_dev_str = csv_fields[:3]

    return {
        KEY_VOLTAGE : _safe_float(voltage_str),
        KEY_CURRENT : _safe_float(current_str),
        KEY_STD : _safe_float(std_dev_str),
    }


def extract_curve_points(measurement_file: Path) -> list[dict]:
    """
    It reads a measurement file and returns the points as a dictionary list.

    Each element has the keys KEY_VOLTAGE, KEY_CURRENT, and KEY_STD.
    Responsibility for how these points are accumulated lies with the caller.
    """
    
    # First check: do not want to open files when size is 0 bytes. Common in LabVIEW.
    if measurement_file.stat().st_size == 0:
        # just return empty to skip processing
        return []
    
    measurements = []

    with open(measurement_file, 'r', encoding='utf-8') as txt_data:
        
        # Second check: files with just the header. Also common in LabVIEW.
        try:
            next(txt_data)  # skip header
        except StopIteration:
            # File is empty; return the empty list immediately
            return measurements

        for line_str in txt_data:
            line_str = line_str.strip()
            if not line_str:
                continue
            measurements.append(parse_row(line_str))

    return measurements


def transpose_curve_data(points: list[dict]) -> dict[str, list[float]]:
    """
    Transposes a list of row-dictionaries into a dictionary of column-lists.
    Example: [{'V': 1, 'I': 2}, {'V': 3, 'I': 4}] -> {'V': [1, 3], 'I': [2, 4]}
    """
    # Initializing the structure based on the known keys
    columnar_data = {
        KEY_VOLTAGE: [],
        KEY_CURRENT: [],
        KEY_STD: [],
    }

    for point in points:
        for key in columnar_data:
            columnar_data[key].append(point[key])

    return columnar_data


def extract_from_dir(directory_path: Path) -> list[dict]:
    """
    Iterates over the .txt files in the directory and assembles the list of curves.

    Each element is a dictionary with the keys METADATA and DATA.
    """ 
    curve_dataset = []    
    
    # filename starts with date, so it should be ordered chronologically
    # the folder might contain other files, in the future I should filter better
    for file in sorted(directory_path.glob("*.txt")):
      
        # using helper functions I extract metadata from filenames and
        # raw data from the content of .txt files
        metadata = parse_filename(file.name)
        raw_points = extract_curve_points(file)

        # organize my list of dict into a dictionary of column-lists
        columnar_data = transpose_curve_data(raw_points)
        
        # assemble final object, might want to change it to pandas or numpy later
        curve_dataset.append({
            METADATA: metadata,
            DATA: columnar_data
        })

    return curve_dataset


def dump_data(save_path: Path, data: list[dict]):
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Saved {len(data)} curves to {save_path}")


def main():

    if not dataset_dir.exists():
        # Using SystemExit is a clean way to quit with an error message
        raise SystemExit(f"Error: Directory not found at {dataset_dir}")
    
    if not dataset_dir.is_dir():
        raise SystemExit(f"Error: {dataset_dir} exists but is not a directory.")
    
    data = extract_from_dir(dataset_dir)
    dump_data(pickle_output_path, data)


if __name__ == "__main__":
    main()