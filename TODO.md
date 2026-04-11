# 🧭 TODO — I(V)-T Analysis Script

A rough development roadmap from raw file handling to final plotting.

---

## 📥 Data Ingestion

* [ ] Define input directory structure
* [ ] Loop over files in directory
* [ ] Filter `.txt` files only
* [ ] Open files using `with open(...)`
* [ ] Read file contents safely
* [ ] Handle empty or malformed files

---

## 🔍 Parsing & Formatting

* [ ] Split lines into columns (CSV-like parsing)
* [ ] Extract voltage and current columns
* [ ] Convert strings to numeric types
* [ ] Handle headers (skip or detect automatically)
* [ ] Store data in structured format (e.g., lists, dicts, or pandas DataFrame)

---

## 🌡️ Temperature Handling

* [ ] Extract temperature from filename or file content
* [ ] Standardize temperature units (e.g., Kelvin)
* [ ] Associate each dataset with its temperature
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
