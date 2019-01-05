from PyQt5.QtWidgets import QTreeView, QShortcut, QFileDialog, QLineEdit
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QEvent, QRect

class TreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.he = None
        self.he_index = None

        self.header().setSectionsClickable(True)
        self.header().sectionClicked.connect(self.sectionClicked)

        shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut.activated.connect(self.openFile)

    def openFile(self):
        fd = QFileDialog(self)
        fd.setNameFilter("Arborg files (*.ndt)")
        if fd.exec():
            filenames = fd.selectedFiles()
            self.model().loadFile(filenames[0])

    def sectionClicked(self, index):
        rect = QRect()
        header = self.header()
        rect.setLeft(header.sectionPosition(index))
        rect.setWidth(header.sectionSize(index))
        rect.setTop(0)
        rect.setHeight(header.height())
        he = QLineEdit(header.viewport())
        he.move(rect.topLeft())
        he.resize(rect.size())
        he.setFrame(False)
        he.setFocus()
        he.show()
        he.installEventFilter(self)
        txt = header.model().headerData(index, header.orientation())
        he.setText(txt)
        self.he_index = index
        self.he = he

    def eventFilter(self, obj, ev):
        if obj == self.he and ev.type() == QEvent.FocusOut:
            header = self.he.parentWidget().parentWidget()
            header.model().setHeaderData(self.he_index, header.orientation(), self.he.text())
            self.he.deleteLater()
            self.he = None
        return super().eventFilter(obj, ev)



