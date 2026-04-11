# Raster Reclassifier – README
## Overview
Raster Reclassifier is a QGIS plugin that classifies raster values into custom intervals and generates a new reclassified raster.
It supports multiple classification methods, an interactive histogram, customizable colors, and a flexible table‑based workflow for defining class boundaries.

Designed for QGIS 4.x, Qt6, and Python 3.12.

## Features
### Input Raster
* Select any raster layer loaded in QGIS
* Choose the band to analyze
* Compute the histogram on:
  - Full raster extent, or
  - Current map view
* Customize histogram and line colors

### Classification Methods
* Equal Interval
* Quantile
* K‑means
* Natural Breaks (approx.)
* User-defined intervals

### User Mode – Manual Interval Definition
User mode provides two ways to define class boundaries:

1. Manual table editing
Enter interval limits and new class values directly in the table.

2. Interactive histogram clicks
Select a table row and click on the histogram.
The plugin automatically fills the interval boundaries based on the selected row:

### First row:
- Start = raster minimum
- End = clicked value

### Intermediate rows:
- Start = previous row’s End
- End = clicked value

### Penultimate row:
- Same logic as intermediate rows
- The last row is filled automatically

### Last row:
- Start = previous End
- End = raster maximum

Each click draws a vertical line on the histogram:
- One movable line per row
- Automatic fixed boundary lines at xmin and xmax for the first and last intervals

### Table and Statistics
Displays interval limits and new class values

* Shows raster statistics:
  - Count
  - Minimum
  - Maximum
  - Mean
  - Standard deviation
* Import/export interval values from/to CSV or TXT
* User mode supports importing a 3‑column CSV/TXT to populate the table

### Output Raster
* Choose the save path for the reclassified raster
* Optionally load the output raster into QGIS automatically

### Additional Tools
* Reset the session
* Save the interval table
* Export the histogram as PNG/JPG
* Close the plugin

### Workflow
1. Select raster and band
2. Choose classification method
3. Generate histogram and intervals
4. Adjust intervals manually or interactively
5. Set output path
6. Run reclassification

The plugin uses GDAL and NumPy for fast raster processing.

### Compatibility
* QGIS 4.x
* Qt6
* Python 3.12

### Author
Faustino Cetraro  
Geologist, scientific communicator, and software developer
Creator of Plugin Builder Enterprise for QGIS 4 / Qt6  
Developer of geomorphological and scientific tools for QGIS