import sys
from PyQt5.QtWidgets import QApplication
from model import TreeModel
from treeview import TreeView
import config

app = QApplication(sys.argv)

model = TreeModel()
view = TreeView(model)
view.setGeometry(300, 200, 500, 500)
view.setWindowTitle(config.windowTitle)
view.show()
app.exec_()
