# Raster Reclassifier
### A QGIS 4 / Qt6 plugin for raster histogram analysis and value reclassification

## 🧭 Overview
**Raster Reclassifier** is a QGIS plugin designed to simplify the analysis of raster value distributions and the reclassification of raster datasets using intuitive, table‑based rules.

It provides:
- Histogram visualization
- Raster statistics (min, max, mean, std, count)
- Automatic interval generation (Equal Interval, Quantile)
- Manual interval definition (User mode)
- Table import/export (CSV/TXT)
- Graph export (PNG/JPG)
- Raster reclassification using GDAL + NumPy
- Optional automatic loading of the output raster into QGIS

Fully compatible with **QGIS 4.x** and **Qt6**.

---

## ✨ Features

### 📊 Histogram & Statistics
- Generates a histogram of raster values (full raster extent)
- Customizable histogram color
- Vertical class‑break lines with customizable color
- Displays:
  - Count of valid cells  
  - Minimum value  
  - Maximum value  
  - Mean  
  - Standard deviation  

---

### 🧮 Classification Methods

| Method | Description |
|--------|-------------|
| **Equal Interval** | Divides the value range into equal‑sized intervals |
| **Quantile** | Divides values into classes with equal number of pixels |
| **User** | Allows manual definition of Start / End / New values |

The resulting intervals populate the table automatically.

---

### 📝 Table Management
- Add new rows  
- Delete selected row  
- Import table from CSV/TXT  
- Export table to CSV/TXT  
- Choose:
  - Column delimiter (`;`, `T` for tab)  
  - Decimal symbol (`.` or `,`)  

---

### 🗺️ Raster Reclassification
The plugin performs raster reclassification using:

- **GDAL** for reading/writing GeoTIFF  
- **NumPy** for fast array operations  

Rules are applied as:

The output raster:
- Preserves georeferencing  
- Preserves NoData  
- Is saved as GeoTIFF  
- Can be automatically loaded into QGIS  

---

## 📂 File Structure

raster_reclassifier/
│
├── init.py
├── metadata.txt
├── raster_reclassifier.py
│
├── core/
│   └── reclassifier_engine.py
│
├── gui/
│   ├── dialog.py
│   ├── raster_reclassifier_dialog_base.ui
│   └── dlg_settings.ui (optional)
│
├── resources/
│   └── icon.png
│
└── README.md

---

## 🚀 Installation

1. Copy the plugin folder `raster_reclassifier` into:


2. Restart QGIS  
3. Enable **Raster Reclassifier** from:  
*Plugins → Manage and Install Plugins*

---

## 🛠️ Requirements

- QGIS 4.x  
- Python 3.12  
- GDAL  
- NumPy  
- Matplotlib  

All dependencies are included in standard QGIS installations.

---

## 📖 Usage

1. Select a raster layer  
2. Choose a band  
3. Click **Extract** to compute histogram and statistics  
4. Choose classification method  
5. Edit or import table values  
6. Select output raster path  
7. Click **Run** to perform reclassification  
8. Optionally load the output raster into QGIS  

---

## 🧑‍💻 Author

**Dr. Geol. Faustino Cetraro**  
Scientific communicator & GIS developer  

---

## 📜 License

This plugin is released under the **GNU GPL v2** (or later).

---

## 🗂️ Changelog

### **1.0.0**
- Full rewrite for QGIS 4 / Qt6  
- Histogram generation  
- Equal Interval, Quantile, User classification  
- Table import/export  
- Graph export  
- GDAL/NumPy raster reclassification  
- Automatic output loading  
- UI cleanup and stability improvements
