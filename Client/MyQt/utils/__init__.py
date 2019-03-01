import sys

from PyQt5.QtWidgets import QApplication


def simple_show(widget_class, *args, **kwargs):
    app = QApplication(sys.argv)

    widget = widget_class(*args, **kwargs)
    widget.show()

    sys.exit(app.exec_())