from PyQt5.QtCore import QAbstractItemModel


class TreeModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
