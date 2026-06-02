from pathlib import Path
from typing import Dict, Union

def _generate_pipeline_report(
    title: str, 
    accepted_count: int, 
    rejected_files: Dict[Union[Path, str], str], 
    success_message: str,
    column_two_header: str
) -> str:
    """Internal helper to write a standardized pipeline execution report."""
    rejected_count = len(rejected_files)
    total_count = accepted_count + rejected_count

    # Build the header block cleanly
    lines = [
        "=" * 60,
        f"{title:^60}",
        "=" * 60,
        f"Total Files Attempted: {total_count}",
        f"Passed Step:           {accepted_count}",
        f"Failed Step:           {rejected_count}",
        "-" * 60
    ]

    if not rejected_files:
        lines.extend([
            f"✅ {success_message}",
            "=" * 60
        ])
        return "\n".join(lines) + "\n"

    lines.extend([
        f"{'FILE NAME':<35} | {column_two_header}",
        "-" * 60
    ])
    
    # Safe sorting handling potential string/Path mix
    sorted_rejections = sorted(
        rejected_files.items(), 
        key=lambda x: Path(x[0]).name if x[0] else ""
    )

    for file_path, reason in sorted_rejections:
        path_obj = Path(file_path)
        lines.extend([
            f"{path_obj.name:<35} | {reason}",
            f"  └─ Source: {path_obj}",
            "-" * 60
        ])

    return "\n".join(lines) + "\n"


def write_discarded_files_report(validation_results: dict) -> str:
    """Generates a formatted summary report of the dataset validation phase."""
    return _generate_pipeline_report(
        title="DATASET VALIDATION DISCARD REPORT",
        accepted_count=len(validation_results.get("accepted", [])), 
        rejected_files=validation_results.get("rejected", {}),
        success_message="Clean run! No files were discarded.",
        column_two_header="REASON FOR DISCARD"
    )


def write_loading_failures_report(loading_results: dict) -> str:
    """Generates a formatted summary report of the dataset ingestion phase."""
    return _generate_pipeline_report(
        title="DATASET LOADING & PROCESSING REPORT",
        accepted_count=len(loading_results.get("accepted", {})), 
        rejected_files=loading_results.get("rejected", {}),
        success_message="Clean run! All files loaded successfully.",
        column_two_header="FAILURE REASON / ERROR"
    )