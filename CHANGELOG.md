# Changelog

## [1.1.2] – 2026‑09‑04
- Removed broad exception handlers that triggered the QGIS security scanner.
- Replaced exception-driven line cleanup with explicit Matplotlib artist state checks.
- Removed exception-based color fallback and validate QColor-like objects before conversion.
- Kept the plugin free of `pass` statements and ambiguous variable names.

# Changelog – Raster Reclassifier
## [1.1.1] – 2026‑05‑21
### Added robust numeric validation in the reclassification engine:  
Reclassification rules are now checked with a try/except block to prevent crashes when table cells contain empty, non‑numeric, or improperly formatted values. The plugin now displays a clear error message indicating the problematic row and stops processing safely instead of failing at 20%.

## [1.1.0] – 2026‑04‑11
### Added
* Full support for interactive interval definition in User mode:
  - Select a table row and click on the histogram to set interval boundaries.
  - Automatic interval filling based on row position:
    - First row: xmin → clicked value
    - Intermediate rows: previous End → clicked value
    - Penultimate row: same logic + automatic filling of the last row
    - Last row: previous End → xmax
  - Dynamic drawing of vertical lines:
    - One movable line per row (updated on each click)
    - Automatic fixed boundary lines at xmin and xmax for the first and last intervals
* Improved line‑drawing engine with per‑row line tracking (_row_lines, _fixed_lines)
* Enhanced histogram refresh from table values
* Updated documentation and in‑plugin help text

### Improved
* More robust handling of color conversion between Qt and Matplotlib
* Cleaner table population logic for User mode
* Better validation of interval values and row dependencies
* More stable behavior when switching between classification methods

### Fixed
* Multiple vertical lines being drawn for the same row
* Missing boundary lines for first and last intervals
* Issues with empty or invalid table cells during interactive editing
* Minor UI alignment and refresh issues under Qt6

### Notes
* Designed and tested for QGIS 4.x, Qt6, and Python 3.12
* Future updates will focus on:
  - Processing Toolbox integration
  - Additional classification methods
  - Multi‑band workflows
  - Localized documentation

## [1.0.0] – 2026‑03‑23
### Added
* Initial public release for QGIS 4 / Qt6
* Histogram generation (full extent)
* Raster statistics: count, min, max, mean, standard deviation
* Classification methods:
  - Equal Interval
  - Quantile
  - User-defined intervals
* Table management:
  - Add / delete rows
  - Import from CSV/TXT
  - Export to CSV/TXT
  - Configurable column delimiter (;, T for tab)
  - Configurable decimal symbol (. or ,)
* Graph export (PNG/JPG)
* Raster reclassification using GDAL + NumPy
* Optional automatic loading of the reclassified raster into QGIS
* Modular architecture (core/, gui/, resources/)
* English documentation (README.md)

### Fixed
* Qt6 table alignment issues
* Color handling between Qt stylesheets and Matplotlib

### Notes
* Designed and tested for QGIS 4.x and Python 3.12
* Planned future improvements include Processing Toolbox integration and localized documentation
