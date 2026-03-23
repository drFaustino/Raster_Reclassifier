# Changelog – Raster Reclassifier

## [1.0.0] – 2026-03-23
### Added
- Initial public release for QGIS 4 / Qt6.
- Histogram generation for raster values (full extent).
- Raster statistics: count, min, max, mean, standard deviation.
- Classification methods:
  - Equal Interval
  - Quantile
  - User-defined intervals
- Table management:
  - Add / delete rows
  - Import from CSV/TXT
  - Export to CSV/TXT
  - Configurable column delimiter (`;`, `T` for tab)
  - Configurable decimal symbol (`.` or `,`)
- Graph export (PNG/JPG).
- Raster reclassification using GDAL + NumPy.
- Optional automatic loading of the reclassified raster into QGIS.
- Modular architecture (`core/`, `gui/`, `resources/`).
- English documentation (`README.md`).

### Fixed
- Qt6 alignment issues in table cells.
- Color handling between Qt stylesheets and Matplotlib (conversion from `rgb(r,g,b)` to `#rrggbb`).

### Notes
- Designed and tested for QGIS 4.x and Python 3.12.
- Future versions may add Processing Toolbox integration and localized documentation.
