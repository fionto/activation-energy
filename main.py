from pathlib import Path
from models import DatasetCollection, Dataset, Measurement, Elaborations
from constants import ColumnNames
import loaders
import processes

def main():
    raw_dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'

    if not raw_dataset_dir.exists():
        # Using SystemExit is a clean way to quit with an error message
        raise SystemExit(f"Error: Directory not found at {raw_dataset_dir}")

    if not raw_dataset_dir.is_dir():
        raise SystemExit(f"Error: {raw_dataset_dir} exists but is not a directory.")

    csv_datasets = []

    # filename starts with date, so it should be ordered chronologically
    # the folder might contain other files, in the future should filter better
    for file in sorted(raw_dataset_dir.glob("*.txt")):
        
        # The acquisition pipeline via LabVIEW store 
        # METADATA in the .txt filename
        csv_metadata = loaders.load_metadata_csv(file.name)

        # The extraction of the .txt file content is presented in a dataclass object
        # to perform pandas elaborations it is necessary to extract the DataFrame (df)
        csv_measurement = loaders.load_measurement_csv(file)
        df = Measurement.to_dataframe(csv_measurement)        

        # Processing data (global linear fit for now)
        csv_linear_fit = processes.linear_fit(df[ColumnNames.VOLTAGE], df[ColumnNames.CURRENT])
        csv_elaborations = Elaborations(linear_fit=csv_linear_fit)

        # Container for a single .txt file
        csv_dataset = Dataset(metadata=csv_metadata, measurement=csv_measurement, elaborations=csv_elaborations)

        csv_datasets.append(csv_dataset)

    # Container for all .txt files in the directory    
    datasets = DatasetCollection(datasets=csv_datasets)
    print(datasets.summary_df)

if __name__ == "__main__":
    main()