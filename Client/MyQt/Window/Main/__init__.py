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
from Client.MyQt.QAction.RegisterProfessorCard import RegisterProfessorCard
from Client.MyQt.Widgets.Chart.QAnalysisDialog import QAnalysisDialog
from Client.MyQt.Widgets.Network.Request import send_updates
from Client.MyQt.Widgets.Table import VisitTable
from Client.MyQt.Window import AbstractWindow, IParentWindow
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

    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - x.date))
    return closest


class MainWindow(AbstractWindow, IParentWindow):
    """
    class represents main window in program. includes table, control elements, status info, professor data.
    """

    def __init__(self, program: IProgram, professor: Professor):
        AbstractWindow.__init__(self)
        IParentWindow.__init__(self)

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

        def show(data: Callable[[], Data]):
            def _show():
                d = QAnalysisDialog(
                    data(),
                    selector={'группы': Group.of(self.professor), 'дисциплины': Discipline.of(self.professor)})
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
                    .group_by(lambda x: x.lesson.week)
            )
        )

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(
            show(
                lambda: Data(professor=self.professor)
                    .filter(lambda x: x.lesson.semester == semester)
                    .group_by(group_by=lambda x: x.lesson.date.weekday())
            )
        )

        analysis.addAction(analysis_week_days)

    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

        lessons_current = QAction("Выбрать ближайщее занятие", self)
        lessons_current.triggered.connect(
            self.centralWidget().selector.select_current_lesson)

        lessons_current_for_group = QAction(
            "Выбрать ближайщее занятие для выбранной группы", self)
        lessons_current_for_group.triggered.connect(
            self.centralWidget().selector.select_current_group_current_lesson)

        lessons.addAction(lessons_current)
        lessons.addAction(lessons_current_for_group)

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
            self.update_action_dialog = send_updates(self.program)
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

        self.selector.start()

    # slots
    @pyqtSlot(name='run_synchronization')
    def run_synchronization(self):
        """
        Slot!
        Runs synchronization process
        """

        NetAction.send_updates(
            self.program.auth.login,
            self.program.auth.password,
            self.program.host,
            self.professor.id,
            self.program.session)
        pass

    def getControl(self):
        return self.control

    def set_current_lesson(self, lesson=None):
        """
        Select a lesson close to the current time.
        """
        if lesson is None:
            lessons = self.professor.lessons
            closest = closest_lesson(lessons)
            # self.lesson_selector.setCurrentId(getLessonIndex(self.lesson_selector.items, closest))
            self.selector.select_current_lesson(closest)
        else:
            self.selector.select_current_lesson(lesson)

    def set_current_lesson_of_current_group(self):
        """
        Select a lesson close to the current time for the currently selected group.
        """
        lessons = Lesson.filter(professor=self.professor,
                                discipline=self.selector.discipline.current(),
                                group=self.selector.group.current())
        closest = closest_lesson(lessons)
        self.lesson.setCurrent(closest['id'])

    def show_message(self, text, is_red):
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f'color: {"red" if is_red else "black"}')

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name="mark_current_lesson")
    def mark_current_lesson(self, column, last_lesson=None):
        assert 0 <= column, f'wrong columns number: columns={column}'
        self.table.visit_table.scrollTo(
            self.table.visit_table.model().index(1, column))

        table: VisitTable = self.table

        if last_lesson is not None and last_lesson > -1:
            for item in table.get_column(last_lesson):
                item.set_current_lesson(False)

        for item in table.get_column(column):
            item.set_current_lesson(True)

    @pyqtSlot('PyQt_PyObject', name='_start_lesson')
    def _start_lesson(self, lesson):
        try:
            self.program.reader().on_read(self._new_visit)

            Action.start_lesson(lesson, self.professor)

            self.program.window.message.emit("Учет начался. Приложите карту студента к считывателю.", True)
        except:
            self.program.window.error.emit("Для учета посещений необходимо подключение считывателя.")

    @pyqtSlot(name='_end_lesson')
    def _end_lesson(self):
        if self.program.reader() is not None:
            self.program.reader().stop_read()
        else:
            self.program.window.error.emit(
                'Во время учета было потеряно соединение со считывателем. Учет завершен.')

    def _new_visit(self, card_id):
        current_data = self.selector.get_current_data()

        student = find(lambda student: student.card_id == card_id, self.students)

        if student is None:
            self.program.window.message.emit("Студента нет в списке.", False)
        else:
            lesson = current_data.lesson

            Action.new_visitation(student, lesson, self.professor.id)

            self.table.new_visit(student, lesson)

    def switch_show_table_cross(self):
        self.table.switch_show_table_cross()

    def hasDialog(self):
        return


if __name__ == '__main__':
    def d(a, b, c):
        print(a+b+c)

    d(4,5,6)
    d(b=4, c=7, a=3)
