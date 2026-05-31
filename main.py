"""Main execution entry point for the I(V) measurement processing pipeline.

This script coordinates the data validation, parsing, regional analysis, 
and plotting of thin-film electrical properties from raw laboratory text files.
"""

from pathlib import Path
import sys
import matplotlib.pyplot as plt

import constants
import loaders
import models
import utils
import validators


def main():
    """Execute the data processing and physical evaluation pipeline."""
    
    # =========================================================================
    # PHASE 1: ENVIRONMENT & CONFIGURATION INITIALIZATION
    # =========================================================================
    # Target directory holding LabVIEW-generated individual I(V) curves
    raw_datasets_dir = Path(__file__).parent / 'data' / 'UH70-FS'

    # =========================================================================
    # PHASE 2: DATA VALIDATION (File names, extensions, size, integrity)
    # =========================================================================
    try:
        directory_content = validators.validate_all_datasets(
            raw_datasets_dir, constants.FILENAME_PATTERN, verbose=False
        )
    except TypeError as e:
        print(f"❌ Fatal error: Invalid regex object\n   {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Fatal error: No datasets found\n   {e}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"❌ Fatal error: Invalid directory path\n   {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Fatal error: Permission denied reading dir\n   {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"❌ Fatal error: Filesystem error\n   {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Fatal error: Directory check failed\n   {e}", file=sys.stderr)
        sys.exit(1)

    # Output file-level structural issues before attempt processing
    utils.print_discarded_files_report(directory_content)
    
    # =========================================================================
    # PHASE 3: DATA INGESTION & MATHEMATICAL PROCESSING
    # =========================================================================
    try:
        # Load internal CSV structures and run localized linear fits
        loaded_content = loaders.load_all_datasets(
            directory_content['accepted'], 
            delimiter=','
        )
    except ValueError as e:
        print(f"❌ Fatal error: Processing run failed\n   {e}", file=sys.stderr)
        sys.exit(1)

    # Output processing/mathematical extraction failures (e.g., div by zero)
    utils.print_loading_failures_report(loaded_content)

    # =========================================================================
    # PHASE 4: MODEL RESOLUTION & DATA AGGREGATION
    # =========================================================================
    valid_datasets = list(loaded_content['accepted'].values())
    collection = models.DatasetCollection(datasets=valid_datasets)
   
    # =========================================================================
    # PHASE 5: EVALUATION, SUMMARIZATION & VISUALIZATION
    # =========================================================================
    # Print high-level operational statistics
    print(collection.summary_df)
    
    # Calculate electrical sheets characteristics
    vdp_results = collection.vdp_df
    print(vdp_results)
    
    # Render regional sheets parameters dynamically against temperature profiles
    vdp_results.plot(x="temp_k", y="sheet_resistance_ohm")
    plt.show()


if __name__ == "__main__":
    main()