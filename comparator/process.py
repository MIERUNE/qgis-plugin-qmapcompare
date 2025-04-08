from qgis.core import (
    Qgis,
    QgsCoordinateTransformContext,
    QgsFillSymbol,
    QgsGeometryGeneratorSymbolLayer,
    QgsGroupLayer,
    QgsInvertedPolygonRenderer,
    QgsLayerTreeGroup,
    QgsMapLayer,
    QgsMapThemeCollection,
    QgsProject,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QT_VERSION_STR
from qgis.PyQt.QtGui import QAction, QPainter
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.utils import iface

from .constants import (
    compare_background_geometry,
    compare_background_layer_name,
    compare_group_name,
    compare_mask_layer_name,
    horizontal_split_geometry,
    lens_geometry,
    mirror_maptheme_name,
    mirror_widget_name,
    vertical_split_geometry,
)
from .utils import (
    get_map_dockwidgets,
    get_right_dockwidgets,
    get_visible_layers,
    is_in_group,
    make_dynamic,
    set_panel_width,
    toggle_layers,
)

QT_VERSION_INT = int(QT_VERSION_STR.split(".")[0])

if QT_VERSION_INT <= 5:
    dock_widget_floatable = QDockWidget.DockWidgetFloatable
    dock_widget_movable = QDockWidget.DockWidgetMovable
    composition_mode_destination_in = QPainter.CompositionMode_DestinationIn
else:
    dock_widget_floatable = QDockWidget.DockWidgetFeature.DockWidgetFloatable
    dock_widget_movable = QDockWidget.DockWidgetFeature.DockWidgetMovable
    composition_mode_destination_in = (
        QPainter.CompositionMode.CompositionMode_DestinationIn
    )

# Syncronize flag to avoid recursive map sync and crash
map_synchronizing = False


def compare_with_mask(compare_layers: list, compare_method: str) -> None:
    """
    Make QGIS Map to be in compare mode with mask layer group method
    with input compare layers
    input:
    - compare layers (a list of QgsMapLayer)
    - compare_method: 'vertical' 'horizontal' or 'lens'
    """
    project = QgsProject.instance()

    compare_layer_group, compare_mask_layer = _create_compare_layer_group_and_mask(
        compare_method
    )

    # reinitialize compare_layer_group
    # remove layers except mask one
    for child in list(compare_layer_group.children()):
        if child.name() == compare_mask_layer_name:
            continue
        compare_layer_group.removeChildNode(child)

    # Add target compare layers to layer group
    for layer in compare_layers:
        # Add layer to compare group if not existing
        if not is_in_group(layer, compare_layer_group):
            compare_layer_group.addLayer(layer)

    # Add white polygon layer for background
    background_layer = QgsVectorLayer(
        "Polygon?crs=EPSG:3857", compare_background_layer_name, "memory"
    )
    project.addMapLayer(background_layer, False)
    compare_layer_group.addLayer(background_layer)
    # symbolize with rectangle of map extent (geometry generator)
    background_geometry_generator = QgsGeometryGeneratorSymbolLayer.create(
        {
            "geometryModifier": compare_background_geometry,
            "geometry_type": 2,  # Polygon
            "extent": "",
            "color": "white",
            "outline_style": "no",
        }
    )
    background_layer_symbol = QgsFillSymbol.createSimple({})
    background_layer_symbol.changeSymbolLayer(0, background_geometry_generator)
    background_renderer = QgsInvertedPolygonRenderer(
        QgsSingleSymbolRenderer(background_layer_symbol)
    )
    background_layer.setRenderer(background_renderer)
    background_layer.triggerRepaint()

    # Symbolize mask layer with geometry generator
    # Orientation Fallback is vertical
    geometry_formula = vertical_split_geometry
    if compare_method == "horizontal":
        geometry_formula = horizontal_split_geometry
    if compare_method == "lens":
        geometry_formula = lens_geometry

    geometry_generator = QgsGeometryGeneratorSymbolLayer.create(
        {
            "geometryModifier": geometry_formula,
            "geometry_type": 2,  # Polygon
            "extent": "",
            "color": "white",
            "outline_style": "no",
        }
    )

    symbol = QgsFillSymbol.createSimple({})
    symbol.changeSymbolLayer(0, geometry_generator)

    #  Create the inverted polygon renderer
    inverted_renderer = QgsInvertedPolygonRenderer(QgsSingleSymbolRenderer(symbol))
    compare_mask_layer.setRenderer(inverted_renderer)

    # Change mask layer blend mode to fit with 'Invert Mask Below'
    compare_mask_layer.setBlendMode(composition_mode_destination_in)

    # update compare mask layer rendering
    compare_mask_layer.triggerRepaint()

    # Duplicate Mask layer in case of project CRS NOT in meter units to avoid square rendering
    if project.crs().mapUnits() != QgsUnitTypes.DistanceMeters:
        duplicate_mask_layer = compare_mask_layer.clone()
        duplicate_mask_layer.setName(compare_mask_layer.name() + "_geographic")
        project.addMapLayer(duplicate_mask_layer, False)
        compare_layer_group.insertLayer(0, duplicate_mask_layer)

    return


def _create_compare_layer_group_and_mask(
    compare_method: str,
) -> tuple[QgsLayerTreeGroup, QgsMapLayer]:
    """Create layer group with mask layer inside at the top
    of layer tree return layer_group and compare_mask_layer
    Input:
    - compare_method: 'vertical' 'horizontal' or 'lens'
    Output:
    - layer_group_node: Compare Layer Group,
    - mask_layer: Compare mask layer
    """

    project = QgsProject.instance()
    root = project.layerTreeRoot()

    # Create a scratch polygon layer
    mask_layers = project.mapLayersByName(compare_mask_layer_name)
    if mask_layers:
        mask_layer = mask_layers[0]
        # Make mask dynamic for lens
        if compare_method == "lens":
            make_dynamic(mask_layer)
        else:
            mask_layer.setAutoRefreshMode(Qgis.AutoRefreshMode.Disabled)
    else:
        mask_layer = QgsVectorLayer(
            f"Polygon?crs={project.crs().authid()}", compare_mask_layer_name, "memory"
        )
        if not mask_layer.isValid():
            print("Failed to create the scratch layer")
        else:
            # Make mask dynamic for lens
            if compare_method == "lens":
                make_dynamic(mask_layer)
            else:
                mask_layer.setAutoRefreshMode(Qgis.AutoRefreshMode.Disabled)
            # Add polygon layer to compare layer group
            project.addMapLayer(mask_layer, False)

    # if not exists, create compare layer group to the top of layer tree
    layer_group_node = root.findGroup(compare_group_name)

    if not layer_group_node:
        # layer group creation with layer rendering as group option
        options = QgsGroupLayer.LayerOptions(QgsCoordinateTransformContext())
        group_layer = QgsGroupLayer("group", options)
        group_layer.setChildLayers([mask_layer])

        project.addMapLayer(group_layer, False)
        layer_group_node = QgsLayerTreeGroup(compare_group_name)
        layer_group_node.setGroupLayer(group_layer)

        layer_group_node.addLayer(mask_layer)
        root.insertChildNode(0, layer_group_node)

    return layer_group_node, mask_layer


def compare_with_mapview(compare_layers: list) -> None:
    """
    Add an additional mapview to be compare with map main canvas
    with input compare layers
    input:
    - compare layers (a list of QgsMapLayer)
    """
    main_window = iface.mainWindow()
    origin_visible_layers = get_visible_layers()

    map_widgets = get_map_dockwidgets()

    # Detect if Mirror map exists.
    mirror_exists = False
    for dock in main_window.findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas) and dock.windowTitle() == mirror_widget_name:
            mirror_exists = True

    # Set visible layers to compare one to create theme
    toggle_layers(compare_layers)

    # Add map widget
    if not mirror_exists:
        main_window.findChild(QAction, "mActionNewMapCanvas").trigger()

    map_widgets = get_map_dockwidgets()
    mirror_widget = map_widgets[0]

    # Configure Mirror Dock Widget window
    mirror_dock_widget = mirror_widget.parent().parent().parent()
    mirror_dock_widget.setWindowTitle(mirror_widget_name)

    # Don't show close button feature to avoid bug when closing mirror window
    mirror_dock_widget.setFeatures(dock_widget_floatable | dock_widget_movable)

    # Tabify right panels layouts Tabify with other Docks in right side
    right_dock_widgets = get_right_dockwidgets()

    # Calculate size of tabified docks to be half of window
    if len(right_dock_widgets) > 0:
        max_width = max(dw.geometry().width() for dw in right_dock_widgets)
    else:
        max_width = 0
    compare_map_size = int((iface.mapCanvas().size().width() + max_width) / 2)

    # Do only if there are more than 1 dock widget (1 is mirror compare map panel)
    if len(right_dock_widgets) > 1:
        base_dock = right_dock_widgets[0]  # the one to tabify the others onto
        for i in range(1, len(right_dock_widgets)):
            if right_dock_widgets[i].windowTitle() == mirror_widget_name:
                mirror_dock_widget = right_dock_widgets[i]
                set_panel_width(mirror_dock_widget, compare_map_size)
            else:
                main_window.tabifyDockWidget(base_dock, right_dock_widgets[i])

        # add mirror map at last to be active
        if mirror_dock_widget:
            main_window.tabifyDockWidget(base_dock, mirror_dock_widget)

    elif len(right_dock_widgets) == 1:
        # Case of if there is no other panel in right side
        set_panel_width(right_dock_widgets[0], int(compare_map_size))
        mirror_widget.refresh()

    # Add Map themes
    mapThemesCollection = QgsProject.instance().mapThemeCollection()
    mapThemeRecord = QgsMapThemeCollection.createThemeFromCurrentState(
        QgsProject.instance().layerTreeRoot(), iface.layerTreeView().layerTreeModel()
    )
    mapThemesCollection.insert(mirror_maptheme_name, mapThemeRecord)
    mirror_widget.setTheme(mirror_maptheme_name)

    # Initialize map extent
    mirror_widget.setCenter(iface.mapCanvas().center())
    mirror_widget.zoomScale(iface.mapCanvas().scale())

    # Retrieve origin layer display
    toggle_layers(origin_visible_layers)

    # synchronize main map extent and scale TO mirror
    iface.mapCanvas().extentsChanged.connect(_sync_mirror_extent_from_main_map)
    iface.mapCanvas().scaleChanged.connect(_sync_mirror_extent_from_main_map)
    # synchronize main map extent and scale FROM mirror
    mirror_widget.extentsChanged.connect(_sync_main_map_extent_from_mirror)
    mirror_widget.scaleChanged.connect(_sync_main_map_extent_from_mirror)

    return


