# -*- coding: utf-8 -*-

import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QColorDialog
from qgis.PyQt.QtCore import Qt

from ..core.reclassifier_engine import ReclassifierEngine


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "raster_reclassifier_dialog_base.ui")
)


class RasterReclassifierDialog(QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.engine = ReclassifierEngine(self)
        self._connect_signals()

    def prepare(self):
        self.engine.populate_raster_list()
        self.engine.populate_bands()
        self.engine.create_empty_histogram()

        # Popola delimitatori
        self.comboBox_col_delim.clear()
        self.comboBox_col_delim.addItems([";", "T"])

        # Popola simboli decimali
        self.comboBox_decimals.clear()
        self.comboBox_decimals.addItems([".", ","])

    def _connect_signals(self):
        self.cmb_raster_load.currentIndexChanged.connect(self.engine.populate_bands)

        self.pushButton_colore_histogram.clicked.connect(self._change_hist_color)
        self.pushButton_colore_class.clicked.connect(self._change_class_color)

        self.pushButton_extract.clicked.connect(self.engine.create_histogram)
        self.pushButton_save_raster.clicked.connect(self.engine.select_output_file)

        self.pushButton_import.clicked.connect(self.engine.import_values)
        self.pushButton_new.clicked.connect(self.engine.add_new_row)
        self.pushButton_del.clicked.connect(self.engine.delete_selected_row)

        self.pushButton_run.clicked.connect(self.engine.run_reclassification)
        self.pushButton_cancel.clicked.connect(self.engine.reset)

        self.pushButton_save_table.clicked.connect(self.engine.save_table)
        self.pushButton_graph.clicked.connect(self.engine.save_graph)

        self.pushButton_close.clicked.connect(self.close)

    def _change_hist_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.label_10.setStyleSheet(f"background-color: {color.name()};")

    def _change_class_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.label_12.setStyleSheet(f"background-color: {color.name()};")
