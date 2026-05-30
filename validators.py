import re
import sys
import utils
from pathlib import Path


def validate_filename(filename: str, pattern: re.Pattern) -> bool:
    """Validates if a filename matches a specific naming convention.

    This function checks the provided filename against a pre-defined regular
    expression pattern to ensure it follows the required structural format,
    including specific date-time stamps, sample identifiers, and optional
    sequence suffixes.

    Args:
        filename: The string filename to validate.
        pattern: A compiled regular expression object (typically imported
            from constants.py) defining the naming convention.

    Returns:
        True if the filename perfectly matches the pattern, False otherwise.

    Raises:
        TypeError: If the provided pattern is not a compiled regular
            expression object.

    Examples:
        >>> import re
        >>> from constants import FILENAME_PATTERN
        >>> validate_filename("20260530_143000_SAMPLE_P101bar_T25C_AB.txt", FILENAME_PATTERN)
        True
        >>> validate_filename("invalid_name.txt", FILENAME_PATTERN)
        False
    """

    m = pattern.match(filename)

    return False if not m else True


def validate_dataset_directory(
    directory_path: Path,
    verbose: bool = False
) -> Path:
    """Validate dataset directory for existence, accessibility, and content.
    
    This function performs validation of the dataset directory, checking 
    that it exists and is a directory.
    
    Args:
        directory_path: Path object pointing to the dataset directory.
        naming_pattern: A compiled regular expression object
        verbose: Whether to print validation messages (default: False).
    
    Returns:
        The validated Path object (allows method chaining if needed).
    
    Raises:
        SystemExit: With descriptive error message if any validation fails.
                   Exit code 1 for all directory/file validation errors.
    
    Examples:
        >>> raw_dir = Path(__file__).parent / 'data' / 'UH70-FS'
        >>> validated_dir = validate_dataset_directory(raw_dir)
        >>> # Now safe to use validated_dir for file operations
    """
    
    # EXISTENCE CHECK OF DIRECTORY
    if not directory_path.exists():
        error_msg = (
            f"Error: Directory not found at {directory_path}\n"
            f"Expected path: {directory_path.resolve()}\n"
            f"Please ensure the directory exists."
        )
        raise SystemExit(error_msg)

    # TYPE CHECK (is it actually a directory?)
    if not directory_path.is_dir():
        error_msg = (
            f"Error: Path exists but is not a directory: {directory_path}\n"
            f"Type: {directory_path.stat().st_mode}\n"
            f"This path points to a file, not a directory."
        )
        raise SystemExit(error_msg)
    
    # PERMISSIONS CHECK (can we read it?)
    try:
        # Attempting to list directory contents tests read permission
        list(directory_path.iterdir())
    except PermissionError:
        error_msg = (
            f"Error: Permission denied reading directory: {directory_path}\n"
            f"Current user does not have read permissions.\n"
            f"Try running with appropriate privileges or check file ownership."
        )
        raise SystemExit(error_msg)
    except OSError as e:
        error_msg = (
            f"Error: OS-level error accessing directory: {directory_path}\n"
            f"Details: {e}\n"
            f"This may indicate a network path issue or filesystem problem."
        )
        raise SystemExit(error_msg)
    
    # SUCCESS: All validations passed
    if verbose:
        print(
            f"✓ Dataset directory validated successfully\n"
            f"  Location: {directory_path.resolve()}\n"
        )
    
    return directory_path.resolve()


def validate_all_datasets(data_dir: Path, pattern: re.Pattern, verbose: bool = True) -> dict:
    """
    Scans a directory and filters files.
    Crashes hard via SystemExit if no files survive the validation checks.
    Returns a standard dict: {"accepted": [...], "rejected": {...}}
    """
    results = {
        "accepted": [],
        "rejected": {}
    }

    validated_dir = validate_dataset_directory(data_dir, verbose=verbose)

    # Grab ALL files in the directory
    all_files = sorted(f for f in validated_dir.iterdir() if f.is_file())

    # CRASH HARD 1: The directory is completely empty of any files
    if not all_files:
        sys.exit(f"\n❌ FATAL ERROR: No files found in directory: '{validated_dir}'")
    
    for i, measurement_file in enumerate(all_files, 1):
        full_path = measurement_file.resolve()
        
        if verbose:
            print(f"Processing {i}/{len(all_files)}: {measurement_file.name}")
        
        # Check extension
        if measurement_file.suffix.lower() not in {".txt", ".csv"}:
            results["rejected"][full_path] = f"Unsupported file extension ({measurement_file.suffix})"
            continue

        # Check filename pattern
        if not validate_filename(measurement_file.name, pattern):
            results["rejected"][full_path] = "Invalid Filename"
            continue

        # Check file size
        if measurement_file.stat().st_size == 0:
            results["rejected"][full_path] = "Empty file"
            continue

        # Check content readability
        try:
            with open(measurement_file, 'r', encoding='utf-8') as f:
                header = f.readline()
                second_line = f.readline()
                if not second_line:
                    results["rejected"][full_path] = "Empty file after the header"
                    continue
        except PermissionError:
            results["rejected"][full_path] = "Permission Error"
            continue
        except UnicodeDecodeError:
            results["rejected"][full_path] = "UnicodeDecodeError"
            continue
        except OSError as e:
            results["rejected"][full_path] = f"OSError: {e}"
            continue
        
        # File is valid
        results["accepted"].append(full_path)

    # CRASH HARD 2: Files were found, but 100% of them were rejected
    if not results["accepted"]:
        utils.print_discarded_files_report(results)

        sys.exit(
            f"❌ FATAL ERROR: All {len(results['rejected'])} file(s) in "
            f"'{validated_dir}' were invalid. Execution halted."
        )
    
    return results