def _sync_mirror_extent_from_main_map() -> None:
    # Don't process if map synchronizing is already running
    global map_synchronizing
    if map_synchronizing:
        return

    # Flag map synchronizing running to avoid invert signal and crash
    map_synchronizing = True
    for dock in iface.mainWindow().findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas) and dock.windowTitle() == mirror_widget_name:
            mirror_mapview = dock.findChild(QgsMapCanvas)

            if mirror_mapview:
                mirror_mapview.zoomScale(iface.mapCanvas().scale())
                mirror_mapview.setCenter(iface.mapCanvas().center())
                mirror_mapview.refresh()
    map_synchronizing = False


def _sync_main_map_extent_from_mirror() -> None:
    # Don't process if map synchronizing is already running
    global map_synchronizing
    if map_synchronizing:
        return

    # Flag map synchronizing running to avoid invert signal and crash
    map_synchronizing = True
    for dock in iface.mainWindow().findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas) and dock.windowTitle() == mirror_widget_name:
            mirror_mapview = dock.findChild(QgsMapCanvas)

            if mirror_mapview:
                iface.mapCanvas().zoomScale(mirror_mapview.scale())
                iface.mapCanvas().setCenter(mirror_mapview.center())
                iface.mapCanvas().refresh()
    map_synchronizing = False


def stop_compare_with_mask() -> None:
    """Stop comparing by removing Comparing layer group"""
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    layer_group_node = root.findGroup(compare_group_name)
    if layer_group_node:
        root.removeChildNode(layer_group_node)

    return


def stop_mirror_compare() -> None:
    """Stop comparing mirror mode by removing Mirror compare panel"""

    for dock in iface.mainWindow().findChildren(QDockWidget):
        if dock.findChild(QgsMapCanvas) and dock.windowTitle() == mirror_widget_name:
            # disconnect map sync
            iface.mapCanvas().extentsChanged.disconnect(
                _sync_mirror_extent_from_main_map
            )
            iface.mapCanvas().scaleChanged.disconnect(_sync_mirror_extent_from_main_map)

            mirror_mapview = dock.findChild(QgsMapCanvas)
            mirror_mapview.extentsChanged.disconnect(_sync_main_map_extent_from_mirror)
            mirror_mapview.scaleChanged.disconnect(_sync_main_map_extent_from_mirror)

            dock.close()

    return
