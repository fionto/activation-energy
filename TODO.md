# 🧭 TODO — I(V)-T Analysis Script

A rough development roadmap from raw file handling to final plotting.

---

## 📥 Data Ingestion

* [x] Define input directory structure
* [x] Loop over files in directory
* [x] Filter `.txt` files only
* [x] Open files using `with open(...)`
* [ ] Read file contents safely
* [ ] Handle empty or malformed files

---

## 🔍 Parsing & Formatting

* [x] Split lines into columns (CSV-like parsing)
* [x] Extract voltage, current and standard deviation columns
* [x] Convert strings to numeric types
* [ ] Handle headers (skip or detect automatically)
* [x] Store data in structured format (e.g., lists, dicts, or pandas DataFrame)
* [x] Separate meta / data in the structured dict

---

## 🌡️ Temperature Handling

* [x] Extract temperature from filename or file content
* [x] Standardize temperature units (e.g., Kelvin)
* [x] Associate each dataset with its temperature
* [ ] Sort datasets by temperature

---

## ⚙️ Data Processing

* [ ] Select relevant voltage region (optional filtering)
* [ ] Compute derived quantities (e.g., conductance or current at fixed voltage)
* [ ] Prepare data for Arrhenius-like transformation
* [ ] Compute inverse temperature (1/T)
* [ ] Apply logarithmic transformation to current (or chosen observable)

---

## 📊 Visualization

* [ ] Initialize plotting environment (matplotlib or similar)
* [ ] Plot transformed data (e.g., log(I) vs 1/T)
* [ ] Label axes clearly
* [ ] Add title and legend (if multiple datasets)
* [ ] Ensure readability (scales, grid, formatting)

---

## 🧪 Output & Validation

* [ ] Display plot to user
* [ ] Optionally save plot to file
* [ ] Validate output visually (linear regions visible)

---

## 🚧 Nice-to-Have (Later)

* [ ] Basic error handling and logging
* [ ] CLI arguments for input/output control
* [ ] Modularize code (functions for each step)
* [ ] Add simple documentation/comments in code

---

## 🎯 End Goal

Produce a clean plot that enables manual extraction of activation energy from slope(s).
