from qgis.core import (
    QgsProject,
    QgsLayerTreeGroup,
    QgsVectorLayer,
    QgsGeometryGeneratorSymbolLayer,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsInvertedPolygonRenderer,
)
from qgis.PyQt.QtGui import QPainter


def compare_split(compare_layers):
    compare_layer_group, compare_mask_layer = _create_compare_layer_group_and_mask()

    # move target compare layers to layer group
    for layer in compare_layers:
        compare_layer_group.addLayer(layer)
    compare_layer_group.setCustomProperty("renderLayersAsGroup", True)

    # Symbolize with geometry generator
    formula = """make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_height / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_height / 2)),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0)"""

    geometry_generator = QgsGeometryGeneratorSymbolLayer.create(
        {
            "geometryModifier": formula,
            "geometry_type": 2,  # Polygon
            "extent": "",  # Use the default map extent
        }
    )

    symbol = QgsFillSymbol.createSimple(
        {"color": "255,0,0,50"}
    )  # Red fill with transparency
    symbol.changeSymbolLayer(0, geometry_generator)

    #  Create the inverted polygon renderer
    inverted_renderer = QgsInvertedPolygonRenderer(QgsSingleSymbolRenderer(symbol))
    compare_mask_layer.setRenderer(inverted_renderer)

    # compare_mask_layer.renderer().setSymbol(symbol)

    # Change mask layer blend mode to fit with 'Invert Mask Below'
    compare_mask_layer.setBlendMode(QPainter.CompositionMode_DestinationOut)

    return


def _create_compare_layer_group_and_mask():
    """Create layer group with mask at the top
    of layer tree return layer_group and compare_mask_layer"""
    project = QgsProject.instance()
    root = project.layerTreeRoot()

    # create compare layer group to the top of layer treee
    layer_group = QgsLayerTreeGroup("QMapCompare_Group")
    root.insertChildNode(0, layer_group)

    # Create a scratch polygon layer
    mask_layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "QMapCompare_mask", "memory")
    if not mask_layer.isValid():
        print("Failed to create the scratch layer")
    else:
        # Add polygon layer to compare layer group
        project.addMapLayer(
            mask_layer, False
        )  # Add without inserting into the default layer tree
        layer_group.addLayer(mask_layer)

    return layer_group, mask_layer
