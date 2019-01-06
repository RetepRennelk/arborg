from PyQt5.QtWidgets import QStyledItemDelegate
from textedit import TextEdit
from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QTextCursor, QTextDocument


class StyledItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        self.t = TextEdit(parent)
        return self.t

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setPlainText(value)
        editor.moveCursor(QTextCursor.End)

    def setModelData(self, editor, model, index):
        txt = editor.toPlainText()
        model.setData(index, txt, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        item = index.internalPointer()
        height = 0
        for content in item.content:
            doc = QTextDocument()
            doc.setPlainText(content)
            doc.setTextWidth(option.rect.width())
            if doc.size().height() > height:
                height = doc.size().height()
        return QSize(option.rect.width(), height)
        
    def commit_and_close_editor(self):
        self.commitData.emit(self.t)
        self.closeEditor.emit(self.t)

    def eventFilter(self, editor, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.commit_and_close_editor()
                treeView = self.parent()
                treeView.deleteLastEditedIndex()
                return False
        return super().eventFilter(editor, event)
