from qgis.core import QgsProject, QgsLayerTreeGroup, QgsVectorLayer, QgsGeometryGeneratorSymbolLayer, QgsFillSymbol

def compare_split(compare_layers):
    compare_layer_group, compare_mask_layer = _create_compare_layer_group_and_mask()

    # move target compare layers to layer group
    for layer in compare_layers:
        compare_layer_group.addLayer(layer)

    # TODO: Symbolize with geometry generator
    formula = """
    make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_height / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_height / 2)),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0
    )
    """

    # Step 3: Create a Geometry Generator Symbol Layer
    geometry_generator = QgsGeometryGeneratorSymbolLayer.create({
        'geometryModifier': formula,
        'geometry_type': 2,  # Polygon
        'extent': ''  # Use the default map extent
    })

    # Step 4: Create a symbol and apply the geometry generator
    symbol = QgsFillSymbol.createSimple({'color': '255,0,0,50'})  # Red fill with transparency
    symbol.changeSymbolLayer(0, geometry_generator)

    # Step 5: Apply the symbol to the scratch layer
    compare_mask_layer.renderer().setSymbol(symbol)


    return

def _create_compare_layer_group_and_mask() :
    """Create layer group with mask at the top
    of layer tree"""
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
        project.addMapLayer(mask_layer, False)  # Add without inserting into the default layer tree
        layer_group.addLayer(mask_layer)

    return layer_group, mask_layer


