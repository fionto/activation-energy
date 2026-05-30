import pandas as pd
from datetime import datetime
from pathlib import Path
import models
import constants
import utils
import processes


def load_measurement_csv(filepath: Path, delimiter : str =',') -> models.Measurement:
    """Load measurement data from a .txt file (formatted in CSV) and convert to 
    Measurement object. With flexible delimiter support.
    
    Reads a raw .txt file, standardizes column names, and validates that all
    required measurement columns are present before creating a Measurement object.
    
    Args:
        filepath: Path to the .txt file containing measurement data.
        delimiter: what delimiter is used in the .txt files. Default = comma
    
    Returns:
        A Measurement object containing the validated measurement data.
    
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing from the .txt file.
        pd.errors.ParserError: If the .txt file is malformed or cannot be parsed.
    
    """
    
    # Read the raw .txt file (formatted in CSV)
    raw_df = pd.read_csv(filepath, sep=delimiter)
    
    # Define mapping from file column names to standardized internal names
    column_mapping = {
        'Voltage (V)': constants.ColumnNames.VOLTAGE,
        'Current (A)': constants.ColumnNames.CURRENT,
        'Standard Deviation (A)': constants.ColumnNames.STD_DEV,
        'Measurement delay (s)': constants.ColumnNames.DELAY,
    }
 
    # Remove leading/trailing whitespace from all column names
    # (.str is a pandas accessor that applies string methods to each column name)
    raw_df.columns = raw_df.columns.str.strip()
    
    # Rename columns from their original names (as they appear in the file)
    # to our standardized internal column names using the mapping dictionary
    raw_df = raw_df.rename(columns=column_mapping)
    
    # Validate and return as Measurement object
    return models.Measurement.from_dataframe(raw_df)


def load_metadata_csv(filename: str) -> models.Metadata:
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
    temperature_k = utils._safe_float(temp_str.removeprefix('T').removesuffix('C')) + constants.CELSIUS_TO_KELVIN
    alignment = utils.check_alignment(alignment_raw)

    return models.Metadata(
        sample=sample_str,
        timestamp=timestamp,
        pressure_torr=pressure_torr,
        temperature_k=temperature_k,
        alignment=alignment,
    )

def load_and_process_dataset(measurement_file: Path) -> models.Dataset:
    """Load a single measurement file and compute all elaborations.
    
    Loads raw I(V) measurement data from a .txt file, extracts metadata from the
    filename, and computes linear fit elaborations on the full, positive, and
    negative voltage regions.
    
    The processing pipeline includes:
        1. Extracting sample metadata from the filename
        2. Loading the CSV-formatted I(V) measurement data
        3. Converting to DataFrame and separating positive/negative voltage regions
        4. Computing linear fits (slope = resistance) for each region
        5. Packaging everything into a Dataset container
    
    Args:
        measurement_file: Path to the .txt file containing the I(V) measurement.
            The filename must follow the standard format:
            YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt
            The file should contain CSV data with columns for voltage and current.
    
    Returns:
        A Dataset object containing:
            - metadata: Sample information, timestamp, pressure, temperature, alignment
            - measurement: Raw I(V) data points
            - elaborations: Linear fit results for global, positive, and negative regions
    
    Raises:
        FileNotFoundError: If measurement_file does not exist.
        ValueError: If filename format is invalid, CSV data is malformed, 
            or required columns (VOLTAGE, CURRENT) are missing.
        pd.errors.ParserError: If the .txt file cannot be parsed as CSV.
    """

    # The acquisition pipeline via LabVIEW 
    # stores METADATA in the .txt filename
    metadata = load_metadata_csv(measurement_file.name)
    measurement = load_measurement_csv(measurement_file)
    voltage_current_df = models.Measurement.to_dataframe(measurement) # for elaborations i need a df

    # Split data for linear fit
    positive_VI_df = voltage_current_df[voltage_current_df[constants.ColumnNames.VOLTAGE] > 0]
    negative_VI_df = voltage_current_df[voltage_current_df[constants.ColumnNames.VOLTAGE] < 0]

    # Compute fits
    elaborations = models.Elaborations(
        global_linear_fit=processes.linear_fit(
            voltage_current_df[constants.ColumnNames.VOLTAGE], 
            voltage_current_df[constants.ColumnNames.CURRENT]
        ),
        positive_linear_fit=processes.linear_fit(
            positive_VI_df[constants.ColumnNames.VOLTAGE], 
            positive_VI_df[constants.ColumnNames.CURRENT]
        ),
        negative_linear_fit=processes.linear_fit(
            negative_VI_df[constants.ColumnNames.VOLTAGE], 
            negative_VI_df[constants.ColumnNames.CURRENT]
        )
    )

    return models.Dataset(metadata=metadata, measurement=measurement, elaborations=elaborations)


def load_all_datasets(filtered_files: list) -> models.DatasetCollection:
    """Load and process all measurement files in a directory.
        
    Args:
        
    Returns:
    
    Raises:
    
    Note:

    """
    
    datasets_list = []

    for measurement_file in filtered_files:
        datasets_list.append(load_and_process_dataset(measurement_file))

    return models.DatasetCollection(datasets=datasets_list)