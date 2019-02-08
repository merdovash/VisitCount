from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QWidget, QFileDialog


class IAcceptDrop:
    drop = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        if isinstance(self, QWidget):
            self.setAcceptDrops(True)
        else:
            raise TypeError(f'{self} must be QWidget')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()

            self.drop.emit(event.mimeData().urls())
        else:
            event.ignore()


class ISelectFile:
    last_path = '/'
    select_file = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        if isinstance(self, QWidget):
            self.select_file.connect(self._on_select_file)
        else:
            raise TypeError(f'{self} must be QWidget')

    def _on_select_file(self, callback, title="Выберите файл", suffixs="Document Word (*.docx)"):
        user_input = QFileDialog().getOpenFileUrls(
            self,
            title,
            self.last_path,
            suffixs)
        if user_input is not None and len(user_input[0]) > 0:
            files = user_input[0]
            for file in files:
                callback(file)
            ISelectFile.last_path = str(Path(files[0].path()).relative_to('/'))
