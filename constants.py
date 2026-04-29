CELSIUS_TO_KELVIN = 273.15


class ColumnNames:
    """Centralized definition of all DataFrame column names."""
    VOLTAGE = 'voltage_v'
    CURRENT = 'current_a'
    STD_DEV = 'std_dev'
    DELAY = 'delay_s'
    
    # Convenience: get all as a set for validation
    @classmethod
    def required(cls):
        return {cls.VOLTAGE, cls.CURRENT, cls.STD_DEV, cls.DELAY}
    
    # Convenience: get all as a list
    @classmethod
    def all(cls):
        return [cls.VOLTAGE, cls.CURRENT, cls.STD_DEV, cls.DELAY]


class MetadataFieldNames:
    """Field names for the Metadata dataclass."""
    SAMPLE = 'sample'
    TIMESTAMP = 'timestamp'
    PRESSURE_TORR = 'pressure_torr'
    TEMPERATURE_K = 'temperature_k'
    ALIGNMENT = 'alignment'
    
    @classmethod
    def all(cls):
        """Return all metadata field names as a set."""
        return {
            cls.SAMPLE,
            cls.TIMESTAMP,
            cls.PRESSURE_TORR,
            cls.TEMPERATURE_K,
            cls.ALIGNMENT
        }
    

class LinearFitNames:
    """Field names for the Metadata dataclass."""
    SLOPE = 'slope'
    INTERCEPT = 'intercept'
    R_SQUARED = 'r_squared'

    
    @classmethod
    def all(cls):
        """Return all metadata field names as a set."""
        return {
            cls.SLOPE,
            cls.INTERCEPT,
            cls.R_SQUARED,
        }