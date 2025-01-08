# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RasterReclassifier
                                 A QGIS plugin
 Reclassification of the raster layer using a table to assign new values. It is also possible to display a histogram of the classes according to the minimum and maximum values ​​of the reference band.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-01-03
        copyright            : (C) 2025 by Dr. Geol. Faustino Cetraro
        email                : geol-faustino@libero.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RasterReclassifier class from file RasterReclassifier.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .raster_reclassifier import RasterReclassifier
    return RasterReclassifier(iface)