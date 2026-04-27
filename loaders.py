import pandas as pd
from datetime import datetime
from pathlib import Path
from models import Measurement, Metadata
from constants import ColumnNames, CELSIUS_TO_KELVIN
import utils


def load_measurement_csv(filepath: Path) -> Measurement:
    """Load measurement data from a CSV file and convert to Measurement object.
    
    Reads a raw CSV file, standardizes column names, and validates that all
    required measurement columns are present before creating a Measurement object.
    
    Args:
        filepath: Path to the CSV file containing measurement data.
    
    Returns:
        A Measurement object containing the validated measurement data.
    
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing from the CSV file.
        pd.errors.ParserError: If the CSV file is malformed or cannot be parsed.
    
    """
    
    # Read the raw CSV file
    raw_df = pd.read_csv(filepath)
    
    # Define mapping from file column names to standardized internal names
    column_mapping = {
        'Voltage (V)': ColumnNames.VOLTAGE,
        'Current (A)': ColumnNames.CURRENT,
        'Standard Deviation (A)': ColumnNames.STD_DEV,
        'Measurement delay (s)': ColumnNames.DELAY,
    }
    
    # Create a copy of the raw DataFrame to avoid modifying the original
    cleaned_df = raw_df.copy()
    
    # Remove leading/trailing whitespace from all column names
    # (.str is a pandas accessor that applies string methods to each column name)
    cleaned_df.columns = cleaned_df.columns.str.strip()
    
    # Rename columns from their original names (as they appear in the file)
    # to our standardized internal column names using the mapping dictionary
    cleaned_df = cleaned_df.rename(columns=column_mapping)
    
    # Validate and return as Measurement object
    return Measurement.from_dataframe(cleaned_df)


def load_metadata_csv(filename: str) -> Metadata:
    """Parse measurement filename and extract metadata.
    
    Extracts metadata from a filename with the standard format:
    
        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt
    
    The Van der Pauw alignment suffix (AB or BA) is optional. The pressure
    suffix 'torr' and temperature suffix 'C' are optional and will be stripped.
    
    Args:
        filename: The measurement filename to parse (with or without .txt extension).
    
    Returns:
        A Metadata object containing:
            - sample: Sample name extracted from filename
            - timestamp: Datetime object parsed from YYYYMMDD_HHMMSS
            - pressure_torr: Pressure value in Torr
            - temperature_k: Temperature value in Kelvin
            - alignment: Van der Pauw alignment ('AB', 'BA', or None)
    
    Raises:
        ValueError: If filename format is invalid (wrong number of fields or
            unparseable numeric values in pressure/temperature fields).
    
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
    pressure_torr = utils._safe_float(pressure_str.removeprefix('P').removesuffix('torr'))
    temperature_k = utils._safe_float(temp_str.removeprefix('T').removesuffix('C')) + CELSIUS_TO_KELVIN
    alignment = utils.check_alignment(alignment_raw)

    return Metadata(
        sample=sample_str,
        timestamp=timestamp,
        pressure_torr=pressure_torr,
        temperature_k=temperature_k,
        alignment=alignment
    )