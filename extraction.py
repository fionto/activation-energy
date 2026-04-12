from pathlib import Path


# costruisco Path partendo dal parent del percorso relativo allo script
# lo script è posizionato alla radice dove ci sono le cartelle delle misure
raw_dataset_path = Path(__file__).parent / 'data'
txt_file_path = raw_dataset_path / 'E14_FS' / 'E14_FS_4E-2_675C_100426_164801.txt'

KEY_VOLTAGE = 'Voltage'
KEY_CURRENT = 'Current'
KEY_STD = 'std_dev'


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


def parse_row(row_str: str) -> dict:
     
    fields = [f.strip() for f in row_str.split(',')]

    voltage_str, current_str, std_dev_str = fields[:3]

    return {
        KEY_VOLTAGE : _safe_float(voltage_str),
        KEY_CURRENT : _safe_float(current_str),
        KEY_STD : _safe_float(std_dev_str),
    }


def build_collection() -> dict:
    
    return {
        KEY_VOLTAGE : [],
        KEY_CURRENT : [],
        KEY_STD : [],
    }


def append_point(collection: dict[str, list[float]], reading: dict[str, float]) -> None:
    """Appends values from a single reading to the corresponding lists in a collection.

    Iterates explicitly over the keys of the `collection` dictionary to ensure only
    pre-defined fields are processed. Any keys present in `reading` but missing from
    `collection` are silently ignored, maintaining a strict filter on required data.
    If a required key is missing from `reading`, `float('nan')` is appended to preserve
    list length alignment and allow safe mathematical propagation later.

    This function modifies the `collection` dictionary in-place and returns None,
    following standard Python conventions for mutator methods.

    Args:
        collection: A dictionary where keys are measurement names (e.g., 'voltage',
            'current') and values are lists of floats to be extended.
        reading: A dictionary representing a single data point, containing keys that
            may or may not match the collection's keys. Values are floats.

    Returns:
        None
    """
    # I iterate over collection.keys() instead of reading.items() to explicitly
    # filter only the parameters I actually need. This makes the function future-proof:
    # if 'reading' later includes extra fields (e.g., temperature, pressure),
    # they will be silently ignored without raising errors or cluttering the pipeline.
    for key in collection.keys():
        # Using .get() with a NaN fallback ensures list lengths stay perfectly aligned
        # even if a field is missing in the current reading. NaN will propagate
        # safely through future mathematical operations instead of crashing the script.
        collection[key].append(reading.get(key, float('nan')))


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