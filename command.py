from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand


class EditCommand(QUndoCommand):
    '''This command allows to return to the state of a cell before editing took place.
    '''
    def __init__(self, model, index, newTxt, oldTxt):
        super().__init__()
        self.model = model
        self.index = index
        self.newTxt = newTxt
        self.oldTxt = oldTxt

    def redo(self):
        self.model.setData(self.index, self.newTxt, Qt.EditRole)

    def undo(self):
        self.model.setData(self.index, self.oldTxt, Qt.EditRole)

    
