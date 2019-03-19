from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QFrame, QMessageBox

from Client.src import src


class QImageWidget(QLabel):
    def __init__(self, img_path):
        super().__init__()

        image = QImage()
        image.load(img_path)
        pixmap: QPixmap = QPixmap().fromImage(image)
        pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.setPixmap(pixmap)


def QSeparator(orientation)->QFrame:
    if orientation == Qt.Vertical:
        frame = QFrame()
        frame.setFrameShape(QFrame.VLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame
    if orientation == Qt.Horizontal:
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        return frame
    raise ValueError(orientation)


class Message(QMessageBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        with open('Client/src/style.qss', 'r') as style_file:
            self.setStyleSheet(style_file.read())


class BisitorWidget(QWidget):
    _style_text: str = None

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        if BisitorWidget._style_text is None:
            with open(src.qss, 'r') as style_file:
                BisitorWidget._style_text = style_file.read()
        self.setStyleSheet(BisitorWidget._style_text)

