# 📊 I(V)-T Analysis Script

## Overview

This repository contains a lightweight script designed to process electrical measurements of current–voltage (I–V) characteristics acquired at different temperatures.

The typical use case is a set of `.txt` files containing I(V) curves, organized in a CSV-like format, where each file corresponds to a specific temperature.

The script automates the workflow from raw data loading to the generation of a final plot suitable for extracting activation energies.

---

## 🎯 Goal

The current goal of the project is intentionally minimal and focused:

> Provide a clear, ready-to-use plot that allows the user to visually identify slopes and manually estimate one or more activation energies.

In other words, this is not (yet) a fully automated fitting tool — it’s a clean and reliable preprocessing + visualization pipeline.

---

## 📂 Expected Data Structure

The script assumes:

* Multiple `.txt` files
* Each file contains I–V data (Voltage vs Current)
* Files are associated with a measurement temperature
* Data is organized in a consistent CSV-like format

Example (conceptual):

```
T_300K.txt
T_320K.txt
T_340K.txt
...
```

Each file should contain two columns:

```
Voltage, Current
```

---

## ⚙️ What the Script should do

The script should perform the following steps:

1. Loads all measurement files
2. Parses I–V data
3. Associates each dataset with its corresponding temperature
4. Processes the data into a form suitable for activation analysis
5. Generates a final plot (e.g., Arrhenius-like representation)

The output is a visualization from which activation energies can be extracted by evaluating the slope(s) of the relevant regions.

---

## 📈 Output

The main output is a plot that typically represents a transformed version of the data (e.g., logarithmic current vs inverse temperature).

This allows the user to:

* Identify linear regions
* Detect multiple conduction regimes
* Estimate activation energies from slope changes

---

## 🛠️ Future Directions

Potential extensions include:

* Automated linear fitting
* Multi-region slope detection
* Activation energy extraction
* Interactive plotting
* Improved data validation and logging

---

## ▶️ Usage (Conceptual)

```bash
python main.py path/to/data_folder
```

The script will:

* Read all valid files in the directory
* Process the datasets
* Display the final plot

---

## 🤝 Contributing

This is an evolving tool. Contributions, suggestions, and critiques are welcome — especially regarding:

* Data handling robustness
* Visualization clarity
* Physical interpretation workflows

---

## 📌 Notes

This project is intentionally simple and focused. The philosophy is:

> Keep the pipeline transparent, let the researcher interpret the physics.