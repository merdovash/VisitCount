from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox


class AbstractWindow(QMainWindow):
    error = pyqtSignal(str)
    message = pyqtSignal(str, bool)
    ok_message = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__()

        self.error.connect(self.on_error)
        self.message.connect(self.on_show_message)
        self.ok_message.connect(self.on_ok_message)

    def change_widget(self, widget):
        self.setCentralWidget(widget)

    @pyqtSlot(str)
    def on_error(self, msg):
        QMessageBox().critical(self, "Ошибка", msg)

    @pyqtSlot(str, bool)
    def on_show_message(self, text, is_red):
        self.central_widget.show_message(text, is_red)

    @pyqtSlot(str, name='on_ok_message')
    def on_ok_message(self, text):
        QMessageBox().information(self, "Сообщение", text)

    @pyqtSlot(name='on_finish')
    def on_finish(self):
        self.ok_message.emit('Успешно сохранено')
        self.program.session.expire_all()
