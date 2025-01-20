import os
import sip

from PyQt5.QtWidgets import QDockWidget, QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.core import (
    QgsProject,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsApplication,
    QgsMapLayerModel,
)

from .comparator.process import compare_split, stop_compare


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

        self.ui.pushButton_h_split.clicked.connect(self._on_pushbutton_h_split_clicked)
        self.ui.pushButton_v_split.clicked.connect(self._on_pushbutton_v_split_clicked)
        self.ui.pushButton_lens.clicked.connect(self._on_pushbutton_lens_clicked)
        self.ui.pushButton_stopcompare.clicked.connect(
            self._on_pushbutton_stopcompare_clicked
        )

        # Populate layer tree box when open a project
        QgsProject.instance().readProject.connect(self.process_node)

        # memorize layers id checked by user
        self.checked_layers = []

    def _on_pushbutton_h_split_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            self.ui.pushButton_h_split.setEnabled(False)
            self.ui.pushButton_v_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(True)
            self._memorize_checked_layers(layers)
            compare_split(layers,"horizontal")
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    def _on_pushbutton_v_split_clicked(self):
        # get layers
        layers = self._get_checked_layers()
        if layers:
            self.ui.pushButton_v_split.setEnabled(False)
            self.ui.pushButton_h_split.setEnabled(True)
            self.ui.pushButton_lens.setEnabled(True)
            self._memorize_checked_layers(layers)
            compare_split(layers, "vertical")
        else:
            QMessageBox.information(
                None, "Error", "Please select at least one layer to compare"
            )

    # TODO: implement
    def _on_pushbutton_lens_clicked(self):
        QMessageBox.information(None, "Message", "Coming soon!")

    # TODO: implement
    def _on_pushbutton_lens_clicked(self):
        QMessageBox.information(None, "Message", "Lens Coming soon!")

    def _on_pushbutton_stopcompare_clicked(self):
        # remove compare layer group
        stop_compare()

        # re-enable all compare push_button
        self.ui.pushButton_h_split.setEnabled(True)
        self.ui.pushButton_v_split.setEnabled(True)
        self.ui.pushButton_lens.setEnabled(True)

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

            if child_type == "group":
                self._process_node_recursive(child, item)

    def _memorize_checked_layers(self, layers):
        for layer in layers:
            self.checked_layers.append(layer.id())
