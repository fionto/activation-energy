from datetime import datetime

filename_raw = '20260408_123516_E14FS_P4E-2mbar_T020C.txt'

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

print(parse_filename(filename_raw))