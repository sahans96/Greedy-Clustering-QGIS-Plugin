from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "forms", "Design.ui"))

class ClusterDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(ClusterDialog, self).__init__(parent)
        self.setupUi(self)
