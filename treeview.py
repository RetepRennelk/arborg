from PyQt5.QtWidgets import QTreeView


class TreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
