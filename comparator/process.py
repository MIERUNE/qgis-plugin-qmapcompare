from qgis.core import QgsProject, QgsLayerTreeGroup, QgsVectorLayer

def compare_swipe(layers):
    compare_layer_group = _create_compare_layer_group_and_mask()
    _populate_compare_layers(layers, compare_layer_group)

    return

def _create_compare_layer_group_and_mask() -> QgsLayerTreeGroup:
    """Create layer group with mask at the top
    of layer tree"""
    project = QgsProject.instance()
    root = project.layerTreeRoot()

    # create compare layer group to the top of layer treee
    layer_group = QgsLayerTreeGroup("QMapCompare_Group")
    root.insertChildNode(0, layer_group) 

    # Create a scratch polygon layer
    scratch_layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "QMapCompare_mask", "memory")
    if not scratch_layer.isValid():
        print("Failed to create the scratch layer")
    else:
        # Step 3: Add the scratch layer to the project
        project.addMapLayer(scratch_layer, False)  # Add without inserting into the default layer tree

        # Step 4: Add the layer to the newly created group
        layer_group.addLayer(scratch_layer)

    return layer_group

def _populate_compare_layers(layers, comparer_layer_group):
    #TODO Move target layers to 
    return
