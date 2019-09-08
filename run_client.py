if __name__ == "__main__":
    import os
    import sys

    # инициализация
    from Parser import Args
    Args('client')

    import PyQt5

    from PyQt5.QtGui import QFont, QFontDatabase
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5 import QtWebEngineWidgets # обязательно импортировать

    from Client.MyQt.Window.Auth import AuthWindow
    from Client.src import src, resource


    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

    app = QApplication(sys.argv+["--disable-web-security"])

    id = QFontDatabase.addApplicationFont(str(resource("AlegreyaSans-Regular.ttf")))
    family = QFontDatabase.applicationFontFamilies(id)[0]

    font = QFont(family)
    font.setPixelSize(14)
    font.setStyleName('Regular')
    app.setFont(font)
    app.setStyle(QStyleFactory().create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    from BisitorLogger.client import init as LoggerInit
    LoggerInit()

    old_hook = sys.excepthook

    def catch_exceptions(exception_type, exception, tb):
        from Domain.Exception import BisitorException
        if isinstance(exception, BisitorException):
                exception.show(exception.window)
        else:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            QMessageBox().critical(None,
                                   "Непредвиденная ошибка",
                                   "Exception type: {},\n"
                                   "value: {},\n"
                                   "tb: {}".format(exception_type, exception, traceback.format_tb(tb)))
        old_hook(exception_type, exception, tb)

    sys.excepthook = catch_exceptions

    # test(program)
    auth = AuthWindow()
    auth.show()
    sys.exit(app.exec_())
