"""
This module contains main Window with tables

TODO:
    * fix error on relogin after changing user
"""
import datetime
from typing import List, Callable

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QStatusBar

from Client.IProgram import IProgram
from Client.MyQt.Dialogs.QOkMsg import QOkMsg
from Client.MyQt.QAction.RegisterProfessorCard import RegisterProfessorCard
from Client.MyQt.Widgets.Chart.QAnalysisDialog import QAnalysisDialog, PlotType
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.ExcelLoadingWindow import ExcelLoadingWidget
from Client.MyQt.Window.Main.UiTableWindow import UI_TableWindow
from Client.MyQt.Window.NotificationParam import NotificationWindow
from DataBase2 import Professor, Lesson, Group, Discipline
from Domain import Action
from Domain.Action import NetAction
from Domain.Data import valid_card
from Domain.Date import BisitorDateTime
from Domain.Structures import Data
from Domain.functools.List import find

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

    def __init__(self, program: IProgram, professor: Professor):
        AbstractWindow.__init__(self)

        self.program: IProgram = program

        self.professor = professor
        if str(professor.id) not in program.win_config:
            program.win_config.new_user(professor.id)
            program.win_config.set_professor_id(professor.id)

        self.central_widget = MainWindowWidget(
            program=program,
            professor=professor,
            parent=self)

        self.setCentralWidget(self.central_widget)

        self.__init_menu__()

        self.showMaximized()

        self.setAcceptDrops(True)

        self.setStatusBar(QStatusBar(self))

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
        print(event)
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
                print('drop dialog')
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
        self.analysis = []

        def show(data: Callable[[], Data], type):
            def _show():
                d = QAnalysisDialog(
                    data(),
                    selector={'группы': Group.of(self.professor), 'дисциплины': Discipline.of(self.professor)},
                    plot_styler=type)
                self.analysis.append(d)

                d.show()

            return _show

        analysis = self.menu_bar.addMenu("Анализ")

        analysis_weeks = QAction("По неделям", self)
        semester = BisitorDateTime.now().semester
        analysis_weeks.triggered.connect(
            show(
                lambda: Data(professor=self.professor)
                    .filter(lambda x: x.lesson.semester == semester)
                    .group_by(lambda x: x.lesson.week),
                PlotType.WEEK
            )
        )

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(
            show(
                lambda: Data(professor=self.professor)
                    .filter(lambda x: x.lesson.semester == semester)
                    .group_by(group_by=lambda x: x.lesson.date.weekday()),
                PlotType.WEEKDAY
            )
        )

        analysis.addAction(analysis_week_days)

    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

    def _init_menu_file(self):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(lambda: self.program.change_user())

        file.addAction(file_change_user)

        if self.program.professor is not None:
            if not valid_card(self.program.professor):
                file.addAction(RegisterProfessorCard(self.program, self))

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

        updates = self.menu_bar.addMenu("Синхронизация")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(update_db_action)

        updates.addAction(updates_action)

    def _init_notification(self):
        note = self.menu_bar.addMenu('Оповещения')

        note_run = QAction('Настройка оповещения', self)
        note_run.triggered.connect(
            lambda:
            self.setDialog(NotificationWindow.instance(self.program))
        )

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
        QOkMsg(text).exec_()

    def show_message(self, text, is_red):
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f'color: {"red" if is_red else "black"}')

    def switch_show_table_cross(self):
        self.table.switch_show_table_cross()


if __name__ == '__main__':
    def d(a, b, c):
        print(a + b + c)


    d(4, 5, 6)
    d(b=4, c=7, a=3)
