import sys
from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QApplication

from Client.MyQt.Widgets.ComboBox import QMComboBox
from Client.MyQt.Widgets.ComboBox.QMSelector import QMSelector
from Client.MyQt.Widgets.LoadData import AbstractLoadingWizard, Step, LoadingWizardWindow
from DataBase2 import Lesson, Professor, Group, Discipline
from Domain.Loader.VisitationLoader import VisitationExcelLoader


class VisitationLoadingWidget(AbstractLoadingWizard):
    label = "Загрузить посещения"
    description = "Открывает интерфейс загрузки посещений из .xls или .xlsx документа"
    steps = (Step('Выбрать группу', ''),
             Step('Выбрать дисциплину', ''),
             Step('Выбрать файл', ''),
             Step('Запустить чтение', ''))

    def __init__(self, professor, session, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        main_layout = QVBoxLayout()
        group = QMComboBox(Group)
        discipline = QMComboBox(Discipline)

        main_layout.addWidget(QMSelector([discipline, group], professor), alignment=Qt.AlignTop)

        def on_group_select(lessons: List[Lesson], group):
            self.first_lesson = sorted(lessons, key=lambda lesson: lesson.date)[0]
            self.revoke_step.emit(self.steps[2])
            self.file_name = None
            start_button.setEnabled(False)

        group.current_changed.connect(on_group_select)
        group.current_changed.connect(lambda x, y: self.step.emit(self.steps[0]))
        discipline.current_changed.connect(lambda x, y: self.step.emit(self.steps[1]))

        button = QPushButton('Выбрать файл')
        def on_button_click():
            file, status = QFileDialog().getOpenFileName(self, 'Выберите файл', '', 'Sheet (*.xls *.xlsx)')
            if status:
                self.file_name = file
                self.step.emit(self.steps[2])
                start_button.setEnabled(True)
                start_button.setText(f'Считать из файла {Path(file).name}')
        button.clicked.connect(on_button_click)

        def start():
            self.reader = VisitationExcelLoader(
                file_name=self.file_name,
                group=list(group.current()),
                discipline=discipline.current(),
                session=session)
        start_button = QPushButton('Считать из файла')
        start_button.setEnabled(False)
        start_button.clicked.connect(start)

        main_layout.addWidget(button, alignment=Qt.AlignHCenter|Qt.AlignVCenter)
        main_layout.addWidget(start_button, alignment=Qt.AlignHCenter|Qt.AlignTop)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = LoadingWizardWindow(Professor.get(id=1))

    w.show()

    sys.exit(app.exec_())

