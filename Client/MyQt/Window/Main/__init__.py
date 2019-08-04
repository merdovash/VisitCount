"""
This module contains main Window with tables

TODO:
    * fix error on relogin after changing user
"""
import datetime
from typing import List

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDropEvent, QFont
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QStatusBar, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, \
    QApplication

from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Widgets.LoadData import LoadingWizardWindow
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.Widgets.Selector import Selector
from Client.MyQt.Widgets.VisualData.Graph.BisitorMPLWidget import BisitorMPLWidget
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.ContactManager import QContactManagerWindow
from Client.MyQt.Window.ExcelLoadingWindow import ExcelLoadingWidget
from Client.Reader.Functor.RegisterCardProcess import RegisterCardProcess
from DataBase2 import Professor, Lesson
from Parser import Args

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
    refresh_data = pyqtSignal()

    def __init__(self, professor: Professor, **kwargs):
        AbstractWindow.__init__(self, **kwargs)

        self.professor = professor

        self.central_widget = MainWindowWidget(
            professor=professor,
            parent=self)
        self.refresh_data.connect(self.central_widget.on_refresh_data)

        self.setCentralWidget(self.central_widget)

        self.__init_menu__()

        self.showMaximized()

        self.setAcceptDrops(True)

        self.setStatusBar(QStatusBar(self))

        self.log_out.connect(self._quit_to_auth)

    @pyqtSlot(name="_quit_to_auth")
    def _quit_to_auth(self):
        from Client.MyQt.Window.Auth import AuthWindow

        self.auth = AuthWindow()
        self.auth.show()

        self.close()
        QApplication.processEvents()

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

            if Args().test:
                dialog = ExcelLoadingWidget(files=event.mimeData().urls())
                dialog.show()

        else:
            event.ignore()

    def __init_menu__(self):
        menu_bar = self.menuBar()

        self.menu_bar = menu_bar

        self._init_menu_file()
        self._init_menu_analysis()
        self._init_menu_view()
        self._init_menu_lessons()
        self._init_menu_updates()

    def _init_menu_analysis(self):
        def show():
            if not hasattr(self, 'visual') or self.visual is None:
                self.visual = BisitorMPLWidget(self.professor)
            self.visual.showMaximized()

        analysis = self.menu_bar.addMenu("Анализ")

        analysis.addAction("Просмотр", show)

    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

    def _init_menu_file(self):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(self._quit_to_auth)

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
        switch_color_rate_action = QAction('Выделять цветом итог студентов', self)
        switch_color_rate_action.setCheckable(True)
        switch_color_rate_action.setToolTip("Выделяет зелёным цветом студентов, пропустивших 3 или меньше занятия.\n "
                                            "Выделяет красным цветом студентов, посетивших меньше половины занятий.")
        switch_color_rate_action.triggered.connect(self.centralWidget().view_show_color_rate)
        view.addAction(switch_color_rate_action)

    def _init_menu_updates(self):
        def update_db_action():
            self.update_action_dialog = SendUpdatesWidget(self.professor)
            self.update_action_dialog.show()

        def show_loader_widget():
            self.loader_Widget = LoadingWizardWindow(self.professor)
            self.loader_Widget.data_loaded.connect(self.refresh_data)
            self.loader_Widget.show()

        def show_contact_manager_widget():
            self.contact_manager_widget = QContactManagerWindow(self.professor)
            self.contact_manager_widget.show()

        updates = self.menu_bar.addMenu("Данные")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(update_db_action)

        load_new_action = QAction("Загрузить данные", self)
        load_new_action.triggered.connect(show_loader_widget)

        contact_manager_action = QAction('Настройки рассылки', self)
        contact_manager_action.triggered.connect(show_contact_manager_widget)

        updates.addAction(updates_action)
        updates.addAction(load_new_action)
        updates.addAction(contact_manager_action)


class MainWindowWidget(QWidget):
    """
    contains select lesson menu and table
    """
    ready_draw_table = pyqtSignal()
    table_changed = pyqtSignal()
    start_sync = pyqtSignal()

    view_show_color_rate = pyqtSignal(bool)

    def __init__(self, professor: Professor, parent=None):
        super().__init__(parent)
        with open('Client/src/style.qss', 'r') as style_file:
            self.setStyleSheet(style_file.read())

        self.professor = professor

        layout = QVBoxLayout(self)

        info_layout = QHBoxLayout()

        professor_label = QLabel(
            professor.full_name()
        )
        professor_label.setFont(QFont('Calibri', 16))

        self.info_label = QStatusMessage()

        info_layout.addWidget(professor_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.info_label, alignment=Qt.AlignRight)

        layout.addLayout(info_layout, stretch=1)

        self.selector = Selector(professor)

        layout.addWidget(self.selector, stretch=9999)

        self.setLayout(layout)

        self.last_lesson = None

        self.selector.set_up.emit(self.professor)
        self.selector.reader_required.connect(self.on_ok_message)
        self.view_show_color_rate.connect(self.selector.view_show_color_rate)

    @pyqtSlot(name='on_refresh_data')
    def on_refresh_data(self):
        self.selector.set_up.emit(self.professor)

    @pyqtSlot('PyQt_PyObject', name='on_ok_message')
    def on_ok_message(self, text):
        QMessageBox().information(self, "!", text)

    def show_message(self, text, is_red):
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f'color: {"red" if is_red else "black"}')

    def switch_show_table_cross(self):
        self.table.switch_show_table_cross()
