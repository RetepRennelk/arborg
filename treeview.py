from PyQt5.QtWidgets import QTreeView, QShortcut, QFileDialog, QLineEdit, \
    QAbstractItemView
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QEvent, QRect
import config

class TreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        
        self.lastEditedIndex = None

        self.he = None
        self.he_index = None

        self.header().setSectionsClickable(True)
        self.header().sectionClicked.connect(self.sectionClicked)

        shortcut = QShortcut(QKeySequence("Delete"), self)
        shortcut.activated.connect(self.deleteCell)

        shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut.activated.connect(self.openFile)

        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.saveFile)

        self.model().headerDataChanged.connect(self.showModelInvalid)
        self.model().layoutChanged.connect(self.showModelInvalid)

        shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        shortcut.activated.connect(self.insertSiblingBelow)

        shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), self)
        shortcut.activated.connect(self.insertChildBelow)

    def showModelInvalid(self):
        filename = self.model().filename
        if filename == "":
            title = config.windowTitle
        else:
            title = config.windowTitle + ": " + filename + " (*)"
        self.setWindowTitle(title)

    def showModelValid(self):
        filename = self.model().filename
        if filename == "":
            title = config.windowTitle
        else:
            title = config.windowTitle + ": " + filename
        self.setWindowTitle(title)

    def openFile(self):
        fd = QFileDialog(self)
        fd.setNameFilter(config.nameFilterString)
        if fd.exec():
            filenames = fd.selectedFiles()
            self.model().loadFile(filenames[0])
            self.showModelValid()

    def saveFile(self):
        fd = QFileDialog(self)
        fd.setNameFilter(config.nameFilterString)
        filename = self.model().filename
        if filename == "":
            if fd.exec():
                filename = fd.selectedFiles()[0]
                if not filename.endswith(config.fileEnding):
                    filename += config.fileEnding
        self.model().saveFile(filename)
        self.showModelValid()

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
        if obj == self.he:
            sw1 = ev.type() == QEvent.FocusOut
            sw2 = ev.type() == QEvent.KeyPress and ev.key() == Qt.Key_Return
            if sw1 or sw2:
                header = self.he.parentWidget().parentWidget()
                header.model().setHeaderData(self.he_index, header.orientation(), self.he.text())
                self.he.deleteLater()
                self.he = None

        return super().eventFilter(obj, ev)

    def insertSiblingBelow(self):
        currentIndex = self.currentIndex()
        lastEditedIndex = self.model().insertSiblingBelow(currentIndex)
        self.lastEditedIndex = lastEditedIndex
        self.setCurrentIndex(lastEditedIndex)
        self.edit(lastEditedIndex, QAbstractItemView.AllEditTriggers, None)

    def insertChildBelow(self):
        currentIndex = self.currentIndex()
        lastEditedIndex = self.model().insertChildBelow(currentIndex)
        self.lastEditedIndex = lastEditedIndex
        self.setCurrentIndex(lastEditedIndex)
        self.edit(lastEditedIndex, QAbstractItemView.AllEditTriggers, None)

    def deleteCell(self, index=None):
        if index is None:
            index = self.currentIndex()
        self.model().deleteCell(index)

    def deleteLastEditedIndex(self):
        if self.lastEditedIndex:
            self.model().deleteCell(self.lastEditedIndex)
        self.lastEditedIndex = None


