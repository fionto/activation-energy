from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
from constants import ColumnNames, MetadataFieldNames, LinearFitNames

# METADATA: Information about the environment (Sample ID, Timestamp, P, T)
# Contains geometric information on how the measurement was spatially performed
# (Van Der Pauw alignment)
@dataclass
class Metadata:
    sample: str
    timestamp: datetime
    pressure_torr: float
    temperature_k: float
    alignment: str | None

    def summary(self) -> str:
        """Return a human-readable one-line summary."""
        return (f"Sample {self.sample} | {self.temperature_k}K, {self.pressure_torr}Torr | "
                f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

# DATA: Contains the arrays of measured values
@dataclass
class Measurement:
    data: pd.DataFrame  # Must contain: voltage_v, current_a, std_dev columns, delay_s
    
    def __post_init__(self):
        required = ColumnNames.required()
        missing = required - set(self.data.columns) # Set subtraction: find what's NOT in the DataFrame
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    
    @property
    def voltage(self) -> pd.Series:
        return self.data[ColumnNames.VOLTAGE]
    
    @property
    def current(self) -> pd.Series:
        return self.data[ColumnNames.CURRENT]
    
    @property
    def std_dev(self) -> pd.Series:
        return self.data[ColumnNames.STD_DEV]
    
    @property
    def delay(self) -> pd.Series:
        return self.data[ColumnNames.DELAY]
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame):
        return cls(data=df[[ColumnNames.VOLTAGE, ColumnNames.CURRENT, ColumnNames.STD_DEV, ColumnNames.DELAY]].copy())
    
    def to_dataframe(self):
        return self.data.copy()
    
# ELABORATIONS: Contains the results of data processing
# e.g.: fits, derived quantities, etc...
@dataclass
class LinearFit:
    slope: float
    intercept: float
    r_squared: float

    @property
    def resistance(self) -> float:
        """Returns resistance in Ohms. Assumes fit was I(V)."""
        return 1 / self.slope if self.slope != 0 else float('inf')

    @property
    def conductance(self) -> float:
        """Returns conductance in Siemens."""
        return self.slope

@dataclass
class Elaborations:
    linear_fit: LinearFit
    # Room for: mobility, resistivity, carrier_concentration, etc.

@dataclass
class Dataset:
    metadata: Metadata
    measurement: Measurement
    elaborations: Elaborations

    def report(self) -> str:
        """
        Generates a concise, human-readable summary of the entire dataset, 
        focusing on environmental conditions and the quality of the linear fit.
        """
        # Metadata header
        header = self.metadata.summary()
        
        # Data stats
        num_points = len(self.measurement.data)
        v_min = self.measurement.voltage.min()
        v_max = self.measurement.voltage.max()
        
        # Fit results
        fit = self.elaborations.linear_fit
        
        return (
            f"--- DATASET REPORT ---\n"
            f"Configuration: {header}\n"
            f"Measurement:   {num_points} points collected over [{v_min:.2e}V to {v_max:.2e}V]\n"
            f"Linear Fit:    Slope: {fit.slope:.4e} | Intercept: {fit.intercept:.4e}\n"
            f"Resistance:   {fit.resistance:.2e} Ω (R²: {fit.r_squared:.4f})\n"
            f"----------------------"
        )
    
@dataclass
class DatasetCollection:
    # datasets has a default value (empty list)
    datasets: list[Dataset] = field(default_factory=list)

    @property
    def summary_df(self) -> pd.DataFrame:
        """Flattens the most important info into a single DataFrame for global analysis."""
    
        if not self.datasets:
            return pd.DataFrame()
        
        # Pandas DataFrame can be created by passing lists of dictionaries as input data. 
        # By default, dictionary keys will be taken as columns. 

        rows = []

        for d in self.datasets:
            recap = {
                MetadataFieldNames.SAMPLE : d.metadata.sample,
                MetadataFieldNames.TEMPERATURE_K : d.metadata.temperature_k,
                MetadataFieldNames.ALIGNMENT : d.metadata.alignment,
                LinearFitNames.SLOPE : d.elaborations.linear_fit.slope,
                LinearFitNames.R_SQUARED : d.elaborations.linear_fit.r_squared,
            }
            rows.append(recap)
        
        return pd.DataFrame(rows)
    
    def __iter__(self):
        return iter(self.datasets)

    def __len__(self):
        return len(self.datasets)