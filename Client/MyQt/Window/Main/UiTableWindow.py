from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QAction, QMenu, QMainWindow

from Client.MyQt.Chart.QAnalysisDialog import show
from Client.MyQt.Chart.WeekAnalysis import WeekChart
from Client.MyQt.Chart.WeekDayAnalysis import WeekDayChart
from Client.MyQt.QAction.DataAction import DataAction
from Client.MyQt.QAction.RegisterProfessorCard import RegisterProfessorCard
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Table import VisitTable
from Client.MyQt.Window.Main import Selector
from Client.MyQt.Window.NotificationParam import NotificationWindow
from Client.Types import valid_card
from DataBase2.Types import format_name
from Modules.Synchronize.ClientSide import Synchronize


class Ui_TableWindow(object):
    def setupUi(self, TableWindow: QMainWindow):
        self.main_layout = QVBoxLayout()
        TableWindow.setLayout(self.main_layout)
        TableWindow.layou

        # INFO BLOCK
        self.info_layout = QHBoxLayout()

        self.professor_label = QLabel(format_name(TableWindow.professor))
        self.professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage()

        self.info_layout.addWidget(self.professor_label, alignment=Qt.AlignLeft)
        self.info_layout.addWidget(self.info_label, alignment=Qt.AlignRight)

        self.main_layout.addLayout(self.info_layout)

        # SELECTOR BLOCK
        self.selector = Selector(TableWindow.program)

        self.main_layout.addWidget(self.selector)

        # DATA BLOCK
        self.table = VisitTable(self.main_layout, TableWindow.program)

        TableWindow.setLayout(self.main_layout)

        self.showMaximized()

    def __init_menu__(self, TableWindow):
        menu_bar = TableWindow.menuBar()

        self.menu_bar = menu_bar

        self._init_menu_file(TableWindow)
        self._init_menu_analysis(TableWindow)
        self._init_menu_view()
        self._init_menu_lessons(TableWindow)
        self._init_menu_updates(TableWindow)
        self._init_notification(TableWindow)

    def _init_menu_analysis(self, TableWindow):
        analysis = TableWindow.menu_bar.addMenu("Анализ")

        analysis_weeks = QAction("По неделям", self)
        analysis_weeks.triggered.connect(show(WeekChart, TableWindow.program))

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(show(WeekDayChart, TableWindow.program))

        analysis.addAction(analysis_week_days)

    def _init_menu_lessons(self, TableWindow):
        lessons = TableWindow.menu_bar.addMenu("Занятия")

        lessons_current = QAction("Выбрать ближайщее занятие", self)
        lessons_current.triggered.connect(self.selector.select_current_lesson)

        lessons_current_for_group = QAction(
            "Выбрать ближайщее занятие для выбранной группы", self)
        lessons_current_for_group.triggered.connect(self.selector.select_current_group_current_lesson)

        lessons.addAction(lessons_current)
        lessons.addAction(lessons_current_for_group)

    def _init_menu_file(self, TableWindow):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(lambda: TableWindow.program.change_user())

        file.addAction(file_change_user)

        if TableWindow.program.professor is not None:
            if not valid_card(TableWindow.program.professor.card_id):
                file.addAction(RegisterProfessorCard(TableWindow.program, TableWindow))

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(TableWindow.close)

        file.addAction(file_exit)

    def _init_menu_view(self):
        view: QMenu = self.menu_bar.addMenu("Вид")

        data = QMenu('Заголовок таблицы', self)
        view.addMenu(data)

        data_show_month_day = DataAction(
            ["Отображать день", "Не отображать день"],
            VisitTable.Header.DAY,
            self
        )
        data.addAction(data_show_month_day)

        data.addAction(
            DataAction(
                ["Отображать день недели", "Не отображать день недели"],
                VisitTable.Header.WEEKDAY,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать месяц", "Не отображать месяц"],
                VisitTable.Header.MONTH,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать номер занятия", "Не отображать номер занятия"],
                VisitTable.Header.LESSON,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать тип занятия", "Не отображать тип занятия"],
                VisitTable.Header.LESSONTYPE,
                self
            )
        )

        data.addAction(
            DataAction(
                ["Отображать номер недели", "Не отображать номер недели"],
                VisitTable.Header.WEEK_NUMBER,
                self
            )
        )

        view.addSeparator()
        view.addAction('Отображать перекрестие в таблице', self.table)

    def _init_menu_updates(self, TableWindow):
        updates = self.menu_bar.addMenu("Синхронизация")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(Synchronize(TableWindow.program).start)

        updates.addAction(updates_action)

    def _init_notification(self, TableWindow):
        note = self.menu_bar.addMenu('Оповещения')

        note_run = QAction('Настройка оповещения', self)
        note_run.triggered.connect(
            NotificationWindow(TableWindow.professor, self).exec)

        note.addAction(note_run)
