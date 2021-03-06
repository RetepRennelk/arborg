from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand, QAbstractItemView


class UndoCommand(QUndoCommand):
    def __init__(self, model, index):
        super().__init__()
        self.model = model
        self.index = index
        self.parentIndex = index.parent()
        self.item = self.model.getItem(self.index)
        self.parent = self.item.getParent()
        self.row = self.index.row()
        # Remember the file state before the first redo.
        self.fileModified = model.getFileModified()

    def redo(self):
        self.model.setFileModified(True)

    def undo(self):
        self.model.setFileModified(self.fileModified)

class EditCommand(UndoCommand):
    '''This command allows to return to the state of a cell before editing took place.
    '''
    def __init__(self, model, index, newTxt, oldTxt):
        super().__init__(model, index)
        self.newTxt = newTxt
        self.oldTxt = oldTxt

    def redo(self):
        super().redo()
        self.model.setData(self.index, self.newTxt, Qt.EditRole)

    def undo(self):
        super().undo()
        self.model.setData(self.index, self.oldTxt, Qt.EditRole)

class DeleteCellCommand(UndoCommand):
    def __init__(self, model, index):
        super().__init__(model, index)

    def deleteIndex(self):
        self.model.beginRemoveRows(self.parentIndex, self.row, self.row)
        self.parent.removeChild(self.item)
        self.model.removeRow(self.row, self.parentIndex)
        self.model.endRemoveRows()

    def undo(self):
        super().undo()
        self.model.beginInsertRows(self.index.parent(), self.row, self.row)
        self.parent.children.insert(self.row, self.item)
        self.model.insertRow(self.row, self.index.parent())
        self.model.endInsertRows()

    def redo(self):
        super().redo()
        self.deleteIndex()

class InsertSiblingAboveCommand(UndoCommand):
    def __init__(self, model, index, treeView):
        super().__init__(model, index)
        self.siblingNode = None
        self.treeView = treeView

    def undo(self):
        super().undo()
        self.model.deleteCell(self.lastEditedIndex)

    def redo(self):
        super().redo()
        # Ensure that the same node is reinserted once it has been created.
        self.lastEditedIndex, self.siblingNode = self.model.insertSiblingAbove(self.index, self.siblingNode)
        self.treeView.setCurrentIndex(self.lastEditedIndex)

class InsertSiblingBelowCommand(UndoCommand):
    def __init__(self, model, index, treeView):
        super().__init__(model, index)
        self.siblingNode = None
        self.treeView = treeView

    def undo(self):
        super().undo()
        self.model.deleteCell(self.lastEditedIndex)

    def redo(self):
        super().redo()
        # Ensure that the same node is reinserted once it has been created.
        self.lastEditedIndex, self.siblingNode = self.model.insertSiblingBelow(self.index, self.siblingNode)
        self.treeView.setCurrentIndex(self.lastEditedIndex)

class InsertChildBelowCommand(UndoCommand):
    def __init__(self, model, index, treeView):
        super().__init__(model, index)
        self.siblingNode = None
        self.treeView = treeView

    def undo(self):
        super().undo()
        self.model.deleteCell(self.lastEditedIndex)

    def redo(self):
        super().redo()
        # Ensure that the same node is reinserted once it has been created.
        self.lastEditedIndex, self.siblingNode = self.model.insertChildBelow(self.index, self.siblingNode)
        self.treeView.setCurrentIndex(self.lastEditedIndex)

class MoveChildrenUpCommand(UndoCommand):
    def __init__(self, model, index, N_rows):
        super().__init__(model, index)
        self.N_rows = N_rows

    def undo(self):
        super().undo()
        self.model.moveNodesDown(self.lastEditedIndex, self.N_rows)

    def redo(self):
        super().redo()
        self.lastEditedIndex = self.model.moveNodesUp(self.index, self.N_rows)


class MoveChildrenDownCommand(UndoCommand):
    def __init__(self, model, index, N_rows):
        super().__init__(model, index)
        self.N_rows = N_rows

    def undo(self):
        super().undo()
        self.model.moveNodesUp(self.lastEditedIndex, self.N_rows)

    def redo(self):
        super().redo()
        self.lastEditedIndex = self.model.moveNodesDown(self.index, self.N_rows)


class MoveChildrenCtrlRightCommand(UndoCommand):
    def __init__(self, model, index, treeView):
        super().__init__(model, index)
        self.treeView = treeView

    def undo(self):
        super().undo()
        item = self.model.getItem(self.lastEditedIndex)
        self.lastEditedIndex = self.model.moveNodeCtrlShiftLeft(self.lastEditedIndex)
        self.treeView.expand(self.lastEditedIndex.parent())

    def redo(self):
        super().redo()
        self.lastEditedIndex = self.model.moveNodeCtrlShiftRight(self.index)
        item = self.model.getItem(self.lastEditedIndex)
        if self.lastEditedIndex:
            self.treeView.expand(self.lastEditedIndex.parent())

