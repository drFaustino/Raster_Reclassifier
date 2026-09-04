# -*- coding: utf-8 -*-

import os
from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from .gui.dialog import RasterReclassifierDialog


class RasterReclassifier:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr("&Raster Reclassifier")
        self.first_start = True

        locale = QSettings().value("locale/userLocale")[0:2]
        qm_path = os.path.join(self.plugin_dir, "resources", "i18n", f"raster_reclassifier_{locale}.qm")

        if os.path.exists(qm_path):
            self.translator = QTranslator()
            self.translator.load(qm_path)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate("RasterReclassifier", message)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        action = QAction(QIcon(icon_path), self.tr("Raster Reclassifier"), self.iface.mainWindow())
        action.triggered.connect(self.run)

        self.iface.addToolBarIcon(action)
        self.iface.addPluginToRasterMenu(self.menu, action)
        self.actions.append(action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginRasterMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        try:
            if self.first_start:
                self.first_start = False
                self.dlg = RasterReclassifierDialog(self.iface)

            self.dlg.prepare()
            self.dlg.show()
            self.dlg.exec()

        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), self.tr("Error"), str(e))
