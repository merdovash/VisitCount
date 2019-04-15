import time

from PyQt5.QtCore import Qt

from Client.src import src

if __name__ == "__main__":
    import os
    import sys

    import PyQt5
    from PyQt5.QtGui import QFont, QPixmap
    from PyQt5.QtWidgets import QApplication, QStyleFactory, QSplashScreen

    pyqt = os.path.dirname(PyQt5.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

    app = QApplication(sys.argv)

    splash_pix = QPixmap(src.preload_image)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    font = QFont('Roboto')
    font.setPixelSize(12)
    font.setStyleName('Regular')
    app.setFont(font)
    app.setStyle(QStyleFactory().create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    from Client.IProgram import IProgram
    from Client.Program import MyProgram
    from Parser.client import client_args

    print(client_args)
    program: IProgram = MyProgram(css=client_args.css, test=client_args.test, host=client_args.host)

    old_hook = sys.excepthook


    def catch_exceptions(exception_type, exception, tb):
        program.window.error.emit(exception_type, exception, tb)
        old_hook(exception_type, exception, tb)


    sys.excepthook = catch_exceptions

    # test(program)
    splash.finish(program.window)
    sys.exit(app.exec_())
