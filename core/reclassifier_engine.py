# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtWidgets import (
    QFileDialog, QMessageBox, QTableWidgetItem, QGraphicsScene
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsRasterBandStats, QgsApplication
)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from osgeo import gdal

from .reclassifier_task import ReclassifierTask
from qgis.PyQt.QtCore import QCoreApplication

class ReclassifierEngine:

    def __init__(self, dlg, hist_color=None, line_color=None):
        self.dlg = dlg
        self.canvas = None
        self.figure = None
        self.scene = None

        self.hist_color = hist_color
        self.line_color = line_color

        self.enable_user_clicks = False
        self.user_clicks = []
        self._row_lines = {} # linee Xsel per riga
        self._fixed_lines = {} # linee xmin/xmax per riga

        self.min_val = None
        self.max_val = None

        # Linee degli intervalli disegnate sul grafico
        self._interval_lines = []

    def tr(self, text):
        return QCoreApplication.translate("ReclassifierEngine", text)

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
        self.dlg.cmb_field.clear()
        raster_id = self.dlg.cmb_raster_load.currentData()
        layer = QgsProject.instance().mapLayer(raster_id)
        if not layer:
            return

        provider = layer.dataProvider()
        for band in range(1, provider.bandCount() + 1):
            self.dlg.cmb_field.addItem(self.tr(f"Band {band}"), band)

    # ----------------------------------------------------------
    # COLORI TUPLA
    # ----------------------------------------------------------
    def _qcolor_to_mpl(self, qcolor):
        return (
            qcolor.red() / 255,
            qcolor.green() / 255,
            qcolor.blue() / 255
        )

    # ----------------------------------------------------------
    # ISTOGRAMMA
    # ----------------------------------------------------------
    def create_empty_histogram(self):
        plt.close("all")
        fig = plt.figure(figsize=(4.41, 3.41))
        ax = fig.add_subplot(111)
        ax.set_title(self.tr("Histogram"), fontweight="bold")
        ax.grid(True)
        self._draw_canvas(fig)

    def create_histogram(self):
        try:
            self._set_progress(0)

            raster_id = self.dlg.cmb_raster_load.currentData()
            layer = QgsProject.instance().mapLayer(raster_id)
            if not layer:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No raster selected."))
                return

            band_index = self.dlg.cmb_field.currentData()
            if band_index is None:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No band selected."))
                return

            provider = layer.dataProvider()
            stats = provider.bandStatistics(band_index, QgsRasterBandStats.All)
            min_val, max_val = stats.minimumValue, stats.maximumValue

            self.min_val = min_val
            self.max_val = max_val

            rows = layer.height()
            cols = layer.width()
            total_cells = rows * cols

            if total_cells < 20_000_000:
                ds_factor = 1
            elif total_cells < 100_000_000:
                ds_factor = 4
            elif total_cells < 200_000_000:
                ds_factor = 10
            else:
                QMessageBox.information(
                    self.dlg,
                    self.tr("Large raster"),
                    self.tr("The raster is extremely large. The histogram will use the CURRENT VIEW.")
                )
                ds_factor = None

            src = gdal.Open(provider.dataSourceUri())
            band = src.GetRasterBand(band_index)

            if ds_factor is None:
                canvas = self.dlg.iface.mapCanvas()
                rect = canvas.extent()

                gt = src.GetGeoTransform()
                inv_gt = gdal.InvGeoTransform(gt)

                px_min, py_min = gdal.ApplyGeoTransform(inv_gt, rect.xMinimum(), rect.yMaximum())
                px_max, py_max = gdal.ApplyGeoTransform(inv_gt, rect.xMaximum(), rect.yMinimum())

                px_min, py_min = int(px_min), int(py_min)
                px_max, py_max = int(px_max), int(py_max)

                width = px_max - px_min
                height = py_max - py_min

                if width <= 0 or height <= 0:
                    QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("Invalid current view extent."))
                    return

                raster_data = band.ReadAsArray(px_min, py_min, width, height).astype(float)

            else:
                raster_data = band.ReadAsArray().astype(float)
                if ds_factor > 1:
                    QMessageBox.information(
                        self.dlg,
                        self.tr("Downsampling"),
                        self.tr(f"Histogram computed using 1/{ds_factor} of the raster.")
                    )
                    raster_data = raster_data[::ds_factor, ::ds_factor]

            self._set_progress(10)

            nodata = band.GetNoDataValue()
            if nodata is None:
                nodata = provider.sourceNoDataValue(band_index)

            masked = np.ma.masked_equal(raster_data, nodata)
            data = masked.compressed()

            self.dlg.lineEdit_count.setText(str(data.size))
            self.dlg.lineEdit_min.setText(f"{min_val:.2f}")
            self.dlg.lineEdit_max.setText(f"{max_val:.2f}")
            self.dlg.lineEdit_mean.setText(f"{stats.mean:.2f}")
            self.dlg.lineEdit_std.setText(f"{stats.stdDev:.2f}")

            num_classes = self.dlg.spinBox_classes.value()
            method = self.dlg.cmb_method.currentIndex()

            self.enable_user_clicks = (method == 4)
            self.user_clicks = []

            task = ReclassifierTask(
                "Reclassification",
                data,
                min_val,
                max_val,
                stats,
                num_classes,
                method,
                hist_color=self._qcolor_to_mpl(self.hist_color),
                line_color=self._qcolor_to_mpl(self.line_color)
            )

            task.progressChanged.connect(self._set_progress)

            def finished():
                breaks = task.breaks
                fig = task.fig

                # Salva la figura per usi successivi (linee da tabella)
                self.figure = fig

                classes = task.num_classes
                self.dlg.tableWidget_value.setRowCount(classes)

                for i in range(classes):

                    if method == 4:
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

                self._draw_canvas(fig)
                self._set_progress(100)
                self._set_progress(0)

            task.taskCompleted.connect(finished)
            task.taskTerminated.connect(lambda: QMessageBox.critical(self.dlg, self.tr("Error"), self.tr("Task failed.")))

            QgsApplication.taskManager().addTask(task)

        except Exception as e:
            QMessageBox.critical(self.dlg, self.tr("Error"), str(e))

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------
    def select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self.dlg, self.tr("Select output raster"), "", "GeoTIFF (*.tif)"
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
            self.dlg, self.tr("Import table"), "", "CSV (*.csv);;Text (*.txt)"
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
            QMessageBox.warning(self.dlg, self.tr("Warning"), self.tr("No row selected."))
            return

        table.removeRow(selected)

    def save_table(self):
        path, _ = QFileDialog.getSaveFileName(
            self.dlg, self.tr("Save table"), "", "CSV (*.csv);;Text (*.txt)"
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
            QMessageBox.warning(self.dlg, self.tr("Empty"), self.tr("No graph to save."))
            return

        self._set_progress(0)

        path, _ = QFileDialog.getSaveFileName(
            self.dlg, self.tr("Save graph"), "", "PNG (*.png);;JPG (*.jpg)"
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
        # Valori numerici azzerati
        self.dlg.lineEdit_count.setText("0")
        self.dlg.lineEdit_min.setText("0.00")
        self.dlg.lineEdit_max.setText("0.00")
        self.dlg.lineEdit_mean.setText("0.00")
        self.dlg.lineEdit_std.setText("0.00")

        # Output vuoto
        self.dlg.lineEdit_output.clear()

        # Tabella svuotata
        self.dlg.tableWidget_value.clearContents()
        self.dlg.tableWidget_value.setRowCount(0)

        # Istogramma vuoto
        self.create_empty_histogram()

        # Progress bar a zero
        self._set_progress(0)

    # ----------------------------------------------------------
    # RICLASSIFICAZIONE RASTER
    # ----------------------------------------------------------
    def run_reclassification(self):
        try:
            self._set_progress(0)

            raster_id = self.dlg.cmb_raster_load.currentData()
            layer = QgsProject.instance().mapLayer(raster_id)

            self._set_progress(10)

            if not layer:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No raster selected."))
                self._set_progress(0)
                return

            band_index = self.dlg.cmb_field.currentData()
            if band_index is None:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No band selected."))
                self._set_progress(0)
                return

            out_path = self.dlg.lineEdit_output.text().strip()
            if not out_path:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No output path selected."))
                self._set_progress(0)
                return

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

                if decimal_symbol == ",":
                    start = start.replace(",", ".")
                    end = end.replace(",", ".")
                    new = new.replace(",", ".")

                try:
                    start = float(start)
                    end = float(end)
                    new = float(new)
                except ValueError:
                    QMessageBox.critical(
                        self.dlg,
                        self.tr("Error"),
                        self.tr(f"Invalid numeric value in row {r+1}.")
                    )
                    self._set_progress(0)
                    return

                if start >= end:
                    QMessageBox.critical(
                        self.dlg,
                        self.tr("Error"),
                        self.tr(f"Start value must be < end value in row {r+1}.")
                    )
                    self._set_progress(0)
                    return

                rules.append((start, end, new))


            if not rules:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No valid reclassification rules."))
                return

            self._set_progress(50)

            src = gdal.Open(layer.dataProvider().dataSourceUri())
            band = src.GetRasterBand(band_index)
            arr = band.ReadAsArray().astype(float)

            nodata = band.GetNoDataValue()
            if nodata is None:
                nodata = -9999

            self._set_progress(60)

            out_arr = np.full(arr.shape, nodata, dtype=float)

            for start, end, new in rules:
                mask = (arr >= start) & (arr < end)
                out_arr[mask] = new

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

            out_ds = None

            if self.dlg.checkBox_load_prg.isChecked():
                layer_name = os.path.splitext(os.path.basename(out_path))[0]
                new_layer = QgsRasterLayer(out_path, layer_name)
                if new_layer.isValid():
                    QgsProject.instance().addMapLayer(new_layer)

            self._set_progress(100)
            QMessageBox.information(self.dlg, self.tr("Done"), self.tr("Raster reclassification completed."))
            self._set_progress(0)

        except Exception as e:
            QMessageBox.critical(self.dlg, self.tr("Error"), self.tr(f"Reclassification failed:\n{e}"))

    # ----------------------------------------------------------
    # UTILITY
    # ----------------------------------------------------------
    def _draw_canvas(self, fig):
        self.canvas = FigureCanvas(fig)

        # collega il click
        self.canvas.mpl_connect("button_press_event", self._on_click)

        scene = QGraphicsScene()
        scene.addWidget(self.canvas)
        self.dlg.graphicsView_hystogram.setScene(scene)
        self.canvas.draw()

    def _set_progress(self, value):
        try:
            self.dlg.progressBar.setValue(value)
        except:
            pass

    # ----------------------------------------------------------
    # REFRESH GRAPH
    # ----------------------------------------------------------
    def draw_lines_from_table(self):
        if self.canvas is None:
            QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No histogram available."))
            return

        table = self.dlg.tableWidget_value
        rows = table.rowCount()
        if rows == 0:
            QMessageBox.warning(self.dlg, self.tr("Error"), self.tr("No rows in the table."))
            return

        # Colore di fallback
        color = self.line_color if self.line_color else "red"

        boundaries = []
        decimal_symbol = self.dlg.comboBox_decimals.currentText()

        for r in range(rows):
            start_item = table.item(r, 0)
            end_item = table.item(r, 1)

            if not start_item or not end_item:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr(f"Missing values in row {r+1}."))
                return

            start_txt = start_item.text().strip()
            end_txt = end_item.text().strip()

            if not start_txt or not end_txt:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr(f"Empty values in row {r+1}."))
                return

            if decimal_symbol == ",":
                start_txt = start_txt.replace(",", ".")
                end_txt = end_txt.replace(",", ".")

            try:
                start_val = float(start_txt)
                end_val = float(end_txt)
            except ValueError:
                QMessageBox.warning(self.dlg, self.tr("Error"), self.tr(f"Invalid numeric values in row {r+1}."))
                return

            boundaries.append(start_val)
            boundaries.append(end_val)

        # Rimuovi linee precedenti
        if hasattr(self, "_interval_lines"):
            for ln in self._interval_lines:
                try:
                    ln.remove()
                except:
                    pass
        self._interval_lines = []

       # Determina il colore delle linee
        if isinstance(self.line_color, tuple):
            color = self.line_color
        elif self.line_color:
            try:
                color = self._qcolor_to_mpl(self.line_color)
            except:
                color = (1, 0, 0)  # fallback rosso
        else:
            color = (1, 0, 0)  # fallback rosso

        # Disegna linee ordinate e uniche
        ax = self.canvas.figure.axes[0]

        for b in sorted(set(boundaries)):
            line = ax.axvline(b, color=color, linestyle="--", linewidth=1)
            self._interval_lines.append(line)

        self.canvas.draw()

    # ----------------------------------------------------------
    # CLICK USER
    # ----------------------------------------------------------
    def _on_click(self, event):
        if not self.enable_user_clicks:
            return

        if event.xdata is None:
            return

        x = float(event.xdata)

        table = self.dlg.tableWidget_value
        n = table.rowCount()
        row = table.currentRow()
        if row < 0:
            return

        decimal_symbol = self.dlg.comboBox_decimals.currentText()

        def _to_float(txt):
            txt = txt.strip()
            if decimal_symbol == ",":
                txt = txt.replace(",", ".")
            return float(txt)

        # ----------------------------------------------------------
        # RIGA 1 (indice 0): xmin → Xsel
        # ----------------------------------------------------------
        if row == 0:
            start_val = self.min_val
            end_val = x

            table.setItem(0, 0, QTableWidgetItem(f"{start_val:.2f}"))
            table.setItem(0, 1, QTableWidgetItem(f"{end_val:.2f}"))

        # ----------------------------------------------------------
        # RIGHE 2…PENULTIMA: x_prec → Xsel
        # ----------------------------------------------------------
        elif 1 <= row <= n - 2:
            prev_item = table.item(row - 1, 1)
            if not prev_item or not prev_item.text().strip():
                QMessageBox.warning(
                    self.dlg,
                    self.tr("Error"),
                    self.tr(f"Fill row {row} before row {row + 1}.")
                )
                return

            start_val = _to_float(prev_item.text())
            end_val = x

            table.setItem(row, 0, QTableWidgetItem(f"{start_val:.2f}"))
            table.setItem(row, 1, QTableWidgetItem(f"{end_val:.2f}"))

            # Se è la penultima riga → compila anche l’ultima
            if row == n - 2:
                last_start = end_val
                last_end = self.max_val

                table.setItem(n - 1, 0, QTableWidgetItem(f"{last_start:.2f}"))
                table.setItem(n - 1, 1, QTableWidgetItem(f"{last_end:.2f}"))

        # ----------------------------------------------------------
        # RIGA FINALE (indice n-1): x_prec → xmax
        # ----------------------------------------------------------
        elif row == n - 1:
            prev_item = table.item(n - 2, 1)
            if not prev_item or not prev_item.text().strip():
                QMessageBox.warning(
                    self.dlg,
                    self.tr("Error"),
                    self.tr("Fill the previous row before the last one.")
                )
                return

            start_val = _to_float(prev_item.text())
            end_val = self.max_val

            table.setItem(row, 0, QTableWidgetItem(f"{start_val:.2f}"))
            table.setItem(row, 1, QTableWidgetItem(f"{end_val:.2f}"))

        # ----------------------------------------------------------
        # DISEGNO LINEE VERTICALI
        # ----------------------------------------------------------

        # Colore sicuro
        if isinstance(self.line_color, tuple):
            color = self.line_color
        elif self.line_color:
            try:
                color = self._qcolor_to_mpl(self.line_color)
            except Exception:
                color = (1, 0, 0)
        else:
            color = (1, 0, 0)

        ax = self.canvas.figure.axes[0]

        # --- 1) Rimuovi la linea Xsel precedente per questa riga ---
        if row in self._row_lines:
            try:
                self._row_lines[row].remove()
            except Exception:
                pass

        # --- 2) Disegna la nuova linea Xsel ---
        new_line = ax.axvline(x, color=color, linestyle="--", linewidth=1)
        self._row_lines[row] = new_line

        # --- 3) Gestione linea fissa (xmin o xmax) ---
        # Prima riga → xmin
        if row == 0:
            fixed_x = self.min_val

        # Penultima riga → xmax
        elif row == n - 2:
            fixed_x = self.max_val

        else:
            fixed_x = None

        if fixed_x is not None:
            # rimuovi eventuale linea fissa precedente
            if row in self._fixed_lines:
                try:
                    self._fixed_lines[row].remove()
                except Exception:
                    pass

            # disegna la nuova linea fissa
            fixed_line = ax.axvline(fixed_x, color=color, linestyle="--", linewidth=1)
            self._fixed_lines[row] = fixed_line

        self.canvas.draw()
