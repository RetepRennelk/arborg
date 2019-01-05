from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from nestedtreedictionary import NestedDictionaryTree

class TreeModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.ndt = NestedDictionaryTree()
        self.ndt.initialise(["Outline", "Comment"])
        self.filename = ""
        
    def loadFile(self, filename):
        self.beginResetModel()
        self.ndt = NestedDictionaryTree.createTreeFromFile(filename)
        self.endResetModel()
        self.filename = filename
        
    def columnCount(self, parent=None):
        return self.ndt.columnCount()

    def rowCount(self, parent):
        if not parent.isValid():
            parentObject = self.ndt.getRoot()
        else:
            parentObject = parent.internalPointer()
        N_children = 0 if parentObject is None else len(parentObject.getChildren())
        return N_children

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            parentObject = self.ndt.getRoot()
        else:
            parentObject = parent.internalPointer()
        if row>=0 and row<len(parentObject.getChildren()):
            idx = parentObject.getChildren()[row]
            return self.createIndex(row, column, idx)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        indexObject = index.internalPointer()
        parentObject = indexObject.getParent()
        if parentObject == self.ndt.getRoot():
            return QModelIndex()
        grandParentObject = parentObject.getParent()
        row = grandParentObject.getChildren().index(parentObject)
        return self.createIndex(row, 0, parentObject)

    def data(self, index, role):
        if not index.isValid():
            return QModelIndex()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            item = index.internalPointer()
            return item.content[index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.ndt.getRoot().content[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return 0
        return Qt.ItemIsEditable | super().flags(index)

    def setHeaderData(self, section, orientation, value):
        flag = self.ndt.setHeaderData(section, value)
        if flag:
            # The documentation demands the signal headerDataChanged to be emitted
            # when the data has changed.
            self.headerDataChanged.emit(orientation, section, section)
        return flag # True would mean data was changed





