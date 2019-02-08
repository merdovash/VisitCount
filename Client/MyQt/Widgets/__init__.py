from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QFrame


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
