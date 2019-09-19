import sys

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFormLayout, \
    QApplication, QMessageBox

from Client.MyQt.Widgets import QSeparator
from Client.MyQt.Widgets.LoadData.AbstractWizard import Step, AbstractLoadingWizard
from Client.MyQt.Widgets.LoadData.LessonsLoad import LessonLoadingWidget
from Client.MyQt.Widgets.LoadData.StepsWidget import QStepsWidget
from DataBase2 import Auth, Session, Professor, Lesson, UserType


class LoadingWizardWindow(QMainWindow):
    data_loaded = pyqtSignal()

    def __init__(self, professor, flags=None):
        super().__init__(flags)
        self.professor = professor

        self.loading_session = Session()

        self.setWindowTitle("Загрузка данных")
        self.setMinimumSize(900, 500)

        wizard_widget = LoadingWizardWidget(professor)
        wizard_widget.start_loader.connect(self.on_start_load)
        wizard_widget.start_loader.connect(print)
        self.setCentralWidget(wizard_widget)

    def on_start_load(self, class_):
        widget = WizardWidget(class_(self.professor, self.loading_session), self)
        widget.data_loaded.connect(self.data_loaded)
        widget.complete.connect(self.close)
        self.setCentralWidget(widget)


class WizardWidget(QWidget):
    data_loaded = pyqtSignal()
    complete = pyqtSignal()

    def __init__(self, wizard: AbstractLoadingWizard, parent=None):
        super().__init__(parent)

        self.wizard = wizard

        main_layout = QHBoxLayout()

        self.steps = QStepsWidget(self.wizard.steps)
        self.wizard.steps_changed.connect(self.steps.on_steps_changes)
        self.wizard.step.connect(self.steps.on_step)
        self.wizard.revoke_step.connect(self.steps.on_revoke_step)

        body_layout = QVBoxLayout()

        body_layout.addWidget(self.wizard)

        control_layout = QHBoxLayout()

        self.ok_button = QPushButton("Продолжить")
        self.ok_button.setEnabled(False)
        def submit():
            self.wizard.loading_session.commit()
            self.wizard.professor.session().expire_all()
            self.data_loaded.emit()
            self.complete.emit()
        self.ok_button.clicked.connect(submit)
        self.steps.completed.connect(lambda x: self.ok_button.setEnabled(x))
        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.clicked.connect(self.close)

        control_layout.addWidget(self.ok_button)
        control_layout.addWidget(self.cancel_button)

        body_layout.addLayout(control_layout)

        main_layout.addWidget(self.steps, stretch=1)
        main_layout.addWidget(QSeparator(Qt.Vertical))
        main_layout.addLayout(body_layout, stretch=3)

        self.setLayout(main_layout)

    def close(self):
        reply = QMessageBox().question(self, "Отмена", "Вы действительно хотите прервать загрузку?\n"
                                                       "Все данные вернутся к исходному состоянию (до процедуры загрузки)")
        if reply == QMessageBox.Yes:
            self.parent().close()


class LoadingWizardWidget(QWidget):
    start_loader = pyqtSignal('PyQt_PyObject')

    def __init__(self, professor, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.hello_label = QLabel("Привествуем в мастере загрузки данных из внешних источников.\n"
                                  "Выберите действие.")

        option_layout = QFormLayout()

        for child in AbstractLoadingWizard.__subclasses__():
            def starter(class_):
                def __starter__():
                    self.start_loader.emit(class_)
                return __starter__
            btn = QPushButton(child.label)
            option_layout.addRow(btn, QLabel(child.description))
            btn.clicked.connect(starter(child))

        main_layout.addWidget(self.hello_label)
        main_layout.addLayout(option_layout)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth = Auth.get_or_create(login='VAE', password='123456', user_id=1, user_type_id=UserType.PROFESSOR)
    professor = Professor.get_or_create(id=1)

    w = LoadingWizardWindow(professor=auth.user)

    w.show()

    sys.exit(app.exec_())
