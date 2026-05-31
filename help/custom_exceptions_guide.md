# Eccezioni Personalizzate in Python: Guida Pratica per il Tuo Progetto

## Introduzione: Perché le Eccezioni Personalizzate Sono Importanti

Nel tuo progetto di processing dei dati di misurazione, stai attualmente usando `ValueError` in situazioni molto diverse:

- In `validators.py`: "All files were rejected" (problema di batch processing)
- In `loaders.py`: "Failed to parse CSV file" (problema di parsing)
- In `loaders.py`: "Filename format is invalid" (problema di naming)

Il problema è che chi chiama queste funzioni non può distinguere la causa reale dell'errore senza leggere il messaggio di testo. Con eccezioni personalizzate, **il tipo della eccezione comunica il problema**, rendendo il codice che le usa più chiaro e resiliente.

### Quando Usare Eccezioni Personalizzate

**Usa eccezioni personalizzate quando:**
- L'errore rappresenta una categoria semantica **specifica e ricorrente** nel tuo dominio
- Chi chiama la funzione trarrà beneficio dal capire il tipo di errore senza leggere il messaggio
- Vuoi aggregare errori correlati sotto una categoria comune
- L'errore richiede azioni diverse dal codice che lo gestisce

**Non le usare quando:**
- Stai semplicemente ridenominando una eccezione built-in per motivi stilistici (es. `class ValidationError(ValueError)` senza aggiungere alcuna logica è ridondante)
- L'errore è unico nel progetto e non si verificherà mai in contesti diversi

Nel tuo caso, le eccezioni personalizzate sono **altamente appropriate** perché hai flussi di elaborazione multi-fase dove diversi tipi di errori richiedono trattamenti diversi.

---

## Gerarchia e Naming

### Principio di Base: Ereditarietà Gerarchica

Le eccezioni personalizzate devono formare una gerarchia che rifletta la tua architettura logica. La pratica standard in Python è:

```python
# Eccezione base per il dominio (radice della gerarchia)
class DatasetProcessingError(Exception):
    """Eccezione base per tutti gli errori di processing dei dataset."""
    pass

# Categoria 1: Errori di validazione
class ValidationError(DatasetProcessingError):
    """Errore durante la validazione di file o directory."""
    pass

# Sottocategoria di ValidationError
class FilenameValidationError(ValidationError):
    """Il nome del file non corrisponde al pattern atteso."""
    pass

class FileContentValidationError(ValidationError):
    """Il contenuto del file non è valido (UTF-8, struttura, ecc)."""
    pass

# Categoria 2: Errori di caricamento
class LoadingError(DatasetProcessingError):
    """Errore durante il caricamento dei dati."""
    pass

class CSVParsingError(LoadingError):
    """Il file CSV non può essere parsato (delimitatore sbagliato, corruzione, ecc)."""
    pass

class MetadataExtractionError(LoadingError):
    """Errore nell'estrazione dei metadati dal filename."""
    pass
```

### Convenzioni di Naming

| Pattern | Uso | Esempio |
|---------|-----|---------|
| `Error` (suffix) | Eccezione concreta per errori specifici | `FilenameValidationError`, `CSVParsingError` |
| Base (no suffix) | Classe radice del dominio | `DatasetProcessingError` |
| Categorie intermedie | Raggruppano errori correlati per facilità di catch | `ValidationError` → raggruppa tutti gli errori di validazione |

**Regola pratica**: se scrivi `except ValidationError`, deve catturare *tutti* gli errori che hanno senso insieme. Nel tuo caso, errori di filename, UTF-8 e contenuto vuoto sono tutti "il file non è valido" → stessa categoria.

---

## Implementazione nel Tuo Progetto

### Step 1: Definisci il File `exceptions.py`

Crea un nuovo modulo `exceptions.py` nella radice del progetto:

