from PyQt5.QtWidgets import QAction


class QShowAction(QAction):
    def __init__(self, title, parent, widget, tooltip=None):
        super().__init__(title, parent)
        self.setToolTip(title if tooltip is None else tooltip)
        self.widget = widget

        self.triggered.connect(lambda: self.widget.show())

    def __call__(self, *args, **kwargs):
        self.widget.show()
