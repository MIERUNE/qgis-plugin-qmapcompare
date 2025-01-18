from qgis.core import (
    QgsProject,
    QgsLayerTreeGroup,
    QgsMapLayer,
    QgsVectorLayer,
    QgsGeometryGeneratorSymbolLayer,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsInvertedPolygonRenderer,
    QgsGroupLayer,
    QgsCoordinateTransformContext
)
from qgis.PyQt.QtGui import QPainter

from .constants import compare_mask_layer_name, compare_group_name


def compare_split(compare_layers: list) -> None:
    """
    Make QGIS Map to be in compare split mode 
    with input compare layers 
    """

    compare_layer_group, compare_mask_layer = _create_compare_layer_group_and_mask()

    # Add target compare layers to layer group
    for layer in compare_layers:
        # get layer origin node
        root = QgsProject.instance().layerTreeRoot()
        layer_node = root.findLayer(layer.id())
        
        # Hide target layer to be shown in Compare Group
        layer_node.setItemVisibilityChecked(False)
        
        # Add layer to compare group if not existing
        if not _is_in_group(layer, compare_layer_group): 
            compare_layer_group.addLayer(layer)
    

    # Symbolize mask with geometry generator
    formula = """make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_height / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_height / 2)),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0)"""

    geometry_generator = QgsGeometryGeneratorSymbolLayer.create(
        {
            "geometryModifier": formula,
            "geometry_type": 2,  # Polygon
            "extent": "",  
        }
    )

    symbol = QgsFillSymbol.createSimple(
        {"color": "255,0,0,50"}
    )  
    symbol.changeSymbolLayer(0, geometry_generator)

    #  Create the inverted polygon renderer
    inverted_renderer = QgsInvertedPolygonRenderer(QgsSingleSymbolRenderer(symbol))
    compare_mask_layer.setRenderer(inverted_renderer)

    # Change mask layer blend mode to fit with 'Invert Mask Below'
    compare_mask_layer.setBlendMode(QPainter.CompositionMode_DestinationOut)

    return


def _create_compare_layer_group_and_mask()-> tuple[QgsLayerTreeGroup,QgsMapLayer]:
    """Create layer group with mask layer inside at the top
    of layer tree return layer_group and compare_mask_layer
    Output: 
    - layer_group_node: Compare Layer Group, 
    - mask_layer: Compare mask layer 
    """

    project = QgsProject.instance()
    root = project.layerTreeRoot()
    
    # Create a scratch polygon layer
    mask_layers =  project.mapLayersByName(compare_mask_layer_name)
    if mask_layers:
        mask_layer = mask_layers[0]
    else:
        mask_layer = QgsVectorLayer("Polygon?crs=EPSG:3857", compare_mask_layer_name, "memory")
        if not mask_layer.isValid():
            print("Failed to create the scratch layer")
        else:
            # Add polygon layer to compare layer group
            project.addMapLayer(
                mask_layer, False
            )  
            
        
    # create compare layer group to the top of layer treee
    options = QgsGroupLayer.LayerOptions(QgsCoordinateTransformContext())
    group_layer = QgsGroupLayer('group', options)
    group_layer.setChildLayers([mask_layer])

    project.addMapLayer(group_layer, False)
    layer_group_node = QgsLayerTreeGroup(compare_group_name)
    layer_group_node.setGroupLayer(group_layer)

    layer_group_node.addLayer(mask_layer)
    root.insertChildNode(0, layer_group_node)
        
    return layer_group_node, mask_layer


def _is_in_group(layer:QgsMapLayer, layer_group:QgsMapLayer) -> bool:
    """Return True if a target layer is in a target layer groyp"""
    for child in layer_group.children():
        if child.layerId() == layer.id():  # 0 = Layer node
            return True
    return False