"""
This module contains main Window with tables

TODO:
    * fix error on relogin after changing user
"""
import datetime
from typing import List

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QStatusBar, QMessageBox

from Client.IProgram import IProgram
from Client.MyQt.Widgets.LoadData import LoadingWizardWindow
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.Widgets.VisualData.VisualMenu import VisualWidget
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.ExcelLoadingWindow import ExcelLoadingWidget
from Client.MyQt.Window.Main.UiTableWindow import UI_TableWindow
from Client.MyQt.Window.NotificationParam import NotificationWindow
from Client.Reader.Functor.RegisterCardProcess import RegisterCardProcess
from DataBase2 import Professor, Lesson

month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(
    ',')


def closest_lesson(lessons: List[Lesson]):
    """

    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """

    now = datetime.datetime.now()
    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(now - x.date))
    return closest


class MainWindow(AbstractWindow):
    """
    class represents main window in program. includes table, control elements, status info, professor data.
    """

    log_out = pyqtSignal()

    def __init__(self, program: IProgram, professor: Professor):
        AbstractWindow.__init__(self)

        self.program: IProgram = program

        self.professor = professor

        self.central_widget = MainWindowWidget(
            program=program,
            professor=professor,
            parent=self)

        self.setCentralWidget(self.central_widget)

        self.__init_menu__()

        self.showMaximized()

        self.setAcceptDrops(True)

        self.setStatusBar(QStatusBar(self))

        self.log_out.connect(lambda: self.program.change_user())

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

            try:
                self.setDialog(
                    dialog=ExcelLoadingWidget(
                        files=event.mimeData().urls(),
                        program=self.program
                    )
                )
            except Exception as e:
                self.error.emit(str(e))
        else:
            event.ignore()

    def closeEvent(self, *args, **kwargs):
        if self.program.reader() is not None:
            self.program.reader().close()

    def __init_menu__(self):
        menu_bar = self.menuBar()

        self.menu_bar = menu_bar

        self._init_menu_file()
        self._init_menu_analysis()
        self._init_menu_view()
        self._init_menu_lessons()
        self._init_menu_updates()
        self._init_notification()

    def _init_menu_analysis(self):
        def show():
            if not hasattr(self, 'visual') or self.visual is None:
                self.visual = VisualWidget(self.professor)
            self.visual.show()

        analysis = self.menu_bar.addMenu("Анализ")

        analysis.addAction("Просмотр", show)

    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

    def _init_menu_file(self):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(self.log_out)

        file.addAction(file_change_user)

        if self.professor.card_id is None:
            def register_card():
                register_process = RegisterCardProcess(self.professor, self)
                register_process.success.connect(lambda: register_professor_card.setVisible(False))

            register_professor_card = QAction("Зарегистрировать карту", self)
            register_professor_card.triggered.connect(register_card)
            file.addAction(register_professor_card)

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(self.close)

        file.addAction(file_exit)

    def _init_menu_view(self):
        view: QMenu = self.menu_bar.addMenu("Вид")

        data = QMenu('Заголовок таблицы')
        view.addMenu(data)

        view.addSeparator()
        view.addAction('Отображать перекрестие', self.centralWidget().switch_show_table_cross)

    def _init_menu_updates(self):
        def update_db_action():
            self.update_action_dialog = SendUpdatesWidget(self.program)
            self.update_action_dialog.show()

        def show_loader_widget():
            self.loader_Widget = LoadingWizardWindow(self.professor)
            self.loader_Widget.show()

        updates = self.menu_bar.addMenu("Данные")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(update_db_action)

        load_new_action = QAction("Загрузить данные", self)
        load_new_action.triggered.connect(show_loader_widget)

        updates.addAction(updates_action)
        updates.addAction(load_new_action)

    def _init_notification(self):
        def show_notification_window():
            if self.notification_window is None:
                self.notification_window = NotificationWindow(program=self.program)
                self.notification_window.show()
                self.notification_window.close = lambda x: x.setVisible(False)
            else:
                self.notification_window.activateWindow()
                self.notification_window.setVisible(True)
                self.notification_window.raise_()

        self.notification_window: NotificationWindow = None
        note = self.menu_bar.addMenu('Оповещения')

        note_run = QAction('Настройка оповещения', self)
        note_run.triggered.connect(show_notification_window)

        note.addAction(note_run)


class MainWindowWidget(QWidget, UI_TableWindow):
    """
    contains select lesson menu and table
    """
    ready_draw_table = pyqtSignal()
    table_changed = pyqtSignal()
    start_sync = pyqtSignal()

    def __init__(self, program: IProgram, professor: Professor, parent=None):
        super().__init__(parent)

        self.program: IProgram = program
        self.professor = professor

        self.setupUi(self)

        self.last_lesson = None

        self.selector.set_up.emit(self.professor)
        self.selector.reader_required.connect(self.on_ok_message)

    @pyqtSlot('PyQt_PyObject', name='on_ok_message')
    def on_ok_message(self, text):
        QMessageBox().information(self, "!", text)

    def show_message(self, text, is_red):
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f'color: {"red" if is_red else "black"}')

    def switch_show_table_cross(self):
        self.table.switch_show_table_cross()
