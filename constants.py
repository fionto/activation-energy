import re
from typing import List, Set

CELSIUS_TO_KELVIN = 273.15


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


FILENAME_PATTERN = re.compile(
    r"^"
    # 1. timestamp YYYYMMDD_HHMMSS
    r"(?P<ts>\d{8}_\d{6})"
    # 2. nome campione
    r"_(?P<sample>[A-Za-z0-9]+)"
    # 3. pressione: numero puro nel gruppo 'pressure', unità (opzionale) nel gruppo 'press_unit'
    r"_P(?P<pressure>[0-9]*\.?[0-9]+(?:[Ee][+-]?\d+)?)(?P<press_unit>[A-Za-z]+)?"
    # 4. temperatura: numero puro nel gruppo 'temperature', unità (opzionale) nel gruppo 'temp_unit'
    r"_T(?P<temperature>\d+)(?P<temp_unit>[Cc]|[Kk])?"
    # 5. allineamento opzionale
    r"(?:_(?P<alignment>AB|BA))?"
    # 6. estensione
    r"\.txt$",
    re.IGNORECASE,
)