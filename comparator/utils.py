from qgis.core import (
    Qgis,
    QgsMapLayer,
    QgsLayerTreeGroup,
    QgsProject,
    QgsLayerTreeLayer,
)

from qgis.gui import QgsMapCanvas

from qgis.PyQt.QtWidgets import QDockWidget
from qgis.utils import iface

from .constants import lens_auto_refresh_interval_time


def is_in_group(layer: QgsMapLayer, layer_group: QgsLayerTreeGroup) -> bool:
    """
    Return True if a target layer is in a target layer group
    """
    for child in layer_group.children():
        if child.layerId() == layer.id():  # 0 = Layer node
            return True
    return False


def make_dynamic(layer: QgsMapLayer) -> None:
    """
    make layer dynamic by refreshing with interval
    interval is set with lens_auto_refresh_interval_time in ms
    """
    layer.setAutoRefreshEnabled(True)
    layer.setAutoRefreshInterval(lens_auto_refresh_interval_time)
    layer.setAutoRefreshMode(Qgis.AutoRefreshMode.ReloadData)


def get_visible_layers(node=None) -> list:
    """
    Recursively gather all layers that are marked as visible
    under the given layer tree node (defaults to project root).
    Returns a list of QgsMapLayer objects.
    """
    if node is None:
        node = QgsProject.instance().layerTreeRoot()

    visible_layers = []

    for child in node.children():
        if isinstance(child, QgsLayerTreeGroup):
            # Recurse into sub-groups
            visible_layers.extend(get_visible_layers(child))
        elif isinstance(child, QgsLayerTreeLayer):
            # If the layer node is visible in the layer tree
            if child.isVisible():
                visible_layers.append(child.layer())

    return visible_layers


def toggle_layers(layers_to_display: list) -> None:
    """
    Make visible only a list a layer set as input
    """
    root = QgsProject.instance().layerTreeRoot()
    layer_to_display_ids = [layer.id() for layer in layers_to_display]

    for child in root.children():
        if isinstance(child, QgsLayerTreeLayer):
            if child.layerId() in layer_to_display_ids:
                child.setItemVisibilityChecked(True)
            else:
                child.setItemVisibilityChecked(False)

                
def get_map_dockwidgets() -> list:
    """ """
    main_window = iface.mainWindow()
    map_widgets = []
    for dock in main_window.findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas):
            map_widgets.append(dock.findChild(QgsMapCanvas))
    return map_widgets
