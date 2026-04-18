## 1. Correctness

The function `extract_curve_points` contains a fragile assumption that every file processed will contain at least one line of data. By calling `next(txt_data)` immediately upon opening the file, the script will raise a `StopIteration` exception and terminate if it encounters an empty `.txt` file. This prevents the processing of any subsequent valid files in the directory. You should check if the file is empty or wrap the header skip in a try-except block to ensure robustness.

The `_safe_float` utility introduces a silent failure mode. While returning `NaN` prevents the script from crashing on a malformed string, it allows "poisoned" data to enter your dataset without warning. If a measurement tool writes an error message into a data column, your final pickle file will contain invalid floats that may break downstream analysis or curve-fitting. A better approach would be to log the error or raise a specific exception that the caller can handle to skip only that specific record or file.

The path definitions for `raw_dataset_path` and `save_path` assume a rigid directory structure relative to the script's location. If the `data` folder or the specific `E14_FS` subfolder is missing, `extract_from_dir` will likely fail when it attempts to call `.iterdir()` on a non-existent path. There are no checks to verify that these paths exist before the script begins execution.

## 2. Design

The script relies on global variables for configuration. Defining `raw_dataset_path` and `save_path` at the top level of the module tightly couples the script to a specific machine's file layout. This makes it impossible to import these functions into another script without triggering side effects or needing to modify the source code. These values should be passed as arguments to your functions or handled within a `main` function.

The function `extract_from_dir` is overloaded with responsibilities. It handles directory traversal, file filtering, data structure initialization, and the transformation of row-based data into column-based lists. This "God function" pattern makes the code harder to test. Specifically, the nested loop that transposes the data points should be its own function, allowing you to test the transformation logic independently of the file system.

The data structure created by `build_data_structure` is highly repetitive and memory-inefficient for large datasets. By storing data as a list of dictionaries where each dictionary contains redundant lists, you are creating a complex hierarchy that is difficult to query. For scientific data of this nature, you should consider a design that separates the metadata from the numerical arrays entirely.

## 3. Style

Type annotations are present but inconsistently applied and occasionally too vague. For instance, `extract_from_dir` is annotated as returning `list[dict]`, which provides no information about the internal structure of those dictionaries (e.g., that they contain `METADATA` and `DATA` keys). Using `TypedDict` or a simple `Dataclass` would make the data contract explicit and allow tools like `mypy` to catch key errors before runtime.

The docstrings frequently describe "how" the code works rather than "what" it does. In `extract_from_dir`, the comment "here I have to transform the list of dictionaries..." is an implementation detail that belongs in the code as a comment, if anywhere. A docstring should define the inputs, outputs, and the purpose of the function. Additionally, your constants are well-defined, but they are mixed with logic at the top of the file rather than being grouped together.

Naming conventions generally follow PEP 8, but `_safe_float` uses an underscore prefix usually reserved for internal class methods, though here it serves to indicate a "private" helper. However, the logic inside `parse_filename` relies on `removesuffix`, which was introduced in Python 3.9. While this is clean, the script lacks a version check or documentation indicating this dependency, which could lead to cryptic `AttributeError` messages for users on older Python environments.

## 4. Scope for improvement

1. Use `argparse` to accept the dataset path and output file as command-line arguments. (Decouples the logic from the file system and allows you to run the script on different datasets without editing the code.)
2. Replace manual string splitting in `parse_row` with the `csv` module. (Standardizes the handling of delimiters and whitespace, making the parser more resilient to variations in file formatting.)
3. Implement a `main` function to encapsulate the execution logic. (Ensures that the script does not execute its parsing logic automatically if it is imported as a module by another program.)
4. Replace `NaN` returns in `_safe_float` with a custom exception or logging. (Ensures that data integrity issues are surfaced to the researcher immediately rather than being hidden in the output file.)
5. Use a `Dataclass` for the measurement objects instead of nested dictionaries. (Provides a clear schema for your data and enables better IDE autocompletion and error checking.)