```python
"""Custom exceptions for dataset validation and processing.

This module defines a hierarchical exception structure that maps to the
workflow stages of the data processing pipeline:
  - Validation stage: file/directory checks
  - Loading stage: CSV parsing and metadata extraction
  - Processing stage: calculations and elaborations
"""


# ============================================================================
# BASE EXCEPTION FOR THE ENTIRE DOMAIN
# ============================================================================

class DatasetProcessingError(Exception):
    """Base exception for all dataset processing errors.
    
    This is the root exception for the entire data pipeline. Callers can
    catch this to handle any error that occurs during validation, loading,
    or processing of measurement datasets.
    """
    pass


# ============================================================================
# VALIDATION EXCEPTIONS (Stage 1: File/Directory Integrity)
# ============================================================================

class ValidationError(DatasetProcessingError):
    """Raised when dataset validation fails (file/directory checks).
    
    This covers structural and accessibility issues:
    - Directory does not exist or is not readable
    - File extensions are unsupported
    - File is empty or corrupted
    - Filename does not match the required naming convention
    
    Attribute:
        context: Optional Path or filename for additional debugging info
    """
    
    def __init__(self, message: str, context=None):
        self.message = message
        self.context = context
        super().__init__(self.message)


class DirectoryValidationError(ValidationError):
    """Raised when the dataset directory is invalid or inaccessible."""
    pass


class FilenameValidationError(ValidationError):
    """Raised when a filename does not match the required naming pattern.
    
    Example:
        Filename "invalid_name.txt" fails to match the pattern
        YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt
    """
    pass


class FileContentValidationError(ValidationError):
    """Raised when file content validation fails.
    
    This covers:
    - File is empty
    - File contains only header, no data rows
    - File is not valid UTF-8 encoded
    - File extension is not supported
    
    Attribute:
        reason: Specific cause (e.g., "Empty file", "Not UTF-8")
    """
    
    def __init__(self, message: str, reason: str = None, context=None):
        self.message = message
        self.reason = reason
        super().__init__(self.message)


# ============================================================================
# LOADING EXCEPTIONS (Stage 2: File Parsing and Metadata Extraction)
# ============================================================================

class LoadingError(DatasetProcessingError):
    """Raised when dataset loading fails (CSV parsing, metadata extraction).
    
    This covers:
    - CSV parsing errors (invalid delimiter, corrupted file)
    - Metadata extraction errors (unparseable filename format)
    - Missing or malformed required columns
    """
    pass


class CSVParsingError(LoadingError):
    """Raised when CSV file cannot be parsed.
    
    Reasons include:
    - Incorrect delimiter specification
    - File corruption or encoding issues (caught by pandas)
    - File is completely empty after parsing
    
    Attribute:
        original_error: The underlying Exception from pandas (if available)
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class MissingColumnsError(LoadingError):
    """Raised when required CSV columns are missing from the file.
    
    Attribute:
        missing_columns: List of column names that are missing
        found_columns: List of columns actually present in the file
    """
    
    def __init__(self, message: str, missing_columns: list = None, 
                 found_columns: list = None):
        self.message = message
        self.missing_columns = missing_columns or []
        self.found_columns = found_columns or []
        super().__init__(self.message)


class MetadataExtractionError(LoadingError):
    """Raised when metadata cannot be extracted from a filename.
    
    Reasons include:
    - Filename does not match expected pattern
    - Numeric fields (pressure, temperature) are unparseable
    - Unit conversion fails
    
    Attribute:
        filename: The filename that could not be parsed
    """
    
    def __init__(self, message: str, filename: str = None):
        self.message = message
        self.filename = filename
        super().__init__(self.message)


# ============================================================================
# PROCESSING EXCEPTIONS (Stage 3: Data Analysis and Elaborations)
# ============================================================================

class ProcessingError(DatasetProcessingError):
    """Raised when dataset processing or elaboration fails.
    
    This covers:
    - Linear fitting calculations (e.g., insufficient data points)
    - Division by zero in resistance calculations
    - Data range or type errors
    """
    pass


class LinearFitError(ProcessingError):
    """Raised when linear fitting fails on voltage/current data.
    
    Reasons include:
    - Insufficient data points for linear regression
    - All voltage values are identical (undefined slope)
    - NaN or infinite values in the data
    """
    pass


# ============================================================================
# BATCH PROCESSING EXCEPTIONS (Aggregation of Multiple Errors)
# ============================================================================

class BatchProcessingFailure(DatasetProcessingError):
    """Raised when batch processing rejects all files.
    
    This is raised at the end of a batch operation (e.g., validate_all_datasets,
    load_all_datasets) when *all* files are rejected. This helps distinguish
    between "some files failed" (normal, returned in summary dict) and
    "complete batch failure" (error condition).
    
    Attributes:
        rejected_count: Number of files that were rejected
        rejection_reasons: Dict mapping file path to rejection reason
    """
    
    def __init__(self, message: str, rejected_count: int = 0, 
                 rejection_reasons: dict = None):
        self.message = message
        self.rejected_count = rejected_count
        self.rejection_reasons = rejection_reasons or {}
        super().__init__(self.message)
```

