from qgis.core import QgsMapLayer, QgsLayerTreeGroup, Qgis

from .constants import lens_auto_refresh_interval_time


def is_in_group(layer: QgsMapLayer, layer_group: QgsLayerTreeGroup) -> bool:
    """Return True if a target layer is in a target layer groyp"""
    for child in layer_group.children():
        if child.layerId() == layer.id():  # 0 = Layer node
            return True
    return False


def make_dynamic(layer: QgsMapLayer) -> None:
    layer.setAutoRefreshEnabled(True)
    layer.setAutoRefreshInterval(lens_auto_refresh_interval_time)
    layer.setAutoRefreshMode(Qgis.AutoRefreshMode.ReloadData)
