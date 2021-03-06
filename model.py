from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, \
    pyqtSignal
from nestedtreedictionary import NestedDictionaryTree

class TreeModel(QAbstractItemModel):
    fileModified = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.ndt = NestedDictionaryTree()
        self.ndt.initialise(["Outline", "Comment"])
        self.filename = ""
        self.fileModifiedFlag = False
        
    def loadFile(self, filename):
        self.beginResetModel()
        self.ndt = NestedDictionaryTree.createTreeFromFile(filename)
        self.endResetModel()
        self.filename = filename
        self.fileModifiedFlag = False

    def saveFile(self, filename):
        self.filename = filename
        self.ndt.updateNDTfromTree()
        self.ndt.writeDD2File(filename)
        self.fileModifiedFlag = False

    def setFileModified(self, flag):
        if flag != self.fileModifiedFlag:
            self.fileModified.emit(flag)
        self.fileModifiedFlag = flag
        
    def getFileModified(self):
        return self.fileModifiedFlag
        
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

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.ndt.getRoot()

    def insertSiblingAbove(self, index, siblingNode=None):
        row = index.row()
        self.beginInsertRows(index.parent(), row, row)
        item = self.getItem(index)
        siblingNode = self.ndt.insertSiblingAbove(item, siblingNode)
        self.insertRow(row, index.parent())
        self.endInsertRows()
        
        if row == -1 and index.column() == -1:
            lastEditedIndex = self.index(0, 0, QModelIndex())
        else:
            lastEditedIndex = self.index(row, index.column(), index.parent())
        return lastEditedIndex, siblingNode

    def insertSiblingBelow(self, index, siblingNode=None):
        row = index.row()
        self.beginInsertRows(index.parent(), row+1, row+1)
        item = self.getItem(index)
        siblingNode = self.ndt.insertSiblingBelow(item, siblingNode)
        self.insertRow(row+1, index.parent())
        self.endInsertRows()
        
        if row == -1 and index.column() == -1:
            lastEditedIndex = self.index(0, 0, QModelIndex())
        else:
            lastEditedIndex = self.index(row+1, index.column(), index.parent())
        return lastEditedIndex, siblingNode
        
    def insertChildBelow(self, index, childNode=None):
        row = index.row()
        self.beginInsertRows(index, 0, 0)
        item = self.getItem(index)
        
        childNode = self.ndt.insertChildBelow(item, childNode)
        self.insertRow(0, index)
        
        self.endInsertRows()
        
        if row == -1 and index.column() == -1:
            lastEditedIndex = self.index(0, 0, QModelIndex())
        else:
            lastEditedIndex = self.index(0, index.column(), index)
        return lastEditedIndex, childNode

    def setData(self, index, txt, role):
        item = index.internalPointer()
        oldTxt = item.content[index.column()]
        if oldTxt != txt:
            item.content[index.column()] = txt
            super().setData(index, txt, role)
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        return False

    def deleteCell(self, index):
        row = index.row()
        self.beginRemoveRows(index.parent(), row, row)
        item = index.internalPointer()
        item.parent.removeChild(item)
        self.removeRow(row, index.parent())
        self.endRemoveRows()

    def areAllParentsIdentical(self, indices):
        parents = [i.parent() for i in indices]
        flag = all(p==parents[0] for p in parents)
        return flag

    def moveNodesUp(self, index, N_rows):
        row = index.row()
        parentIndex = index.parent()
        self.beginMoveRows(parentIndex, row, row+N_rows-1, parentIndex, row-1)
        item = self.getItem(index)
        parent = item.getParent()
        for i in range(N_rows):
            parent.moveChildUp(row+i)
        self.endMoveRows()
        return self.index(row-1, index.column(), parentIndex)

    def moveNodesDown(self, index, N_rows):
        row = index.row()
        parentIndex = index.parent()
        self.beginMoveRows(parentIndex, row, row+N_rows-1, parentIndex, row+N_rows+1)
        item = self.getItem(index)
        parent = item.getParent()
        for i in range(N_rows):
            parent.moveChildUp(row+N_rows-i)
        self.endMoveRows()
        return self.index(row+1, index.column(), parentIndex)

    def moveNodeCtrlShiftRight(self, index):
        '''A sibling becomes a parent.'''
        row = index.row()
        if row == 0:
            return None
        parentIndex = index.parent()
        siblingIndex = index.sibling(row-1, index.column())
        sibling = self.getItem(siblingIndex)
        N_children = sibling.childrenCount()
        self.beginMoveRows(parentIndex, row, row, siblingIndex, N_children)
        parentItem = self.getItem(parentIndex)
        item = self.getItem(index)
        parentItem.removeChild(item)
        sibling.appendChild(item)
        self.endMoveRows()
        return self.index(N_children, index.column(), siblingIndex)

    def moveNodeCtrlShiftLeft(self, index):
        '''A parent becomes a sibling.'''
        parentIndex = index.parent()
        parentItem = self.getItem(parentIndex)
        if parentItem.getParent() is None:
            return None
        self.makeSiblingsBelowChildren(index)
        grandParentIndex = parentIndex.parent()
        row = index.row()
        parentRow = parentIndex.row()
        self.beginMoveRows(parentIndex, row, row, grandParentIndex, parentRow+1)
        item = self.getItem(index)
        parentItem.removeChild(item)
        grandParentitem = self.getItem(grandParentIndex)
        grandParentitem.insertChild(item, parentRow+1)
        self.endMoveRows()
        newIndex = self.index(parentRow+1, 0, grandParentIndex)
        return newIndex
    
    def makeSiblingsBelowChildren(self, index):
        item = self.getItem(index)
        row = index.row()
        parentIndex = index.parent()
        parentItem = self.getItem(parentIndex)
        N_children = parentItem.childrenCount()
        flag = self.beginMoveRows(parentIndex, row+1, N_children-1, index, item.childrenCount())
        parentItem.makeChildrenToGrandChildren(item)
        self.endMoveRows()
