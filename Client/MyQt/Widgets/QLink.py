from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class QLink(QLabel):
    def __init__(self, text, link):
        super().__init__(text)

        self.setText(f"<a href=\"{link}\">{text}</a>")
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)
