from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.gui import QgsFileWidget
from .cluster_dialog import ClusterDialog
from .utils.clustering import run_clustering

class GreedyClusterPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None

    def initGui(self):
        self.action = QAction(QIcon(), "Greedy Cluster", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Greedy Cluster", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Greedy Cluster", self.action)

    def run(self):
        
        if self.dlg is None:
            self.dlg = ClusterDialog()

            # Connect field combo to the layer combo box
            self.dlg.fieldComboBox.setLayer(self.dlg.layerComboBox.currentLayer())
            self.dlg.layerComboBox.layerChanged.connect(self.dlg.fieldComboBox.setLayer)
            self.dlg.outputFileWidget.setStorageMode(QgsFileWidget.SaveFile)
            self.dlg.outputFileWidget.setDialogTitle("Select output file")
            self.dlg.outputFileWidget.setDefaultRoot("")

            # Connect RUN button to clustering
            self.dlg.runButton.clicked.connect(self.run_clustering_action)

        # Show dialog
        self.dlg.show()
        result = self.dlg.exec_()

        if result:
            self.run_clustering_action()

    def run_clustering_action(self):
        input_layer = self.dlg.layerComboBox.currentLayer()
        selected_field = self.dlg.fieldComboBox.currentField()
        max_sum = self.dlg.sumSpinBox.value()
        output_path = self.dlg.outputFileWidget.filePath()

        if input_layer:
            run_clustering(input_layer, selected_field, max_sum, output_path)
            self.iface.messageBar().pushSuccess("Greedy Cluster", "Clustering complete!")
        else:
            self.iface.messageBar().pushWarning("Greedy Cluster", "No layer selected.")
        
        
        """if self.dlg is None:
            self.dlg = ClusterDialog()

        self.dlg.show()
        result = self.dlg.exec_()

        if result:
            input_layer = self.dlg.layerComboBox.currentLayer()
            selected_field = self.dlg.fieldComboBox.currentField()
            target_sum = self.dlg.sumSpinBox.value()
            output_path = self.dlg.outputFileWidget.filePath()

            if input_layer:
                run_clustering(input_layer, selected_field, target_sum, output_path)
                self.iface.messageBar().pushSuccess("Greedy Cluster", "Clustering complete!")
            else:
                self.iface.messageBar().pushWarning("Greedy Cluster", "No layer selected.")"""