from qgis.core import (
    Qgis,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsMapLayer,
    QgsProject,
)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QT_VERSION_STR, Qt
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.utils import iface

from .constants import lens_auto_refresh_interval_time

QT_VERSION_INT = int(QT_VERSION_STR.split(".")[0])

if QT_VERSION_INT <= 5:
    right_dock_widget_area = Qt.RightDockWidgetArea
else:
    right_dock_widget_area = Qt.DockWidgetArea.RightDockWidgetArea


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
    """Get all dockwidgets containing a map canvas"""
    main_window = iface.mainWindow()
    map_widgets = []
    for dock in main_window.findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas):
            map_widgets.append(dock.findChild(QgsMapCanvas))
    return map_widgets


def get_right_dockwidgets() -> list:
    """Get visible dockwidgets located in right side of QGIS window"""
    main_window = iface.mainWindow()

    right_dock_widgets = []
    for dock in main_window.findChildren(QDockWidget):
        # Check which side (dock area) the widget is in
        dock_area = main_window.dockWidgetArea(dock)
        if dock_area == right_dock_widget_area and dock.isVisible():
            right_dock_widgets.append(dock)

    return right_dock_widgets


def set_panel_width(widget: QDockWidget, size: int) -> None:
    """Set panel width, and allow afterhand size edit"""
    widget.setFixedWidth(size)

    # Remove fix width to allow width to be editable
    widget.setMinimumWidth(100)
    widget.setMaximumWidth(10000)

    return