### Step 2: Update `validators.py`

Replace generic exceptions with custom ones:

```python
"""Dataset validation module for processing and filtering measurement files."""

import re
import constants
from pathlib import Path
from exceptions import (
    DirectoryValidationError,
    FilenameValidationError,
    FileContentValidationError,
    BatchProcessingFailure
)


def validate_filename(filename: str, pattern: re.Pattern) -> bool:
    """Check if a filename matches the required naming convention pattern.
    
    Args:
        filename: The string filename to validate.
        pattern: A compiled regular expression object defining the naming convention.
    
    Returns:
        True if the filename matches the pattern exactly, False otherwise.
    
    Raises:
        TypeError: If pattern is not a compiled regular expression object.
    """
    if not isinstance(pattern, re.Pattern):
        raise TypeError(f"pattern must be a compiled regex, got {type(pattern)}")
    
    m = pattern.match(filename)
    return bool(m)


def validate_dataset_directory(directory_path: Path, verbose: bool = False) -> Path:
    """Validate that a directory exists, is accessible, and is readable.
    
    Args:
        directory_path: Path object pointing to the dataset directory.
        verbose: If True, print success message. Defaults to False.
    
    Returns:
        The validated Path object (absolute path).
    
    Raises:
        DirectoryValidationError: If directory does not exist, is not a directory,
            or cannot be read due to permissions or filesystem issues.
    """
    # Check if directory exists
    if not directory_path.exists():
        raise DirectoryValidationError(
            f"Directory not found at {directory_path}",
            context=directory_path
        )
    
    # Check if path is actually a directory
    if not directory_path.is_dir():
        raise DirectoryValidationError(
            f"Path exists but is not a directory: {directory_path}",
            context=directory_path
        )
    
    # Check read permissions by attempting to list contents
    try:
        list(directory_path.iterdir())
    except PermissionError as e:
        raise DirectoryValidationError(
            f"Permission denied reading directory: {directory_path}",
            context=directory_path
        ) from e
    except OSError as e:
        raise DirectoryValidationError(
            f"OS-level error accessing directory {directory_path}: {e}",
            context=directory_path
        ) from e
    
    # All validations passed
    if verbose:
        print(
            f"✅ Dataset directory validated successfully at "
            f"{directory_path.resolve()}"
        )
    
    return directory_path.resolve()


def validate_all_datasets(data_dir: Path, pattern: re.Pattern, 
                         verbose: bool = True) -> dict:
    """Scan a directory and validate all dataset files against criteria.
    
    Args:
        data_dir: Path object pointing to the dataset directory to scan.
        pattern: A compiled regular expression object for filename validation.
        verbose: If True, print progress for each file. Defaults to True.
    
    Returns:
        A dict with two keys:
            - "accepted": list of Path objects for valid files.
            - "rejected": dict mapping Path objects to rejection reasons (str).
    
    Raises:
        DirectoryValidationError: If the directory is invalid or inaccessible.
        FileNotFoundError: If the directory contains no files.
        BatchProcessingFailure: If all files in the directory are rejected.
    """
    validation_summary = {"accepted": [], "rejected": {}}
    
    # Validate the directory itself (may raise DirectoryValidationError)
    validated_dir = validate_dataset_directory(data_dir, verbose=verbose)
    
    # Collect all files in the directory
    all_files = sorted(f for f in validated_dir.iterdir() if f.is_file())
    
    # Require at least one file to be present
    if not all_files:
        raise FileNotFoundError(
            f"No files found in directory: {validated_dir}"
        )
    
    # Process each file
    for i, measurement_file in enumerate(all_files, 1):
        full_path = measurement_file.resolve()
        
        if verbose:
            print(f"Processing {i}/{len(all_files)}: {measurement_file.name}")
        
        # Validate file extension
        if measurement_file.suffix.lower() not in constants.ACCEPTED_EXTENSIONS:
            validation_summary["rejected"][full_path] = (
                f"Unsupported file extension: {measurement_file.suffix}"
            )
            continue
        
        # Validate filename against pattern
        if not validate_filename(measurement_file.stem, pattern):
            validation_summary["rejected"][full_path] = "Filename does not match pattern"
            continue
        
        # Check that file is not empty
        if measurement_file.stat().st_size == 0:
            validation_summary["rejected"][full_path] = "Empty file"
            continue
        
        # Validate content: must be readable UTF-8 with at least header + data
        has_content = True
        try:
            with open(measurement_file, "r", encoding="utf-8") as f:
                _header = f.readline()
                data_line = f.readline()
                if not data_line:
                    has_content = False
        except PermissionError:
            validation_summary["rejected"][full_path] = "Permission denied reading file"
            continue
        except UnicodeDecodeError:
            validation_summary["rejected"][full_path] = "File is not valid UTF-8 encoded"
            continue
        except OSError as e:
            validation_summary["rejected"][full_path] = f"Filesystem error: {e}"
            continue
        
        if not has_content:
            validation_summary["rejected"][full_path] = "File contains only header, no data lines"
            continue
        
        validation_summary["accepted"].append(full_path)
    
    # Raise BatchProcessingFailure if all files were rejected
    if not validation_summary["accepted"]:
        raise BatchProcessingFailure(
            f"All files in {validated_dir} were rejected. No valid datasets found.",
            rejected_count=len(validation_summary["rejected"]),
            rejection_reasons=validation_summary["rejected"]
        )
    
    return validation_summary
```

