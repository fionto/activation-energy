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
        ValueError: If the file cannot be parsed by pandas or is empty.
        KeyError: If required measurement columns are missing from the file.
    """
    
    # 1. Catch pandas parsing failures (e.g., parsing errors, completely empty files)
    try:
        raw_df = pd.read_csv(filepath, sep=delimiter)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file at {filepath}. Check delimiter or file integrity. Internal error: {e}")

    # Explicitly catch completely empty files before doing column logic 
    if raw_df.empty:
        raise ValueError(f"The file at {filepath} is empty.")
    
    # Remove leading/trailing whitespace from all column names
    # (.str is a pandas accessor that applies string methods to each column name)
    raw_df.columns = raw_df.columns.str.strip()
    
    # Validate that all required columns actually exist before renaming
    missing_columns = [col for col in constants.COLUMN_MAPPING if col not in raw_df.columns]
    if missing_columns:
        raise KeyError(
            f"The file is missing required columns: {missing_columns}. "
            f"Found columns: {list(raw_df.columns)}. Ensure the correct delimiter '{delimiter}' was used."
        )
    
    # Rename columns safely now that we know they exist
    raw_df = raw_df.rename(columns=constants.COLUMN_MAPPING)
    
    # Validate and return as Measurement object
    return models.Measurement.from_dataframe(raw_df)


def load_metadata_csv(filename: str) -> models.Metadata:
    """Parse measurement filename and extract metadata using regex.
    
    Extracts metadata from a filename stem (without extension) matching the format:
        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)]
    
    The function handles units dynamically:
        - Pressure defaults to Torr (stripping any alphabetical unit).
        - Temperature conversions dynamically check for 'C' or 'K' suffixes.
    
    Args:
        filename: The measurement filename to parse. If a full name or path is
            passed, it will automatically extract the stem.
    
    Returns:
        A Models.Metadata object containing parsed and normalized fields.
    
    Raises:
        ValueError: If the filename does not match the expected pattern, if 
            numeric values are unparseable, or if pressure/temperature unit 
            conversions fail.
    """
    match = constants.FILENAME_PATTERN.match(filename)
    if not match:
        raise ValueError(
            f"Filename format is invalid. Does not match expected pattern: {filename}"
        )
    # Extract all named groups into a dictionary
    data = match.groupdict()

    try:
        # 1. Parse Timestamp
        timestamp = datetime.strptime(data["ts"], "%Y%m%d_%H%M%S")
        
        # 2. Parse Pressure and normalize to Torr dynamically)
        pressure_torr = utils.normalize_pressure_to_torr(
            data["pressure"], 
            data["press_unit"]
        )
        
        # 3. Parse Temperature & Handle Units dynamically
        temp_val = utils._safe_float(data["temperature"])
        temp_unit = (data["temp_unit"] or "C").upper()  # Default to Celsius if not specified
        
        if temp_unit == "C":
            temperature_k = temp_val + constants.CELSIUS_TO_KELVIN
        else:
            temperature_k = temp_val  # Already in Kelvin
            
        # 4. Parse Alignment
        alignment = utils.check_alignment(data["alignment"])

    except (ValueError, TypeError, AttributeError) as err:
        raise ValueError(
            f"Failed to parse numeric or date fields from filename '{filename}': {err}"
        ) from err

    return models.Metadata(
        sample=data["sample"],
        timestamp=timestamp,
        pressure_torr=pressure_torr,
        temperature_k=temperature_k,
        alignment=alignment,
    )


def load_and_process_dataset(measurement_file: Path, delimiter: str = ',') -> models.Dataset:
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
        delimiter: What delimiter is used in the CSV data. Default = comma.
    
    Returns:
        A Dataset object containing:
            - metadata: Sample information, timestamp, pressure, temperature, alignment
            - measurement: Raw I(V) data points
            - elaborations: Linear fit results for global, positive, and negative regions
    
    Raises:
        ValueError: If the filename metadata parsing fails, the CSV is empty, 
                    or the CSV cannot be parsed by pandas.
        KeyError: If required measurement columns are missing from the file.
        ZeroDivisionError: Or other calculation errors if linear fitting fails 
                           due to empty or insufficient data points.
    """

    # The acquisition pipeline via LabVIEW 
    # stores METADATA in the filename
    metadata = load_metadata_csv(measurement_file.stem) # files are already prefiltered
    
    # Load and Validate Measurement Data
    measurement = load_measurement_csv(measurement_file, delimiter=delimiter)
      
    # Extract DataFrame for elaborations
    voltage_current_df = models.Measurement.to_dataframe(measurement)

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
    """Load and parse dataset files into a collection object.
    
    Args:
        file_paths: List of validated Path objects to dataset files.
    
    Returns:
        A collection object containing parsed data.
    
    Raises:
        ValueError: 
            -If the file cannot be parsed by pandas or is empty.
            -If the filename does not match the expected pattern, 
            -If numeric values are unparseable
            -If pressure/temperature unit conversions fail.
        KeyError: 
            -If required measurement columns are missing from the file.
        ZeroDivisionError: 
            -Calculation errors if linear fitting fails due to empty 
                or insufficient data points.
    """
    
    datasets_list = []

    for measurement_file in filtered_files:  
        datasets_list.append(load_and_process_dataset(measurement_file))

    return models.DatasetCollection(datasets=datasets_list)