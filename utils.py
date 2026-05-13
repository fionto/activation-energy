from pathlib import Path

def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.
    Returns float('nan') if conversion fails, to allow error propagation.
    """
    try:
        return float(value_str.strip())
    except ValueError:
        return float("nan")
    

def check_alignment(alignment_str: str | None) -> str | None:
    """
    Validates and normalizes Van der Pauw alignment configuration.

    Args:
        alignment_str: Raw alignment string from filename ('AB', 'BA', or None)

    Returns:
        Normalized alignment string ('horizontal', 'vertical', or None)

    Raises:
        ValueError: if alignment_str is not 'AB', 'BA', or None
    """
    if alignment_str is None:
        return None
    match alignment_str:
        case 'AB':
            return "horizontal"
        case 'BA':
            return "vertical"
        case _:
            raise ValueError(f"Invalid VdP configuration: {alignment_str}")


def validate_dataset_directory(
    directory_path: Path,
    required_extension: str = "*.txt",
    min_files: int = 1,
    verbose: bool = True
) -> Path:
    """Validate dataset directory for existence, accessibility, and content.
    
    This function performs comprehensive validation of the dataset directory,
    checking not only that it exists and is a directory, but also that it
    contains readable files and has sufficient content for processing.
    
    Args:
        directory_path: Path object pointing to the dataset directory.
        required_extension: File pattern to look for (default: "*.txt").
                          Change to "*.csv" if needed in future.
        min_files: Minimum number of matching files required (default: 1).
        verbose: Whether to print validation messages (default: True).
    
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
    
    # EXISTENCE CHECK
    if not directory_path.exists():
        error_msg = (
            f"Error: Directory not found at {directory_path}\n"
            f"Expected path: {directory_path.resolve()}\n"
            f"Please ensure the 'data/UH70-FS' directory exists."
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
    if not directory_path.is_absolute():
        directory_path = directory_path.resolve()
    
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
    
    # CONTENT CHECK (does it contain the expected files?)
    matching_files = list(directory_path.glob(required_extension))
    
    if not matching_files:
        error_msg = (
            f"Error: No files matching '{required_extension}' found in:\n"
            f"{directory_path}\n"
            f"Directory contents: {[f.name for f in directory_path.iterdir()]}\n"
            f"Check that measurement files are named correctly."
        )
        raise SystemExit(error_msg)
    
    if len(matching_files) < min_files:
        error_msg = (
            f"Error: Insufficient data files in {directory_path}\n"
            f"Found: {len(matching_files)} files (minimum required: {min_files})\n"
            f"Files found: {[f.name for f in matching_files]}"
        )
        raise SystemExit(error_msg)
    
    # FILE-LEVEL VALIDATION (are the files readable?)
    unreadable_files = []
    for file in matching_files:
        try:
            # Check if file is readable by attempting to open it
            with open(file, 'r', encoding='utf-8') as f:
                # Try reading first line to ensure file isn't corrupted
                f.readline()
        except PermissionError:
            unreadable_files.append((file.name, "Permission denied"))
        except UnicodeDecodeError:
            unreadable_files.append((file.name, "Invalid encoding (not UTF-8)"))
        except OSError as e:
            unreadable_files.append((file.name, str(e)))
    
    if unreadable_files:
        files_info = "\n".join(
            f"  - {name}: {reason}" for name, reason in unreadable_files
        )
        error_msg = (
            f"Error: Some files in {directory_path} are not readable:\n"
            f"{files_info}\n"
            f"Check file permissions and encoding."
        )
        raise SystemExit(error_msg)
    
    # SUCCESS: All validations passed
    if verbose:
        print(
            f"✓ Dataset directory validated successfully\n"
            f"  Location: {directory_path.resolve()}\n"
            f"  Files found: {len(matching_files)} measurements ready for processing"
        )
    
    return directory_path.resolve()