from PyQt5.QtWidgets import QTreeView, QShortcut, QFileDialog
from PyQt5.QtGui import QKeySequence

class TreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)

        shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut.activated.connect(self.openFile)

    def openFile(self):
        fd = QFileDialog(self)
        fd.setNameFilter("Arborg files (*.ndt)")
        if fd.exec():
            filenames = fd.selectedFiles()
            self.model().loadFile(filenames[0])



