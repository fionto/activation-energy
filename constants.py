import re
from typing import List, Set

# FILE INFO
ACCEPTED_EXTENSIONS = {".txt", ".csv"}

# Temperature conversion
CELSIUS_TO_KELVIN = 273.15

# Define conversion factors to Torr (1 Unit = X Torr)
CONVERSION_FACTORS = {
    "TORR": 1.0,
    "MTORR": 1e-3,
    "BAR": 750.061683,
    "MBAR": 0.750061683,
    "PA": 0.00750061683,
    "ATM": 760.0,
}

class ColumnNames:
    """Centralized definition of all DataFrame column names."""

    VOLTAGE = "voltage_v"
    CURRENT = "current_a"
    STD_DEV = "std_dev"
    DELAY = "delay_s"

    @classmethod
    def required(cls) -> Set[str]:
        """Get required column names for validation."""
        return {cls.VOLTAGE, cls.CURRENT, cls.STD_DEV, cls.DELAY}

    @classmethod
    def all(cls) -> List[str]:
        """Get all column names as a list."""
        return [cls.VOLTAGE, cls.CURRENT, cls.STD_DEV, cls.DELAY]


class MetadataFieldNames:
    """Field names for the Metadata dataclass."""

    SAMPLE = "sample"
    TIMESTAMP = "timestamp"
    PRESSURE_TORR = "pressure_torr"
    TEMPERATURE_K = "temperature_k"
    ALIGNMENT = "alignment"

    @classmethod
    def all(cls) -> Set[str]:
        """Return all metadata field names as a set."""
        return {
            cls.SAMPLE,
            cls.TIMESTAMP,
            cls.PRESSURE_TORR,
            cls.TEMPERATURE_K,
            cls.ALIGNMENT,
        }


class LinearFitNames:
    """Field names for the linear fit parameters."""

    SLOPE = "slope"
    INTERCEPT = "intercept"
    R_SQUARED = "r_squared"

    @classmethod
    def all(cls) -> Set[str]:
        """Return all linear fit field names as a set."""
        return {
            cls.SLOPE,
            cls.INTERCEPT,
            cls.R_SQUARED,
        }

# Define mapping from file column names to standardized internal names
# strict name they appear in the file (maybe in the future will change)
COLUMN_MAPPING = {
    'Voltage (V)': ColumnNames.VOLTAGE,
    'Current (A)': ColumnNames.CURRENT,
    'Standard Deviation (A)': ColumnNames.STD_DEV,
    'Measurement delay (s)': ColumnNames.DELAY,
}

# NOTE: This pattern is designed to match against the file's STEM (filename without extension).
# Extension validation (e.g., .txt) must be handled separately beforehand, allowing this
# pattern to remain decoupled from specific file formats.
FILENAME_PATTERN = re.compile(
    r"^"
    # 1. timestamp YYYYMMDD_HHMMSS
    r"(?P<ts>\d{8}_\d{6})"
    # 2. sample name (allows letters, numbers, hyphens, and dots)
    r"_(?P<sample>[A-Za-z0-9.-]+)"
    # 3. pressure: float/scientific, optional unit
    r"_P(?P<pressure>[0-9]*\.?[0-9]+(?:[Ee][+-]?\d+)?)(?P<press_unit>[A-Za-z]+)?"
    # 4. temperature: integer or decimal, optional unit (C or K)
    r"_T(?P<temperature>\d+(?:\.\d+)?)(?P<temp_unit>[Cc]|[Kk])?"
    # 5. optional alignment suffix (at the very end of the stem)
    r"(?:_(?P<alignment>AB|BA))?$",
    re.IGNORECASE,
)