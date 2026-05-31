from pathlib import Path
from typing import Dict, Union, Any
import constants

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
        

def normalize_pressure_to_torr(value_str: str, unit_str: str | None) -> float:
    """Convert a pressure value string to Torr based on its unit suffix.
    
    Supported units (case-insensitive): bar, mbar, torr, mtorr, Pa, atm.
    If unit_str is empty, unrecognized, or conversion fails, defaults to Torr.
    
    Args:
        value_str: The raw string representation of the numeric pressure value.
        unit_str: The raw string representation of the unit suffix (e.g., 'mbar').
        
    Returns:
        The pressure value normalized to Torr as a float.
    """

    try:
        # Convert numeric string safely
        value = float(value_str)
        
        # Normalize unit string to uppercase; default to 'TORR' if empty or None
        unit = (unit_str or "TORR").strip().upper()
        
        # Fetch conversion factor, fallback to 1.0 (Torr) if unit is unknown
        factor = constants.CONVERSION_FACTORS.get(unit, 1.0)
        
        return value * factor

    except (ValueError, TypeError):
        # Fallback to safely trying to parse the value as pure Torr if something went wrong
        try:
            return float(value_str)
        except (ValueError, TypeError):
            raise ValueError(f"Could not parse numeric pressure value: {value_str}")
        

def _render_pipeline_report(
    title: str, 
    accepted_count: int, 
    rejected_files: Dict[Union[Path, str], str], 
    success_message: str,
    column_two_header: str
) -> None:
    """Internal helper to render a standardized pipeline execution report."""
    rejected_count = len(rejected_files)
    total_count = accepted_count + rejected_count

    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)
    print(f"Total Files Attempted: {total_count}")
    print(f"Passed Step:           {accepted_count}")
    print(f"Failed Step:           {rejected_count}")
    print("-" * 60)

    if not rejected_files:
        print(f"✅ {success_message}")
        print("=" * 60 + "\n")
        return

    print(f"{'FILE NAME':<35} | {column_two_header}")
    print("-" * 60)

    for file_path, reason in sorted(rejected_files.items(), key=lambda x: Path(x[0]).name):
        path_obj = Path(file_path)
        print(f"{path_obj.name:<35} | {reason}")
        print(f"  └─ Source: {path_obj}\n")

    print("=" * 60 + "\n")


# --- Functions Exposed to Main ---

def print_discarded_files_report(validation_results: dict) -> None:
    """Prints a formatted summary report of the dataset validation phase."""
    _render_pipeline_report(
        title="DATASET VALIDATION DISCARD REPORT",
        accepted_count=len(validation_results.get("accepted", [])), # Handles List
        rejected_files=validation_results.get("rejected", {}),
        success_message="Clean run! No files were discarded.",
        column_two_header="REASON FOR DISCARD"
    )


def print_loading_failures_report(loading_results: dict) -> None:
    """Prints a formatted summary report of the dataset ingestion phase."""
    _render_pipeline_report(
        title="DATASET LOADING & PROCESSING REPORT",
        accepted_count=len(loading_results.get("accepted", {})), # Handles Dict
        rejected_files=loading_results.get("rejected", {}),
        success_message="Clean run! All files loaded successfully.",
        column_two_header="FAILURE REASON / ERROR"
    )