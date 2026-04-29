# Project Architecture: I(V) Measurement Pipeline

This document describes the software design and data structures used to process electrical measurement data within this repository.

## Overview
The pipeline is designed to transform raw `.txt` files containing I(V) data into a structured hierarchy of Python objects, enabling both individual dataset inspection and global population analysis.

## Core Components
The system is divided into functional modules to ensure a separation of concerns:

* **Entry Point (`main.py`)**: Orchestrates the batch processing of files within a target directory.
* **Data Models (`models.py`)**: Defines the hierarchical `dataclass` structures used to store metadata, raw data, and processed results.
* **Data Ingestion (`loaders.py`)**: Contains logic for parsing filenames into environmental metadata and reading CSV-formatted raw data into DataFrames.
* **Analysis Engine (`processes.py`)**: Performs statistical analysis and physical modeling, such as linear regression fits.
* **Constants & Configuration (`constants.py`)**: Centralizes shared physical constants and DataFrame schema definitions to prevent "magic strings".
* **Utilities (`utils.py`)**: Provides low-level data cleaning and validation functions.

## Data Model Hierarchy
The architecture centers on the `Dataset` object, which serves as a single source of truth for an experimental measurement.

* **`Metadata`**: Holds environmental context (e.g., `temperature_k`, `pressure_torr`) and spatial configuration (`alignment`).
* **`Measurement`**: A wrapper for the raw `pandas.DataFrame`. It performs self-validation to ensure required electrical columns are present.
* **`Elaborations`**: A container for derived quantities. Currently, it stores `LinearFit` objects containing slope, resistance, and R² values.
* **`Dataset`**: Orchestrates the relationship between the `Metadata`, `Measurement`, and `Elaborations` for a single run.
* **`DatasetCollection`**: Aggregates multiple `Dataset` objects, providing a `summary_df` for cross-sample analysis.

## Pipeline Workflow
The data moves through the system in a structured four-stage process:

1. **Extraction**: Files are identified and metadata is extracted from the naming convention (e.g., `YYYYMMDD_HHMMSS...`).
2. **Ingestion**: The file body is read into a `Measurement` object, where it is validated against the schema defined in `constants.py`.
3. **Processing**: The data is passed to `processes.py`, where fits are performed and stored within the `Elaborations` model.
4. **Reporting**: Results are either printed as individual reports or flattened into a global DataFrame for plotting.