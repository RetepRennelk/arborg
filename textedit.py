from PyQt5.QtWidgets import QTextEdit, QShortcut
from PyQt5.QtGui import QKeySequence, QTextCursor
from PyQt5.QtCore import QSize


class TextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.document().contentsChanged.connect(self.sizeChange)

        shortcut = QShortcut(QKeySequence("Ctrl+Down"), self)
        shortcut.activated.connect(self.splitCell)

    def sizeHint(self):
        w = self.document().size().width()
        h = self.document().size().height()
        return QSize(w, h)

    def sizeChange(self):
        h = self.document().size().height()
        if h < self.parent().geometry().height():
            self.setMinimumHeight(h)

    def splitCell(self):
        tc = self.textCursor()
        tc.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        txt = tc.selectedText()
        tc.removeSelectedText()

        delegate = self.parent()
        treeView = delegate.parent()
        treeView.splitCell(txt)
        treeView.itemDelegate().commit_and_close_editor()