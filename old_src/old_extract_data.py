from pathlib import Path
from datetime import datetime
from typing import TypedDict
import pickle

CELSIUS_TO_KELVIN = 273.15

# TypedDict definitions
# METADATA: Information about the environment (Sample ID, Timestamp, P, T)
# contains geometric information on how the measurement was spatially performed
# (Van Der Pauw alignment)
class Metadata(TypedDict):
    sample: str
    timestamp: datetime
    pressure_torr: float
    temperature_k: float
    alignment: str | None


# SINGLE POINT: how a single row from .txt file is originally stored
class Point(TypedDict):
    voltage: float
    current: float
    std_dev: float


# DATA: Contains the arrays of measured values
class Curves(TypedDict):
    voltages: list[float]
    currents: list[float]
    std_devs: list[float]


# COMPLETE DATASET: With metadata and actual measured data
class Dataset(TypedDict):
    Metadata: Metadata
    Curves: Curves


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
    """
    Validates and normalizes Van der Pauw alignment configuration.

    Args:
        alignment_str: Raw alignment string from filename ('AB', 'BA', or None)

    Returns:
        Normalized alignment string ('horizontal', 'vertical', or None)

    Raises:
        ValueError: if alignment_str is not 'AB', 'BA', or None
    """
    if alignment_str is None:
        return None
    match alignment_str:
        case 'AB':
            return "horizontal"
        case 'BA':
            return "vertical"
        case _:
            raise ValueError(f"Invalid VdP configuration: {alignment_str}")


def parse_filename(filename: str) -> Metadata:
    """
    Parses a measurement filename with the structure:

        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt

    where the Van der Pauw configuration suffix (AB or BA) is optional.

    Extracts metadata from the filename and returns a dictionary containing:
        - sample name
        - timestamp (as a datetime object)
        - pressure (in Torr)
        - temperature (in Kelvin)
        - alignment (str: 'horizontal', 'vertical', or None if not present)

    Args:
        filename: The measurement filename to parse

    Returns:
        Metadata dictionary

    Raises:
        ValueError: if filename format is invalid
    """
    filename = filename.removesuffix(".txt")  # only working from Python 3.9+
    parts = filename.split('_')

    if len(parts) not in {5, 6}:
        raise ValueError(
            f"Expected filename with 5 or 6 fields separated by '_', "
            f"got {len(parts)}: {filename}"
        )

    date_str, time_str, sample_str, pressure_str, temp_str, *extra = parts
    alignment_raw = extra[0] if extra else None

    timestamp = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
    pressure_torr = _safe_float(pressure_str.removeprefix('P').removesuffix('torr'))
    temperature_k = _safe_float(temp_str.removeprefix('T').removesuffix('C')) + CELSIUS_TO_KELVIN
    alignment = check_alignment(alignment_raw)

    return {
        'sample': sample_str,
        'timestamp': timestamp,
        'pressure_torr': pressure_torr,
        'temperature_k': temperature_k,
        'alignment': alignment,
    }


def parse_row(row_str: str) -> Point:
    """
    Parse a single CSV row string into a dictionary of numeric values.

    Args:
        row_str: A comma-separated string with at least 3 numeric fields

    Returns:
        Point dictionary with voltage, current, and std_dev

    Raises:
        ValueError: if the row has fewer than 3 fields
    """
    csv_fields = [f.strip() for f in row_str.split(',')]

    # TODO: improve control of corrupted/malformed .csv files
    if len(csv_fields) < 3:
        raise ValueError(f"Malformed row: {row_str}")

    voltage_str, current_str, std_dev_str = csv_fields[:3]

    return {
        'voltage': _safe_float(voltage_str),
        'current': _safe_float(current_str),
        'std_dev': _safe_float(std_dev_str),
    }


def extract_curve_points(measurement_file: Path) -> list[Point]:
    """
    Reads a measurement file and returns the points as a dictionary list.

    Each element has the keys 'voltage', 'current', and 'std_dev'.
    Responsibility for how these points are accumulated lies with the caller.

    Args:
        measurement_file: Path to the measurement file

    Returns:
        List of Point dictionaries, empty if file is empty or only has header
    """

    # First check: do not want to open files when size is 0 bytes. Common in LabVIEW.
    if measurement_file.stat().st_size == 0:
        return []

    measurements: list[Point] = []

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


def transpose_curve_data(points: list[Point]) -> Curves:
    """
    Transposes a list of row-dictionaries into a dictionary of column-lists.

    Example:
        [{'voltage': 1, 'current': 2}, {'voltage': 3, 'current': 4}]
        ->
        {'voltages': [1, 3], 'currents': [2, 4]}

    Args:
        points: List of Point dictionaries

    Returns:
        Curves dictionary with columnar data
    """
    columnar_data: Curves = {
        'voltages': [],
        'currents': [],
        'std_devs': [],
    }

    for point in points:
        columnar_data['voltages'].append(point['voltage'])
        columnar_data['currents'].append(point['current'])
        columnar_data['std_devs'].append(point['std_dev'])

    return columnar_data


def extract_from_dir(directory_path: Path) -> list[Dataset]:
    """
    Iterates over the .txt files in the directory and assembles the list of curves.

    Each element is a dictionary with the keys 'Metadata' and 'Curves'.

    Args:
        directory_path: Path to directory containing measurement .txt files

    Returns:
        List of Dataset dictionaries
    """
    curve_dataset: list[Dataset] = []

    # filename starts with date, so it should be ordered chronologically
    # the folder might contain other files, in the future should filter better
    for file in sorted(directory_path.glob("*.txt")):

        # using helper functions to extract metadata from filenames and
        # raw data from the content of .txt files
        metadata = parse_filename(file.name)
        raw_points = extract_curve_points(file)

        # organize list of dicts into a dictionary of column-lists
        columnar_data = transpose_curve_data(raw_points)

        # assemble final object, might want to change it to pandas or numpy later
        curve_dataset.append({
            'Metadata': metadata,
            'Curves': columnar_data,
        })

    return curve_dataset


def dump_data(save_path: Path, data: list[Dataset]) -> None:
    """
    Serializes the dataset list to a pickle file.

    Args:
        save_path: Path where to save the pickle file
        data: List of Dataset objects to serialize
    """
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Saved {len(data)} curves to {save_path}")


def main() -> None:
    """
    Main entry point: loads measurement data from disk and saves as pickle.
    """

    # Building the Path object starting from where the script resides:
    # the script is located at the project folder root
    # the measurement (data) directory is located in a subfolder
    dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'

    # Dumping in the same folder I am parsing
    pickle_output_path = dataset_dir / 'iv_curves_UH70FS.pkl'

    if not dataset_dir.exists():
        # Using SystemExit is a clean way to quit with an error message
        raise SystemExit(f"Error: Directory not found at {dataset_dir}")

    if not dataset_dir.is_dir():
        raise SystemExit(f"Error: {dataset_dir} exists but is not a directory.")

    data = extract_from_dir(dataset_dir)
    dump_data(pickle_output_path, data)


if __name__ == "__main__":
    main()