import pandas as pd
from datetime import datetime
from pathlib import Path
from models import Measurement, Metadata, Dataset
from constants import ColumnNames, CELSIUS_TO_KELVIN
import utils


def load_measurement_csv(filepath: Path) -> Measurement:
    """Load raw CSV and convert to Measurement object."""
    
    raw_df = pd.read_csv(filepath)

    column_mapping = {
        'Voltage (V)': ColumnNames.VOLTAGE,
        'Current (A)': ColumnNames.CURRENT,
        'Standard Deviation (A)': ColumnNames.STD_DEV,
        'Measurement delay (s)': ColumnNames.DELAY,
    }

    cleaned_df = raw_df.copy()
    cleaned_df.columns = cleaned_df.columns.str.strip()
    cleaned_df = cleaned_df.rename(columns=column_mapping)

    return Measurement.from_dataframe(cleaned_df)    


def load_metadata_csv(filename: str) -> Metadata:
    """
    Parses a measurement filename with the structure:

        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt

    where the Van der Pauw configuration suffix (AB or BA) is optional.

    Extracts metadata from the filename and returns a Metadata object containing:
        - sample name
        - timestamp (as a datetime object)
        - pressure (in Torr)
        - temperature (in Kelvin)
        - alignment (str: 'horizontal', 'vertical', or None if not present)

    Args:
        filename: The measurement filename to parse

    Returns:
        Metadata: A dataclass instance containing the parsed fields.

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
