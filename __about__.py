#! python3
# -*- coding: utf-8 -*-

"""
Centralized metadata loader for the QGIS plugin.
Reads metadata.txt and exposes clean Python variables.
"""

from configparser import ConfigParser
from datetime import date
from pathlib import Path


__all__ = [
    "__author__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
    "__version_info__",
    "__icon_path__",
    "__plugin_dependencies__",
]


# ----------------------------------------------------------------------
# Percorsi
# ----------------------------------------------------------------------

DIR_PLUGIN_ROOT = Path(__file__).parent
PLG_METADATA_FILE = DIR_PLUGIN_ROOT / "metadata.txt"


# ----------------------------------------------------------------------
# Funzioni
# ----------------------------------------------------------------------

def plugin_metadata_as_dict() -> dict:
    """
    Legge metadata.txt e restituisce un dizionario strutturato.

    Returns:
        dict: {section: {key: value}}
    """
    if not PLG_METADATA_FILE.is_file():
        raise IOError(f"metadata.txt not found at: {PLG_METADATA_FILE}")

    config = ConfigParser(interpolation=None)
    config.read(PLG_METADATA_FILE, encoding="UTF-8")

    return {section: dict(config.items(section)) for section in config.sections()}


# ----------------------------------------------------------------------
# Caricamento metadata
# ----------------------------------------------------------------------

_md = plugin_metadata_as_dict()
_general = _md.get("general", {})


# ----------------------------------------------------------------------
# Variabili pubbliche
# ----------------------------------------------------------------------

__title__ = _general.get("name", "Unknown Plugin")
__author__ = _general.get("author", "Unknown Author")
__email__ = _general.get("email", "")
__license__ = "GPLv3"

__icon_path__ = DIR_PLUGIN_ROOT / _general.get("icon", "")

__uri__ = _general.get("repository", "")
__uri_homepage__ = _general.get("homepage", "")
__uri_repository__ = _general.get("repository", "")
__uri_tracker__ = _general.get("tracker", "")

__version__ = _general.get("version", "0.0.0")

# Version tuple (major, minor, patch)
__version_info__ = tuple(
    int(part) if part.isdigit() else part
    for part in __version__.replace("-", ".", 1).split(".")
)

# Plugin dependencies
__plugin_dependencies__ = [
    dep.strip()
    for dep in _general.get("plugin_dependencies", "").split(",")
    if dep.strip()
]

# Summary (description + about)
__summary__ = "{}\n{}".format(
    _general.get("description", "").strip(),
    _general.get("about", "").strip(),
)


# ----------------------------------------------------------------------
# Debug / test
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Plugin: {__title__}")
    print(f"Author: {__author__}")
    print(f"Email: {__email__}")
    print(f"Version: {__version__}")
    print(f"Summary:\n{__summary__}")
    print(f"Icon: {__icon_path__}")
    print(f"Homepage: {__uri_homepage__}")
    print(f"Repository: {__uri_repository__}")
    print(f"Tracker: {__uri_tracker__}")
    print(f"Dependencies: {__plugin_dependencies__}")
