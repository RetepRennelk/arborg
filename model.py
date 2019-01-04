from PyQt5.QtCore import QAbstractItemModel
from nestedtreedictionary import NestedDictionaryTree

class TreeModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.ndt = NestedDictionaryTree()

    def loadFile(self, filename):
        self.ndt = NestedDictionaryTree.createTreeFromFile(filename)
