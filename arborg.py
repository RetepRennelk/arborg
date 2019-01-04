import sys
from PyQt5.QtWidgets import QApplication
from model import TreeModel
from treeview import TreeView

app = QApplication(sys.argv)

model = TreeModel()
view = TreeView(model)
view.setGeometry(300, 200, 300, 500)
view.show()
app.exec_()