### Step 3: Update `loaders.py`

Replace generic exceptions with custom ones:

```python
"""Measurement Data Ingestion and Processing Module."""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List
import models
import constants
import utils
import calculations
from exceptions import (
    CSVParsingError,
    MissingColumnsError,
    MetadataExtractionError,
    LinearFitError,
    BatchProcessingFailure
)


def load_measurement_csv(filepath: Path, delimiter: str = ',') -> models.Measurement:
    """Load measurement data from a .txt file and convert to Measurement object.
    
    Args:
        filepath: Path to the .txt file containing measurement data.
        delimiter: The separator string used to split columns. Defaults to ','.
    
    Returns:
        A Measurement object containing the validated measurement data.
    
    Raises:
        CSVParsingError: If the file cannot be parsed by pandas or is empty.
        MissingColumnsError: If required measurement columns are missing.
    """
    
    # Attempt to parse CSV
    try:
        raw_df = pd.read_csv(filepath, sep=delimiter)
    except Exception as e:
        raise CSVParsingError(
            f"Failed to parse CSV file at {filepath}. Check delimiter or file integrity.",
            original_error=e
        ) from e
    
    # Check for completely empty files
    if raw_df.empty:
        raise CSVParsingError(
            f"The file at {filepath} is empty."
        )
    
    # Remove leading/trailing whitespace from column names
    raw_df.columns = raw_df.columns.str.strip()
    
    # Validate required columns exist
    missing_columns = [col for col in constants.COLUMN_MAPPING if col not in raw_df.columns]
    if missing_columns:
        raise MissingColumnsError(
            f"The file is missing required columns. Ensure the correct delimiter '{delimiter}' was used.",
            missing_columns=missing_columns,
            found_columns=list(raw_df.columns)
        )
    
    # Rename columns and return as Measurement object
    raw_df = raw_df.rename(columns=constants.COLUMN_MAPPING)
    return models.Measurement.from_dataframe(raw_df)


def load_metadata_csv(filename: str) -> models.Metadata:
    """Parse measurement filename and extract metadata using regex.
    
    Args:
        filename: The measurement filename to parse.
    
    Returns:
        A Metadata object containing parsed and normalized fields.
    
    Raises:
        MetadataExtractionError: If the filename does not match the expected pattern,
            or if numeric/date fields cannot be parsed.
    """
    match = constants.FILENAME_PATTERN.match(filename)
    if not match:
        raise MetadataExtractionError(
            f"Filename format is invalid. Does not match expected pattern.",
            filename=filename
        )
    
    data = match.groupdict()
    
    try:
        # Parse timestamp
        timestamp = datetime.strptime(data["ts"], "%Y%m%d_%H%M%S")
        
        # Parse and normalize pressure
        pressure_torr = utils.normalize_pressure_to_torr(
            data["pressure"], 
            data["press_unit"]
        )
        
        # Parse temperature with unit handling
        temp_val = utils._safe_float(data["temperature"])
        temp_unit = (data["temp_unit"] or "C").upper()
        
        if temp_unit == "C":
            temperature_k = temp_val + constants.CELSIUS_TO_KELVIN
        else:
            temperature_k = temp_val
        
        # Parse alignment
        alignment = utils.check_alignment(data["alignment"])
    
    except (ValueError, TypeError, AttributeError) as err:
        raise MetadataExtractionError(
            f"Failed to parse numeric or date fields from filename '{filename}'.",
            filename=filename
        ) from err
    
    return models.Metadata(
        sample=data["sample"],
        timestamp=timestamp,
        pressure_torr=pressure_torr,
        temperature_k=temperature_k,
        alignment=alignment,
    )


def load_and_process_dataset(measurement_file: Path, delimiter: str = ',') -> models.Dataset:
    """Load a single measurement file and compute all elaborations.
    
    Args:
        measurement_file: Path to the .txt file containing the I(V) measurement.
        delimiter: What delimiter is used in the CSV data. Default = comma.
    
    Returns:
        A Dataset object containing metadata, measurement, and elaborations.
    
    Raises:
        MetadataExtractionError: If filename parsing fails.
        CSVParsingError: If file reading issues occur.
        MissingColumnsError: If required measurement columns are missing.
        LinearFitError: If linear fitting logic crashes.
    """
    
    # Extract metadata from filename
    metadata = load_metadata_csv(measurement_file.stem)
    
    # Load and validate measurement data
    measurement = load_measurement_csv(measurement_file, delimiter=delimiter)
    
    # Convert to DataFrame for elaborations
    voltage_current_df = models.Measurement.to_dataframe(measurement)
    
    # Split data for linear fit by voltage polarity
    positive_VI_df = voltage_current_df[voltage_current_df[constants.ColumnNames.VOLTAGE] > 0]
    negative_VI_df = voltage_current_df[voltage_current_df[constants.ColumnNames.VOLTAGE] < 0]
    
    # Compute fits with error handling
    try:
        elaborations = models.Elaborations(
            global_linear_fit=calculations.linear_fit(
                voltage_current_df[constants.ColumnNames.VOLTAGE], 
                voltage_current_df[constants.ColumnNames.CURRENT]
            ),
            positive_linear_fit=calculations.linear_fit(
                positive_VI_df[constants.ColumnNames.VOLTAGE], 
                positive_VI_df[constants.ColumnNames.CURRENT]
            ),
            negative_linear_fit=calculations.linear_fit(
                negative_VI_df[constants.ColumnNames.VOLTAGE], 
                negative_VI_df[constants.ColumnNames.CURRENT]
            )
        )
    except (ZeroDivisionError, ValueError) as e:
        raise LinearFitError(
            f"Linear fitting failed for {measurement_file.name}. "
            f"Possible causes: insufficient data points, identical voltage values."
        ) from e
    
    return models.Dataset(metadata=metadata, measurement=measurement, elaborations=elaborations)


def load_all_datasets(filtered_files: List[Path], delimiter: str = ',') -> dict:
    """Load and parse dataset files into a collection object.
    
    File-level processing exceptions are caught internally to prevent batch failure.
    
    Args:
        filtered_files: List of validated Path objects to dataset files.
        delimiter: What delimiter is used in the CSV data. Default = comma.
    
    Returns:
        A collection object containing parsed data.
    
    Raises:
        BatchProcessingFailure: If all files are rejected.
    """
    
    loading_summary = {"accepted": {}, "rejected": {}}
    
    for measurement_file in filtered_files:  
        full_path = measurement_file.resolve()
        
        try:
            dataset = load_and_process_dataset(measurement_file, delimiter=delimiter)
        except MetadataExtractionError as e:
            loading_summary["rejected"][full_path] = f"Invalid filename format: {e.message}"
            continue
        except CSVParsingError as e:
            loading_summary["rejected"][full_path] = f"Failed to parse CSV: {e.message}"
            continue
        except MissingColumnsError as e:
            loading_summary["rejected"][full_path] = f"Missing columns: {', '.join(e.missing_columns)}"
            continue
        except LinearFitError as e:
            loading_summary["rejected"][full_path] = f"Processing failed: {e.message}"
            continue
        except Exception as e:
            # Catch unexpected errors
            loading_summary["rejected"][full_path] = f"Unexpected error: {str(e)}"
            continue
        
        # File passed all validations
        loading_summary["accepted"][full_path] = dataset
    
    # Raise BatchProcessingFailure if all files were rejected
    if not loading_summary["accepted"]:
        raise BatchProcessingFailure(
            f"All files were rejected. No valid datasets found.",
            rejected_count=len(loading_summary["rejected"]),
            rejection_reasons=loading_summary["rejected"]
        )
    
    return loading_summary
```

