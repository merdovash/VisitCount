from contextlib import suppress
from datetime import datetime
from typing import List, Dict

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QTabWidget, \
    QMessageBox, QDateTimeEdit

from Client.MyQt.Widgets import QSeparator
from Client.MyQt.Widgets.LoadData.AbstractWizard import Step, AbstractLoadingWizard
from Client.MyQt.Widgets.Network.BisitorRequest import BisitorRequest
from Client.MyQt.Widgets.Table.NewItemsTable import QNewItemsTable
from Client.MyQt.interface import IAcceptDrop, ISelectFile
from DataBase2 import Group, Student
from Domain.Date import semester_start
from Domain.Loader.GroupLoader.GroupLoader import GroupLoader
from Domain.Loader.LessonLoader import LessonLoader
from Modules.API import GroupApi


class LessonLoadingWidget(AbstractLoadingWizard, IAcceptDrop, ISelectFile):
    steps = [
        Step('Выбрать дату начала семестра', ''),
        Step('Загрузить файл с расписанием', 'требуется загрузить файл с распсианием занятий', False),
        Step('Загрузить данные для всех групп', '', False)
    ]

    group_steps: Dict[str, Step]

    def setupUi(self):
        main_layout = QVBoxLayout()

        date_input_layout = QHBoxLayout()

        self.select_date_label = QLabel("Выберите дату начала семестра")
        self.date_input = QDateTimeEdit(semester_start().date())
        self.date_input.setCalendarPopup(True)
        self.accept_date_button = QPushButton("Подтвердить")

        date_input_layout.addWidget(self.select_date_label)
        date_input_layout.addWidget(self.date_input, stretch=9)
        date_input_layout.addWidget(self.accept_date_button)

        self.hello_message = QLabel("Выберите файл с расписанием или перетащите его в окно.")

        self.select_button = QPushButton("Выбрать")

        main_layout.addLayout(date_input_layout)
        main_layout.addWidget(self.hello_message, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        main_layout.addWidget(self.select_button, alignment=Qt.AlignHCenter | Qt.AlignTop)

        self.setLayout(main_layout)

    def __init__(self, professor, loading_session, parent=None):
        QWidget.__init__(self, parent)
        IAcceptDrop.__init__(self)
        ISelectFile.__init__(self)

        self.professor = professor
        self.session = professor.session()
        self.loading_session = loading_session

        self.setupUi()

        def change_date():
            self.date_input.setEnabled(True)
            self.revoke_step.emit(self.steps[0])
            self.accept_date_button.setText("Подтвердить")
            self.accept_date_button.clicked.connect(accept_date)
            with suppress(TypeError):
                self.accept_date_button.clicked.disconnect(change_date)

            self.select_button.setEnabled(False)
            self.select_button.setToolTip("Укажите дату начала семестра")

        def accept_date():
            self.date_input.setEnabled(False)
            self.step.emit(self.steps[0])
            self.accept_date_button.setText("Изменить")
            self.accept_date_button.clicked.connect(change_date)
            self.accept_date_button.clicked.disconnect(accept_date)

            self.select_button.setEnabled(True)
            self.select_button.setToolTip("Выберите файл с расписанием занятий")

        self.accept_date_button.clicked.connect(accept_date)

        self.select_button.clicked.connect(lambda: self.select_file.emit(self.read_file))
        self.drop.connect(self.on_drop)

        self.requested = False

        self.group_steps: Dict[Group, Step] = dict()

        change_date()

    def on_drop(self, files):
        if not self.date_input.isEnabled():
            for file in files:
                self.read_file(file)
        else:
            QMessageBox().information(self, "", "Сначала укажите дату начала семестра.")

    def read_file(self, file: QUrl):
        self.worker = LessonLoader.auto(
            file=file.path(),
            start_day=datetime(self.date_input.date().year(), self.date_input.date().month(),
                               self.date_input.date().day()),
            professor=self.professor,
            session=self.loading_session
        )

        main_layout = self.layout()
        main_layout.removeWidget(self.hello_message)
        main_layout.removeWidget(self.select_button)
        self.hello_message.deleteLater()
        self.select_button.deleteLater()

        self.info_message = QLabel("Предоставте необходимые данные для завершения загрузки")

        data_layout = QHBoxLayout()

        discipline_layout = QVBoxLayout()

        self.discipline_title = QLabel("Обнаружены следующие дисциплины")
        self.discipline_list = QNewItemsTable(self.session, self.loading_session)
        for discipline in self.worker.get_disciplines():
            self.discipline_list.addItem(discipline)

        discipline_layout.addWidget(self.discipline_title)
        discipline_layout.addWidget(self.discipline_list)

        group_layout = QVBoxLayout()

        self.group_title = QLabel("Обнаружены следующие группы")
        self.group_list = QNewItemsTable(self.session, self.loading_session)
        self.steps = self.steps[:-1]

        for group in self.worker.get_groups():
            self.group_list.addItem(group)

            group_step = Step(f'Загрузить данные группы {group.name}', '')
            self.group_steps[group.name]: Dict[str, Step] = group_step
            self.steps.append(group_step)

        self.steps_changed.emit(self.steps)

        student_layout = QHBoxLayout()

        control_student_layout = QVBoxLayout()

        self.description_label = QLabel("Необходимо загрузить информацию о группах.")
        self.server_load_button = QPushButton("Загрузить с сервера")
        self.server_load_button.clicked.connect(self.request_students)
        self.client_load_button = QPushButton("Выбрать файл")
        self.client_load_button.clicked.connect(lambda x: self.select_file.emit(self.load_group))

        list_student_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.students_lists: Dict[Group, QListWidget] = dict()
        for group in self.worker.get_groups():
            list_widget = QNewItemsTable(self.session, self.loading_session)
            self.students_lists[group] = list_widget
            self.tabs.addTab(list_widget, group.name)

        for group in self.worker.get_groups():
            if len(group.students):
                self._apply_group(group_name=group.name, students=group.students)
                self.step.emit(self.group_steps[group.name])

        list_student_layout.addWidget(QLabel("Списки групп"))
        list_student_layout.addWidget(self.tabs)

        control_student_layout.addWidget(self.description_label)
        control_student_layout.addWidget(self.server_load_button)
        control_student_layout.addWidget(self.client_load_button)

        student_layout.addLayout(control_student_layout)
        student_layout.addLayout(list_student_layout)

        group_layout.addWidget(self.group_title)
        group_layout.addWidget(self.group_list)

        data_layout.addLayout(discipline_layout)
        data_layout.addLayout(group_layout)

        main_layout.addLayout(data_layout, stretch=1)
        main_layout.addWidget(QSeparator(Qt.Horizontal))
        main_layout.addLayout(student_layout, stretch=10)

        self.step.emit(self.steps[1])

    def check_groups(self, groups: List[Group]):
        for index, group in enumerate(groups):
            existing_group = self.session.query(Group).filter(Group.name == group.name).first()
            if existing_group is not None:
                students = Student.of(existing_group)
                if len(students) > 0:
                    self._apply_group(existing_group.name, existing_group.students)

    def load_group(self, file: QUrl):
        group_loader = GroupLoader.auto(file=file.path(), professor=self.professor, session=self.loading_session)

        group = group_loader.get_group()
        self._apply_group(group.name, group_loader.get_students_list())

    def _apply_group(self, group_name: str, students: List[Student]):
        group: Group = list(filter(lambda x: x.name == group_name, self.students_lists.keys()))[0]
        list_widget = self.students_lists[group]
        list_widget.clear()
        for student in students:
            self.loading_session.add(student)
            list_widget.addItem(student)

        self.loading_session.flush()
        self.step.emit(self.group_steps[group.name])

    def request_students(self):
        def apply_response(group: GroupApi.GroupResponse):
            self._apply_group(
                group_name=group.name,
                students=group.students
            )

        if not self.requested:
            self.managers = list()
            for group in self.students_lists.keys():
                self.managers.append(
                    BisitorRequest(
                        address='http://localhost:5000/api/group',
                        user=self.professor,
                        data={'name': group.name},
                        callback=apply_response
                    )
                )

            self.requested = True
        else:
            QMessageBox().information(self, "", "Вы уже запросили информацию с сервера.")
