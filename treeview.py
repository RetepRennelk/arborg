from PyQt5.QtWidgets import QTreeView, QShortcut, QFileDialog, QLineEdit, \
    QAbstractItemView, QUndoStack
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QEvent, QRect
import config
from styleditemdelegate import StyledItemDelegate
from command import EditCommand, DeleteCellCommand, InsertSiblingAboveCommand, \
    InsertSiblingBelowCommand, InsertChildBelowCommand

class TreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setItemDelegate(StyledItemDelegate(self))
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
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

        shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut.activated.connect(self.insertSiblingAbove)

        shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        shortcut.activated.connect(self.insertSiblingBelow)

        shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), self)
        shortcut.activated.connect(self.insertChildBelow)

        self.initUndo()
        
    def initUndo(self):
        self.undoStack = QUndoStack(self)
        
        shortcut = QShortcut(QKeySequence.Undo, self)
        shortcut.activated.connect(self.undoStack.undo)

        shortcut = QShortcut(QKeySequence.Redo, self)
        shortcut.activated.connect(self.undoStack.redo)

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
        if filename != "":
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

    def keyPressEvent(self, event):
        currentIndex = self.currentIndex()
        if not currentIndex.isValid():
            return
        m = self.model()
        if event.key() == Qt.Key_Left:
            parentIdx = m.parent(currentIndex)
            if currentIndex.column() > 0:
                newIndex = m.index(currentIndex.row(), currentIndex.column()-1, parentIdx)
                self.setCurrentIndex(newIndex)
            return
        elif event.key() == Qt.Key_Right:
            parentIdx = m.parent(currentIndex)
            if currentIndex.column() < m.columnCount()-1:
                newIndex = m.index(currentIndex.row(), currentIndex.column()+1, parentIdx)
                self.setCurrentIndex(newIndex)
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj, ev):
        if obj == self.he:
            sw1 = ev.type() == QEvent.FocusOut
            sw2 = ev.type() == QEvent.KeyPress and ev.key() == Qt.Key_Return
            if sw1 or sw2:
                header = self.he.parentWidget().parentWidget()
                header.model().setHeaderData(self.he_index, header.orientation(), self.he.text())
                self.he.deleteLater()
                self.he = None
        else:
            sw = ev.type() == QEvent.KeyPress and ev.key() == Qt.Key_F2
            if sw:
                self.edit(self.currentIndex(), QAbstractItemView.AllEditTriggers, None)
                return True


        return super().eventFilter(obj, ev)

    def insertSiblingAbove(self):
        insertSiblingAboveCommand = InsertSiblingAboveCommand(self.model(), self.currentIndex(), self)
        self.undoStack.push(insertSiblingAboveCommand)

    def insertSiblingBelow(self):
        insertSiblingBelowCommand = InsertSiblingBelowCommand(self.model(), self.currentIndex(), self)
        self.undoStack.push(insertSiblingBelowCommand)

    def insertChildBelow(self):
        insertChildBelowCommand = InsertChildBelowCommand(self.model(), self.currentIndex(), self)
        self.undoStack.push(insertChildBelowCommand)
        """ currentIndex = self.currentIndex()
        lastEditedIndex = self.model().insertChildBelow(currentIndex)
        self.lastEditedIndex = lastEditedIndex
        self.setCurrentIndex(lastEditedIndex)
        self.edit(lastEditedIndex, QAbstractItemView.AllEditTriggers, None) """

    def deleteCell(self, index=None):
        if index is None:
            index = self.currentIndex()
        delecteCellCommand = DeleteCellCommand(self.model(), index)
        self.undoStack.push(delecteCellCommand)

    def deleteLastEditedIndex(self):
        if self.lastEditedIndex:
            self.model().deleteCell(self.lastEditedIndex)
        self.lastEditedIndex = None

    def setModelData(self, index, newTxt, oldTxt, role):
        if newTxt != oldTxt:
            editCommand = EditCommand(self.model(), index, newTxt, oldTxt)
            self.undoStack.push(editCommand)