---

## Come Usarle nel Codice Che Chiama

### Scenario 1: Distinguere Errori Specifici

```python
# main.py
from pathlib import Path
from exceptions import (
    BatchProcessingFailure,
    DirectoryValidationError,
    MetadataExtractionError
)
import validators
import loaders


data_dir = Path("./data/measurements")

try:
    # Stage 1: Validation
    validation_results = validators.validate_all_datasets(data_dir, pattern)
    
except DirectoryValidationError as e:
    # Il problema è con la directory stessa → non puoi procedere
    print(f"Setup error: {e.message}")
    print(f"Context: {e.context}")
    exit(1)

except BatchProcessingFailure as e:
    # Nessun file è valido → problema con i file stessi
    print(f"All files rejected. Summary:")
    for path, reason in e.rejection_reasons.items():
        print(f"  {path.name}: {reason}")
    exit(1)


try:
    # Stage 2: Loading
    loading_results = loaders.load_all_datasets(validation_results["accepted"])

except MetadataExtractionError as e:
    # Problema specifico con l'estrazione dei metadati
    print(f"Cannot extract metadata from: {e.filename}")
    print(f"Reason: {e.message}")

except BatchProcessingFailure as e:
    # Tutti i file hanno fallito nel loading
    print(f"Failed to load {e.rejected_count} files")
    for path, reason in e.rejection_reasons.items():
        print(f"  {path.name}: {reason}")
```

