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


class QMapCompareDockWidget(QDockWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qmapcompare_dockwidget.ui"), self
        )

        # レイヤーが追加されるなど、レイヤー一覧が変更されたときに更新する
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(
            self.process_node
        )

        self.ui.pushButton_mirror.clicked.connect(self._on_pushbutton_mirror_clicked)
        self.ui.pushButton_swipe.clicked.connect(self._on_pushbutton_swipe_clicked)
        self.ui.pushButton_lens.clicked.connect(self._on_pushbutton_lens_clicked)
        self.ui.pushButton_stopcompare.clicked.connect(
            self._on_pushbutton_stopcompare_clicked
        )

        # Populate layer tree box when open a project
        QgsProject.instance().readProject.connect(self.process_node)

    # TODO: implement
    def _on_pushbutton_mirror_clicked(self):
        QMessageBox.information(None, "Message", "Mirror")

    # TODO: implement
    def _on_pushbutton_swipe_clicked(self):
        QMessageBox.information(None, "Message", "Swipe")

    # TODO: implement
    def _on_pushbutton_lens_clicked(self):
        QMessageBox.information(None, "Message", "Lens")

    # TODO: implement
    def _on_pushbutton_stopcompare_clicked(self):
        QMessageBox.information(None, "Message", "Stop!")

    def _get_checked_layers(self):
        layers = []
        # QTreeWidgetの子要素を再帰的に取得する
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
        QGISのレイヤーツリーを再帰的に読み込み

        Args:
            node (_type_): _description_
            parent_node (_type_): _description_
            parent_tree (_type_): _description_

        Raises:
            Exception: _description_
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
                    print("not")
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

            # Move group or layer to its parent node
            if not parent_node:
                self.ui.layerTree.addTopLevelItem(item)
            else:
                parent_node.addChild(item)

            if child_type == "group":
                self._process_node_recursive(child, item)
