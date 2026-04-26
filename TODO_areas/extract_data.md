# Task List: I(V) Extraction Script Refactor

## 1. Correctness & Robustness
- [x] **Handle empty files:** Wrap the header skip `next(txt_data)` in a `try-except StopIteration` block.
- [x] **Verify file size before reading**: Use `file_path.stat().st_size` to identify empty files before attempting to open them.
- [x] **Verify directory existence:** Add a check using `raw_dataset_path.exists()` and `is_dir()` before calling `.iterdir()` to prevent runtime crashes.
- [ ] **Replace silent `NaN` failures:** Modify `_safe_float` to raise a custom `DataParsingError` or log a warning. Why allow corrupted data to silently enter your final dataset?

## 2. Structural Design
- [x] **Encapsulate execution in `main()`:** Move the logic currently under `if __name__ == "__main__"` into a dedicated `main()` function to prevent global scope pollution.
- [ ] **Implement `argparse`:** Replace hardcoded global paths with command-line arguments. Can this script be useful to a colleague if they have to edit your source code just to change the input folder?
- [x] **Decompose `extract_from_dir`:** Extract the nested loop responsible for transposing rows into columns into a standalone helper function. 

## 3. Data Representation & Style
- [ ] **Refactor to `dataclasses`:** Replace the nested dictionary structure with a `Measurement` dataclass. This will clarify the "contract" of what a curve contains and improve readability.
- [ ] **Integrate `csv` module:** Replace manual `.split(',')` and `.strip()` logic in `parse_row` with `csv.DictReader` or `csv.reader` for more resilient parsing.
- [x] **Standardize type hints:** Use `typing.TypedDict` or specific classes instead of the generic `list[dict]`. What exactly is inside that dictionary? Make it explicit.
- [x] **Refactor docstrings:** Rewrite docstrings to focus on the "what" and "why" of the interface, moving implementation details (the "how") into standard comments.