### Scenario 2: Catturare Categorie Intere

```python
# Cattura tutti gli errori di validazione (file, directory, contenuto)
try:
    validators.validate_all_datasets(data_dir, pattern)
except ValidationError as e:
    # Questo cattura DirectoryValidationError, FilenameValidationError, 
    # FileContentValidationError e qualsiasi sottoclasse
    print(f"Validation failed: {e.message}")
    if hasattr(e, 'context'):
        print(f"Context: {e.context}")

# Cattura tutti gli errori di loading
try:
    loaders.load_measurement_csv(filepath)
except LoadingError as e:
    # Questo cattura CSVParsingError, MissingColumnsError, MetadataExtractionError
    print(f"Loading failed: {e.message}")
```

### Scenario 3: Logging Strutturato

```python
import logging
from exceptions import DatasetProcessingError

logger = logging.getLogger(__name__)

try:
    validation_results = validators.validate_all_datasets(data_dir, pattern)
    loading_results = loaders.load_all_datasets(validation_results["accepted"])
    
except DatasetProcessingError as e:
    # Log strutturato: il tipo dell'eccezione comunica il problema
    logger.error(
        "Dataset processing failed",
        extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "context": getattr(e, 'context', None),
            "details": {
                "rejected_count": getattr(e, 'rejected_count', None),
                "missing_columns": getattr(e, 'missing_columns', None),
            }
        }
    )
    raise
```

