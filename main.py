from pathlib import Path
from models import DatasetCollection, Dataset, Measurement, Elaborations
from constants import ColumnNames
import loaders
import processes
import utils

def main():
    # CSV DATA MANIPULATION
    # everything is carried on a single .txt file (CSV data) containing one single V(I) measurement
    # the directory contains multiple measurements (.txt files)
    raw_dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'
    validated_dir = utils.validate_dataset_directory(raw_dataset_dir)

    datasets_list = []

    # filename starts with date, so it should be ordered chronologically
    # the folder might contain other files, in the future should filter better
    for measurement_file in sorted(validated_dir.glob("*.txt")):
        
        # The acquisition pipeline via LabVIEW store 
        # METADATA in the .txt filename
        metadata = loaders.load_metadata_csv(measurement_file.name)

        # The extraction of the .txt file content is presented in a dataclass object
        # to perform pandas elaborations it is necessary to extract the DataFrame (df)
        measurement = loaders.load_measurement_csv(measurement_file)
        voltage_current_df = Measurement.to_dataframe(measurement)        

        # Processing data (global linear fit for now)
        linear_fit_result = processes.linear_fit(
            voltage_current_df[ColumnNames.VOLTAGE], 
            voltage_current_df[ColumnNames.CURRENT]
        )
        elaborations = Elaborations(linear_fit=linear_fit_result)

        # Container for a single .txt file
        dataset = Dataset(
            metadata=metadata, 
            measurement=measurement, elaborations=elaborations
        )

        datasets_list.append(dataset)

    # Container for all .txt files in the directory    
    collection = DatasetCollection(datasets=datasets_list)
    print(collection.summary_df)

if __name__ == "__main__":
    main()