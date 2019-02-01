from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class QRequestUncompleteLesson(QWidget):
    delete_all = pyqtSignal()
    save_all = pyqtSignal()
    cancel = pyqtSignal()

    def __init__(self, lesson, parent=None):
        super().__init__(parent)

        self.lesson = lesson

        self.setWindowTitle("Отмена проведения занятия")
        self.setWindowModality(Qt.ApplicationModal)

        self.label = QLabel("Вы собираетесь отменить проведение занятия.\n"
                            f"дата занятия: {lesson.date}\n"
                            "Выберите как поступить с посещениями этого занятия.")

        self.option_1_description = QLabel("Все посещения будут удалены.\n"
                                           "Когда вы начнете это занятие, в нем не будет посещений.")
        self.option_1_button = QPushButton("Удалить посещения")

        self.option_2_description = QLabel("Сохранить посещения.\n"
                                           "Когда вы снова запустите это занятия в нем будут отмечены\n"
                                           "имеющиеся на данный момент посещения.\n"
                                           "Пока оно не проведено - эти посещения не будут влиять\nна общую статистику.")
        self.option_2_button = QPushButton("Оставить посещения")

        self.option_3_description = QLabel("Прервать отмену проведения занятия.\n"
                                           "Занятие останется проведенным, все посещения будут нетронуты.")
        self.option_3_button = QPushButton("Отмена")

        main_layout = QVBoxLayout()

        options_layout = QHBoxLayout()

        option_1_layout = QVBoxLayout()
        option_1_layout.addWidget(self.option_1_description)
        option_1_layout.addWidget(self.option_1_button)

        option_2_layout = QVBoxLayout()
        option_2_layout.addWidget(self.option_2_description)
        option_2_layout.addWidget(self.option_2_button)

        option_3_layout = QVBoxLayout()
        option_3_layout.addWidget(self.option_3_description)
        option_3_layout.addWidget(self.option_3_button)

        options_layout.addLayout(option_1_layout)
        options_layout.addLayout(option_2_layout)
        options_layout.addLayout(option_3_layout)

        main_layout.addWidget(self.label, 1, alignment=Qt.AlignHCenter)
        main_layout.addLayout(options_layout, 10)

        self.setLayout(main_layout)

        self.option_1_button.clicked.connect(self.delete_all)
        self.option_1_button.clicked.connect(self.close)

        self.option_2_button.clicked.connect(self.save_all)
        self.option_2_button.clicked.connect(self.close)

        self.option_3_button.clicked.connect(self.cancel)
        self.option_3_button.clicked.connect(self.close)
