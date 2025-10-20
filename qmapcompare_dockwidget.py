import os

from qgis.core import (
    QgsApplication,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsMapLayerModel,
    QgsProject,
)
from qgis.PyQt import sip, uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDockWidget, QMessageBox, QTreeWidgetItem

from .comparator.constants import compare_group_name
from .comparator.process import (
    compare_with_mapview,
    compare_with_mask,
    stop_compare_with_mask,
    stop_mirror_compare,
)


class QMapCompareDockWidget(QDockWidget):
    def __init__(self):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(__file__), "qmapcompare_dockwidget.ui")
        if not os.path.exists(ui_file):
            raise FileNotFoundError(f"UI file not found: {ui_file}")

        try:
            self.ui = uic.loadUi(ui_file, self)
        except Exception as e:
            raise RuntimeError(f"Error when loading UI file: {str(e)}")

        # Update layer list when layer tree has been updated
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(
            self.process_node
        )

        # reprocess when UI layer tree changed
        self.ui.layerTree.itemChanged.connect(self._on_layertree_item_changed)

        # buttons tooltips
        self.ui.pushButton_h_split.setToolTip("Horizontal Split")
        self.ui.pushButton_v_split.setToolTip("Vertical Split")
        self.ui.pushButton_lens.setToolTip("Lens")
        self.ui.pushButton_mirror.setToolTip("Mirror")
        self.ui.pushButton_stopcompare.setToolTip("Stop Compare")

        # buttons connections
        self.ui.pushButton_h_split.clicked.connect(self._on_pushbutton_h_split_clicked)
        self.ui.pushButton_v_split.clicked.connect(self._on_pushbutton_v_split_clicked)
        self.ui.pushButton_lens.clicked.connect(self._on_pushbutton_lens_clicked)
        self.ui.pushButton_mirror.clicked.connect(self._on_pushbutton_mirror_clicked)
        self.ui.pushButton_stopcompare.clicked.connect(
            self._on_pushbutton_stopcompare_clicked
        )

        # Populate layer tree box when open a project
        QgsProject.instance().readProject.connect(self.process_node)

        # memorize layers id checked by user
        self.checked_layers = []

        # memorize current active mode
        # (inactive, hsplit, vsplit, lens, mirror)
        self.active_compare_mode = "inactive"

        # flag current process to avoid recusrsive process bugs
        self.is_processing = False

        # Stop compare mode when project is reinitialized
        QgsProject.instance().cleared.connect(self._on_pushbutton_stopcompare_clicked)

        # Hide close button to avoid accidental closing
        features = self.features()
        features = features & ~QDockWidget.DockWidgetClosable
        self.setFeatures(features)

    def _on_pushbutton_h_split_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            # Disable only horizontal split
            self.ui.pushButton_h_split.setEnabled(False)
            self.ui.pushButton_v_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(True)
            self.ui.pushButton_mirror.setEnabled(True)

            if self.active_compare_mode == "mirror":
                stop_mirror_compare()

            self.active_compare_mode = "hsplit"

            self._memorize_checked_layers(layers)

            self.is_processing = True
            compare_with_mask(layers, "horizontal")
            self.is_processing = False
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    def _on_pushbutton_v_split_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            # Disable only vertical split
            self.ui.pushButton_v_split.setEnabled(False)
            self.ui.pushButton_h_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(True)
            self.ui.pushButton_mirror.setEnabled(True)

            if self.active_compare_mode == "mirror":
                stop_mirror_compare()

            self.active_compare_mode = "vsplit"

            self._memorize_checked_layers(layers)

            self.is_processing = True
            compare_with_mask(layers, "vertical")
            self.is_processing = False
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    def _on_pushbutton_lens_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            # Disable only lens split
            self.ui.pushButton_h_split.setEnabled(True)
            self.ui.pushButton_v_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(False)
            self.ui.pushButton_mirror.setEnabled(True)

            if self.active_compare_mode == "mirror":
                stop_mirror_compare()

            self.active_compare_mode = "lens"

            self._memorize_checked_layers(layers)

            self.is_processing = True
            compare_with_mask(layers, "lens")
            self.is_processing = False
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    def _on_pushbutton_mirror_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            # Disable only mirror split
            self.ui.pushButton_h_split.setEnabled(True)
            self.ui.pushButton_v_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(True)
            self.ui.pushButton_mirror.setEnabled(False)

            # Stop compare to remove mask group layer
            if self.active_compare_mode in ["hsplit", "vsplit", "lens"]:
                stop_compare_with_mask()

            self.active_compare_mode = "mirror"

            self.is_processing = True
            compare_with_mapview(layers)
            self.is_processing = False
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    def _on_pushbutton_stopcompare_clicked(self):
        # remove compare layer group
        self.is_processing = True
        stop_compare_with_mask()
        if self.active_compare_mode == "mirror":
            stop_mirror_compare()
        self.is_processing = False

        # re-enable all compare push_button
        self.ui.pushButton_h_split.setEnabled(True)
        self.ui.pushButton_v_split.setEnabled(True)
        self.ui.pushButton_lens.setEnabled(True)
        self.ui.pushButton_mirror.setEnabled(True)

        self.active_compare_mode = "inactive"

    def _get_checked_layers(self):
        layers = []
        # Recursively retrieve child elements of a QTreeWidget
        for i in range(self.ui.layerTree.topLevelItemCount()):
            item = self.ui.layerTree.topLevelItem(i)
            layers.extend(self._get_checked_layers_recursive(item))
        return layers

    def _get_checked_layers_recursive(self, item):
        layers = []
        if item.checkState(0) == Qt.CheckState.Checked:
            layer = QgsProject.instance().mapLayer(item.text(1))
            if layer:
                layers.append(layer)
        for i in range(item.childCount()):
            child_item = item.child(i)
            layers.extend(self._get_checked_layers_recursive(child_item))
        return layers

    def process_node(self):
        """
        Read QGIS layer tree
        """
        if not self.isVisible():
            # don't process_node when dialog invisible to avoid crash
            return

        if self.is_processing:
            # don't process_node when compare setup is processing and avoid crash
            return

        self.ui.layerTree.clear()
        self._process_node_recursive(QgsProject.instance().layerTreeRoot(), None)

    def _process_node_recursive(self, node, parent_node):
        """
        Load QGIS layers to target layer tree
        """
        for child in node.children():
            # check signal is connected or not
            try:
                child.nameChanged.disconnect(self.process_node)
            except TypeError:
                # when signal is not connected
                pass
            child.nameChanged.connect(self.process_node)

            if QgsLayerTree.isGroup(child):
                if not isinstance(child, QgsLayerTreeGroup):
                    child = sip.cast(child, QgsLayerTreeGroup)
                child_type = "group"
                child_icon = QIcon(QgsApplication.iconPath("mActionFolder.svg"))
                child_id = ""

            elif QgsLayerTree.isLayer(child):
                if not isinstance(child, QgsLayerTreeLayer):
                    child = sip.cast(child, QgsLayerTreeLayer)

                if not child.layer():
                    continue

                child_type = "layer"
                child_icon = QgsMapLayerModel.iconForLayer(child.layer())
                child_id = child.layer().id()

                if not child.layer().isSpatial():
                    # exclude no geometry layers such as CSV files
                    continue

            else:
                raise Exception("Unknown child type")

            # Don't add compare group to layer tree
            if child.name() == compare_group_name:
                continue

            item = QTreeWidgetItem([child.name(), child_id])
            item.setIcon(0, child_icon)
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsAutoTristate
            )

            item.setCheckState(
                0,
                Qt.CheckState.Unchecked,
            )

            # recheck if layer has been checked by user on UI
            if child_id in self.checked_layers:
                item.setCheckState(
                    0,
                    Qt.CheckState.Checked,
                )

            # Move group or layer to its parent node
            if not parent_node:
                self.ui.layerTree.addTopLevelItem(item)
            else:
                parent_node.addChild(item)

            # add layers to layer tree UI except compare group's children
            if child_type == "group" and child.name() != compare_group_name:
                self._process_node_recursive(child, item)

    def _memorize_checked_layers(self, layers):
        self.checked_layers = []
        for layer in layers:
            self.checked_layers.append(layer.id())

    def _on_layertree_item_changed(self):
        """redo compare process if compare is active"""
        # dont't process if compare is inactive
        if self.active_compare_mode not in ["hsplit", "vsplit", "lens", "mirror"]:
            return

        layers = self._get_checked_layers()
        if layers:
            self.is_processing = True
            if self.active_compare_mode == "vsplit":
                compare_with_mask(layers, "vertical")
            if self.active_compare_mode == "hsplit":
                compare_with_mask(layers, "horizontal")
            if self.active_compare_mode == "lens":
                compare_with_mask(layers, "lens")
            if self.active_compare_mode == "mirror":
                compare_with_mapview(layers)

            self.is_processing = False

        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )
            # reinitialize UI since no layer has been selected
            self._on_pushbutton_stopcompare_clicked()
