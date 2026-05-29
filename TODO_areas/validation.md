# Orchestrator Implementation Todo-List

## Phase 1: Define Naming Convention Validator

- [ ] **Create `build_naming_pattern()` function**
  - Build regex pattern from `load_metadata_csv` requirements
  - Pattern should match: `YYYYMMDD_HHMMSS_SAMPLE_PPRESSURE_TTEMPERATURE[_(AB|BA)].txt`
  - Include optional alignment suffix `(AB|BA)?`
  - Include optional pressure/temp suffixes (torr, C)
  - Return compiled regex pattern or raw pattern string
  - Add docstring with example patterns matching

- [ ] **Create `validate_filename_convention(filename: str, pattern) -> bool`**
  - Accept filename and regex pattern
  - Return True/False (simple check)
  - Does NOT attempt to parse metadata yet (that's parsing, not validation)
  - Add docstring with examples

## Phase 2: Create File-Level Validator Integration

- [ ] **Extend `validate_measurement_file()` call signature** (optional but cleaner)
  - Consider: `validate_measurement_file(filepath, naming_pattern=None)`
  - If naming_pattern provided, check convention first
  - Or: keep it separate and call both checks in orchestrator

- [ ] **Decide error reporting strategy per file**
  - Naming error: `{filename}: does not match naming convention`
  - Content error from `validate_measurement_file()`: reuse existing messages
  - Keep format consistent for batch reporting

## Phase 3: Build the Orchestrator

- [ ] **Create `validate_dataset_directory()` v2**
  - Accept parameters:
    - `directory_path: Path` (required)
    - `naming_pattern` (default: auto-generated from `load_metadata_csv` spec)
    - `required_extension: str = "*.txt"`
    - `min_files: int = 1`
    - `verbose: bool = True`
  
- [ ] **Implement orchestrator logic**
  - Validate directory exists/is readable (reuse existing checks)
  - Glob for matching files
  - **FOR EACH FILE:**
    - [ ] Check naming convention (regex match on filename only)
    - [ ] If naming OK: call `validate_measurement_file(filepath)`
    - [ ] Collect both naming errors AND content errors
  - Accumulate all errors in a list/dict

- [ ] **Implement error aggregation**
  - Separate errors into categories:
    - Naming convention violations
    - Content/quality violations (empty, bad encoding, header-only)
  - Track filename for each error type
  - Keep count for summary

- [ ] **Implement success path**
  - Return list of validated `Path` objects (only files that passed both checks)
  - Or return tuple: `(validated_paths, errors_dict)` if you want to log failures
  - Print summary: "X files passed, Y naming errors, Z content errors"

## Phase 4: Error Reporting

- [ ] **Build error message format**
  - Example output:
    ```
    Validation failed: 8/10 files have issues
    
    Naming convention violations (3 files):
      • bad_filename.txt: does not match pattern
      • 20260101_SAMPLE.txt: does not match pattern
      • measurement_old.txt: does not match pattern
    
    Content validation failures (5 files):
      • 20260301_120000_Au_P1e-3torr_T300C.txt: empty file (0 bytes)
      • 20260302_140000_Cu_P1e-3torr_T350C.txt: header only, no data rows
      • 20260303_160000_Ag_P1e-3torr_T400C.txt: invalid UTF-8 encoding
      • ...
    
    Fix these issues and retry.
    ```

- [ ] **Decide on return behavior**
  - Option A: Raise `SystemExit` if ANY errors (current approach)
  - Option B: Return validated list even if some files failed, let caller decide
  - Option C: Add `strict: bool` parameter to choose behavior

## Phase 5: Integration & Testing

- [ ] **Test with sample directory structure**
  - Create test files with:
    - Correct naming, valid content ✓
    - Correct naming, empty file ✗
    - Correct naming, header-only ✗
    - Wrong naming, valid content ✗
    - Wrong naming, empty ✗

- [ ] **Test error reporting**
  - Verify all error types appear together
  - Verify filenames are clear
  - Verify counts are accurate

- [ ] **Add logging (optional)**
  - Log validated files at INFO level
  - Log errors at ERROR level
  - Makes debugging easier for batch runs

## Phase 6: Documentation & Refinement

- [ ] **Write orchestrator docstring**
  - Explain two-stage filtering (naming → content)
  - Show example usage with batch directory
  - Document error output format

- [ ] **Consider edge cases**
  - Empty directory
  - Directory with files but none match extension
  - Directory with files, all have naming errors
  - Directory with files, all have content errors
  - Very large directories (performance?)

- [ ] **Optional: Add metadata extraction validation**
  - After files pass naming + content checks
  - Try calling `load_metadata_csv()` on each file
  - Add parsing errors to error report
  - Only return files that successfully parse metadata

---

## Implementation Order (Recommended)

1. **Build naming pattern** (Phase 1)
2. **Create orchestrator skeleton** (Phase 3 structure)
3. **Add naming check logic** (Phase 3)
4. **Add content check integration** (Phase 3)
5. **Build error aggregation** (Phase 4)
6. **Test with sample files** (Phase 5)
7. **Add logging & polish** (Phase 6)

---

## Code Structure (pseudocode)

```python
def validate_dataset_directory(directory_path, naming_pattern=None, ...):
    # Phase 1: Validate directory
    if not directory_path.exists():
        raise SystemExit(...)
    
    # Phase 2: Collect files
    all_files = sorted(directory_path.glob("*.txt"))
    
    # Phase 3: Validate each file
    validated_files = []
    errors_by_category = {
        "naming": [],
        "content": []
    }
    
    for filepath in all_files:
        # Check naming
        if not validate_filename_convention(filepath.name, naming_pattern):
            errors_by_category["naming"].append(filepath.name)
            continue
        
        # Check content
        try:
            validate_measurement_file(filepath)
            validated_files.append(filepath)
        except SystemExit as e:
            errors_by_category["content"].append((filepath.name, str(e)))
    
    # Phase 4: Report results
    if any(errors_by_category.values()):
        raise SystemExit(format_error_report(errors_by_category))
    
    print(f"✓ Validated {len(validated_files)} files")
    return validated_files
```