---

## Linee Guida di Design

### 1. Includi Attributi Informativi

Non limitarti al messaggio: aggiungi attributi che il codice che chiama può interrogare:

```python
# ✅ Bene: il codice che chiama può accedere ai dettagli strutturati
raise MissingColumnsError(
    "Missing required columns",
    missing_columns=["Voltage", "Current"],
    found_columns=["V", "I", "Time"]
)

# ❌ Male: tutto è nel messaggio di testo, difficile da parsare
raise ValueError("Missing columns: ['Voltage', 'Current']. Found: ['V', 'I', 'Time']")
```

### 2. Usa `from e` per Preservare il Traceback

```python
try:
    raw_df = pd.read_csv(filepath, sep=delimiter)
except Exception as e:
    # ✅ Bene: il traceback originale è preservato
    raise CSVParsingError(f"Failed to parse {filepath}", original_error=e) from e

# ❌ Male: perdi il traceback originale
except Exception as e:
    raise CSVParsingError(f"Failed to parse {filepath}, original error was {e}")
```

### 3. Mantieni la Gerarchia Coerente

```python
# ✅ Bene: la gerarchia riflette la logica del dominio
class DatasetProcessingError(Exception): pass  # Radice
class ValidationError(DatasetProcessingError): pass  # Categoria 1
class FilenameValidationError(ValidationError): pass  # Specifico

# ❌ Male: gerarchia confusa che non segue il dominio
class MyError1(Exception): pass
class MyError2(Exception): pass  # Non ereditano da una base comune
```

### 4. Non Cambiare le Sottoclassi Quando Catturi

```python
# ✅ Bene: catchi la categoria, consenti a nuovo codice di aggiungere sottoclassi
try:
    validator.validate()
except ValidationError as e:
    handle_validation_error(e)

# ❌ Male: se aggiungi una sottoclasse di ValidationError, il codice non la catturerà
except (FilenameValidationError, FileContentValidationError) as e:
    handle_validation_error(e)
```

---

## Riassunto

| Aspetto | Raccomandazione | Nel Tuo Caso |
|---------|-----------------|-------------|
| **Quando** | Errori semanticamente distinc nei del dominio | Sì: validation, loading, processing sono fasi diverse |
| **Gerarchia** | Radice + categorie + specifici | `DatasetProcessingError` → `ValidationError` / `LoadingError` → specifici |
| **Naming** | `XxxError` per concreti, `Xxx` per astratti | `FilenameValidationError`, `CSVParsingError`, ecc. |
| **Attributi** | Includi dati che il codice che chiama userà | `MissingColumnsError.missing_columns`, `BatchProcessingFailure.rejected_count` |
| **Traceback** | Usa `from e` per preservare lo stack originale | Sì, implementato negli esempi |
| **Redundanza** | Evita sottoclassi senza logica aggiunta | No: ogni sottoclasse aggiunge attributi o comportamento |

Con questa struttura, il tuo codice di pipeline diventa più **leggibile**, **robusto** e **manutenibile**: chi legge il codice capisce il flusso di errori senza dover leggere i messaggi di testo.
