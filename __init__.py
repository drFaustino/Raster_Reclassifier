#! python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# Raster Reclassifier – QGIS Plugin
# ----------------------------------------------------------
# Licensed under the terms of GNU GPL v2 or (at your option) any later version.
# ----------------------------------------------------------

def classFactory(iface):
    from .raster_reclassifier import RasterReclassifier
    return RasterReclassifier(iface)
