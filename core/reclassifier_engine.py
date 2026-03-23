# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QFileDialog, QMessageBox, QTableWidgetItem, QGraphicsScene
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsRasterBandStats
)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from osgeo import gdal


class ReclassifierEngine:

    def __init__(self, dlg):
        self.dlg = dlg
        self.canvas = None

    # ----------------------------------------------------------
    # RASTER E BANDE
    # ----------------------------------------------------------
    def populate_raster_list(self):
        self.dlg.cmb_raster_load.clear()
        layers = [
            lyr for lyr in QgsProject.instance().mapLayers().values()
            if isinstance(lyr, QgsRasterLayer)
        ]
        for lyr in layers:
            self.dlg.cmb_raster_load.addItem(lyr.name(), lyr.id())

    def populate_bands(self):
        raster_id = self.dlg.cmb_raster_load.currentData()
        layer = QgsProject.instance().mapLayer(raster_id)

        self.dlg.cmb_field.clear()
        if not layer:
            return

        provider = layer.dataProvider()
        for band in range(1, provider.bandCount() + 1):
            self.dlg.cmb_field.addItem(f"Band {band}", band)

    # ----------------------------------------------------------
    # ISTOGRAMMA
    # ----------------------------------------------------------
    def create_empty_histogram(self):
        plt.close("all")
        fig = plt.figure(figsize=(4.41, 3.41))
        ax = fig.add_subplot(111)
        ax.set_title("Histogram", fontweight="bold")
        ax.grid(True)
        self._draw_canvas(fig)

    def create_histogram(self):
        try:
            self._set_progress(0)
            raster_id = self.dlg.cmb_raster_load.currentData()
            layer = QgsProject.instance().mapLayer(raster_id)

            if not layer:
                QMessageBox.warning(self.dlg, "Error", "No raster selected.")
                return

            band_index = self.dlg.cmb_field.currentData()
            provider = layer.dataProvider()

            stats = provider.bandStatistics(band_index, QgsRasterBandStats.All)
            min_val, max_val = stats.minimumValue, stats.maximumValue

            extent = layer.extent()
            cols, rows = layer.width(), layer.height()
            block = provider.block(band_index, extent, cols, rows)

            raster_data = np.array(
                [[block.value(c, r) for c in range(cols)] for r in range(rows)],
                dtype=float
            )

            self._set_progress(10)

            nodata = provider.sourceNoDataValue(band_index)
            masked = np.ma.masked_equal(raster_data, nodata)

            valid_cells = np.count_nonzero(~masked.mask)

            self.dlg.lineEdit_count.setText(str(valid_cells))
            self.dlg.lineEdit_min.setText(f"{min_val:.2f}")
            self.dlg.lineEdit_max.setText(f"{max_val:.2f}")
            self.dlg.lineEdit_mean.setText(f"{stats.mean:.2f}")
            self.dlg.lineEdit_std.setText(f"{stats.stdDev:.2f}")

            num_classes = self.dlg.spinBox_classes.value()
            method = self.dlg.cmb_method.currentIndex()

            if method == 0:
                breaks = np.linspace(min_val, max_val, num_classes + 1)
            elif method == 1:
                breaks = np.percentile(masked.compressed(), np.linspace(0, 100, num_classes + 1))
            elif method == 2:
                breaks = [None] * (num_classes + 1)
            else:
                QMessageBox.warning(self.dlg, "Error", "Unsupported method.")
                return
            
            self._set_progress(30)

            self.dlg.tableWidget_value.setRowCount(num_classes)
            for i in range(num_classes):
                if method == 2:
                    start = QTableWidgetItem("")
                    end = QTableWidgetItem("")
                else:
                    start = QTableWidgetItem(f"{breaks[i]:.2f}")
                    end = QTableWidgetItem(f"{breaks[i+1]:.2f}")

                new = QTableWidgetItem("")

                for item in (start, end, new):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.dlg.tableWidget_value.setItem(i, 0, start)
                self.dlg.tableWidget_value.setItem(i, 1, end)
                self.dlg.tableWidget_value.setItem(i, 2, new)

            self._set_progress(60)

            hist_color = self._get_label_color(self.dlg.label_10)
            class_color = self._get_label_color(self.dlg.label_12)

            plt.close("all")
            fig = plt.figure(figsize=(4.41, 3.41))
            ax = fig.add_subplot(111)
            ax.grid(True)

            ax.hist(masked.compressed(), bins=200, color=hist_color, alpha=0.7)

            if method != 2:
                for b in breaks:
                    ax.axvline(b, color=class_color, linestyle="--", linewidth=1)

            self._draw_canvas(fig)

            self._set_progress(100)  # completato
            self._set_progress(0)

        except Exception as e:
            QMessageBox.critical(self.dlg, "Error", str(e))

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------
    def select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self.dlg, "Select output raster", "", "GeoTIFF (*.tif)"
        )
        if path:
            if not path.lower().endswith(".tif"):
                path += ".tif"
            self.dlg.lineEdit_output.setText(path)

    # ----------------------------------------------------------
    # IMPORT / EXPORT
    # ----------------------------------------------------------
    def import_values(self):
        path, _ = QFileDialog.getOpenFileName(
            self.dlg, "Import table", "", "CSV (*.csv);;Text (*.txt)"
        )
        if not path:
            return

        self._set_progress(0)

        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    delimiter = self.dlg.comboBox_col_delim.currentText()
                    delimiter = "\t" if delimiter == "T" else delimiter

                    rows.append(line.split(delimiter))

        self._set_progress(50)

        self.dlg.tableWidget_value.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c in range(min(3, len(row))):
                item = QTableWidgetItem(row[c])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.dlg.tableWidget_value.setItem(r, c, item)
        
        self._set_progress(100)
        self._set_progress(0)

    def add_new_row(self):
        row = self.dlg.tableWidget_value.rowCount()
        self.dlg.tableWidget_value.insertRow(row)
        for c in range(3):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dlg.tableWidget_value.setItem(row, c, item)

    def delete_selected_row(self):
        table = self.dlg.tableWidget_value
        selected = table.currentRow()

        if selected < 0:
            QMessageBox.warning(self.dlg, "Warning", "No row selected.")
            return

        table.removeRow(selected)

    def save_table(self):
        path, _ = QFileDialog.getSaveFileName(
            self.dlg, "Save table", "", "CSV (*.csv);;Text (*.txt)"
        )
        if not path:
            return

        self._set_progress(0)

        delimiter = self.dlg.comboBox_col_delim.currentText()
        delimiter = "\t" if delimiter == "T" else delimiter
        decimal = self.dlg.comboBox_decimals.currentText()

        with open(path, "w", encoding="utf-8") as f:
            for r in range(self.dlg.tableWidget_value.rowCount()):
                vals = []
                for c in range(3):
                    item = self.dlg.tableWidget_value.item(r, c)
                    txt = item.text().replace(".", decimal).replace(",", decimal)
                    vals.append(txt)
                f.write(delimiter.join(vals) + "\n")
        
        self._set_progress(100)
        self._set_progress(0)

    def save_graph(self):
        if not self.canvas:
            QMessageBox.warning(self.dlg, "Empty", "No graph to save.")
            return
        
        self._set_progress(0)

        path, _ = QFileDialog.getSaveFileName(
            self.dlg, "Save graph", "", "PNG (*.png);;JPG (*.jpg)"
        )
        if not path:
            return

        self.canvas.figure.savefig(path, dpi=300)
        
        self._set_progress(100)
        self._set_progress(0)

    # ----------------------------------------------------------
    # RESET
    # ----------------------------------------------------------
    def reset(self):
        self.dlg.lineEdit_count.clear()
        self.dlg.lineEdit_min.clear()
        self.dlg.lineEdit_max.clear()
        self.dlg.lineEdit_mean.clear()
        self.dlg.lineEdit_std.clear()
        self.dlg.lineEdit_output.clear()
        self.dlg.tableWidget_value.clearContents()
        self.dlg.tableWidget_value.setRowCount(0)
        self.create_empty_histogram()
        self._set_progress(0)

    # ----------------------------------------------------------
    # RICLASSIFICAZIONE (placeholder)
    # ----------------------------------------------------------
    def run_reclassification(self):
        QMessageBox.information(
            self.dlg,
            "Info",
            "Raster reclassification logic not yet implemented in this version."
        )

        # ----------------------------------------------------------
    # RICLASSIFICAZIONE RASTER (GDAL + NumPy)
    # ----------------------------------------------------------
    def run_reclassification(self):
        try:
            self._set_progress(0)

            # 1. Raster selezionato
            raster_id = self.dlg.cmb_raster_load.currentData()
            layer = QgsProject.instance().mapLayer(raster_id)

            self._set_progress(10)

            if not layer:
                QMessageBox.warning(self.dlg, "Error", "No raster selected.")
                self._set_progress(0)
                return

            # 2. Banda selezionata
            band_index = self.dlg.cmb_field.currentData()
            if band_index is None:
                QMessageBox.warning(self.dlg, "Error", "No band selected.")
                self._set_progress(0)
                return

            # 3. Percorso output
            out_path = self.dlg.lineEdit_output.text().strip()
            if not out_path:
                QMessageBox.warning(self.dlg, "Error", "No output path selected.")
                self._set_progress(0)
                return

            # 4. Leggi tabella Start / End / New
            self._set_progress(20)

            table = self.dlg.tableWidget_value
            rules = []

            for r in range(table.rowCount()):
                start_item = table.item(r, 0)
                end_item = table.item(r, 1)
                new_item = table.item(r, 2)

                if not start_item or not end_item or not new_item:
                    continue

                decimal_symbol = self.dlg.comboBox_decimals.currentText()

                start = start_item.text().strip()
                end = end_item.text().strip()
                new = new_item.text().strip()

                # Normalizza i decimali (NumPy/GDAL vogliono sempre il punto)
                if decimal_symbol == ",":
                    start = start.replace(",", ".")
                    end = end.replace(",", ".")
                    new = new.replace(",", ".")

                # Converti in float
                start = float(start)
                end = float(end)
                new = float(new)

                rules.append((start, end, new))

            if not rules:
                QMessageBox.warning(self.dlg, "Error", "No valid reclassification rules.")
                return

            # 5. Apri raster con GDAL
            self._set_progress(50)

            src = gdal.Open(layer.dataProvider().dataSourceUri())
            band = src.GetRasterBand(band_index)
            arr = band.ReadAsArray().astype(float)

            nodata = band.GetNoDataValue()
            if nodata is None:
                nodata = -9999

            # 6. Applica riclassificazione
            self._set_progress(60)

            out_arr = np.full(arr.shape, nodata, dtype=float)

            for start, end, new in rules:
                mask = (arr >= start) & (arr < end)
                out_arr[mask] = new

            # 7. Crea GeoTIFF in output
            driver = gdal.GetDriverByName("GTiff")
            out_ds = driver.Create(
                out_path,
                src.RasterXSize,
                src.RasterYSize,
                1,
                gdal.GDT_Float32
            )

            self._set_progress(80)

            out_ds.SetGeoTransform(src.GetGeoTransform())
            out_ds.SetProjection(src.GetProjection())

            out_band = out_ds.GetRasterBand(1)
            out_band.WriteArray(out_arr)
            out_band.SetNoDataValue(nodata)
            out_band.FlushCache()

            out_ds = None  # chiudi file

            # 8. Carica in QGIS se richiesto
            if self.dlg.checkBox_load_prg.isChecked():
                new_layer = QgsRasterLayer(out_path, "Reclassified")
                if new_layer.isValid():
                    QgsProject.instance().addMapLayer(new_layer)
            
            self._set_progress(100)

            QMessageBox.information(self.dlg, "Done", "Raster reclassification completed.")

            self._set_progress(0)

        except Exception as e:
            QMessageBox.critical(self.dlg, "Error", f"Reclassification failed:\n{e}")


    # ----------------------------------------------------------
    # UTILITY
    # ----------------------------------------------------------
    def _draw_canvas(self, fig):
        self.canvas = FigureCanvas(fig)
        scene = QGraphicsScene()
        scene.addWidget(self.canvas)
        self.dlg.graphicsView_hystogram.setScene(scene)
        self.canvas.draw()
    
    def _set_progress(self, value):
        """Aggiorna la progress bar in modo sicuro."""
        try:
            self.dlg.progressBar.setValue(value)
        except:
            pass


    def _get_label_color(self, label):
        style = label.styleSheet()
        if "background-color:" not in style:
            return "#000000"

        raw = style.split("background-color:")[1].split(";")[0].strip()

        if raw.startswith("#"):
            return raw

        if raw.startswith("rgb"):
            inside = raw[raw.find("(")+1 : raw.find(")")]
            r, g, b = [int(v.strip()) for v in inside.split(",")]
            return "#{:02x}{:02x}{:02x}".format(r, g, b)

        return raw

