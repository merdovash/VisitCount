from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QMessageBox

from Client.MyQt.Widgets import BisitorWidget
from Client.MyQt.Widgets.ComboBox import QMComboBox
from Client.MyQt.Widgets.Navigation import QAccentCancelButtons
from Client.MyQt.Widgets.QAttachFile import QAttachFile
from DataBase2 import VisitationLossReason, Student, Lesson, name, LossReason
from Domain.FileManager import writeTempFile
from Domain.MessageFormat import inflect


class QAddLossReason(BisitorWidget):
    def __init__(self, lesson: Lesson, student: Student):
        super().__init__()
        self.lesson = lesson
        self.student = student
        self.remove_file_on_close: List[Path] = []

        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(450, 250)

        self.r = VisitationLossReason.get(lesson.session(), lesson_id=lesson.id, student_id=student.id)

        self.grid = QGridLayout()

        self.setWindowTitle("Добавить причину пропуска")

        self.grid.addWidget(QLabel('Студент'), 0, 0, 1, 2)
        student_name_label = QLabel(student.short_name())
        student_name_label.setObjectName('InfoLabel')
        self.grid.addWidget(student_name_label, 0, 2, 1, 2)

        self.grid.addWidget(QLabel('Занятие'), 1, 0, 1, 2)
        lesson_name_label = QLabel(name(lesson))
        lesson_name_label.setObjectName('InfoLabel')
        self.grid.addWidget(lesson_name_label, 1, 2, 1, 2)

        self.reason = QMComboBox(LossReason)
        self.grid.addWidget(QLabel('Причина'), 2, 0, 1, 2)
        self.grid.addWidget(self.reason, 2, 2, 1, 2)

        self.file_attach = QAttachFile('rb', ('pdf', 'docx', 'img'))
        self.grid.addWidget(self.file_attach, 3, 0, 2, 4)

        self.grid.addWidget(QAccentCancelButtons(self._accept, self.close), 5, 0, 1, 4)

        self.setLayout(self.grid)

        if self.r is not None:
            self.reason.setCurrent(self.r.reason)
            if self.r.file is not None:
                file_path = writeTempFile(self.r.file, self.r.file_ext)
                self.file_attach.set_file(file_path)
                self.remove_file_on_close.append(file_path)

    def _accept(self):
        file = self.file_attach.get_file()
        if self.r is None:
            res = QMessageBox().question(
                self,
                "Подтвердите действие",
                f"Будет добавлена запись для {self.student.short_name()} о пропуске занятия " +
                f"из-за {inflect(self.reason.current().value, {'gent'})} " +
                (f"без подтверждения" if file is None else f"с подтверждением")
            )

            if res == QMessageBox.Yes:
                self.r = VisitationLossReason(
                    lesson_id=self.lesson.id,
                    student_id=self.student.id,
                    reason=self.reason.current())
                if file is not None:
                    self.r.set_file(self.file_attach.get_path())

                self.lesson.session().add(self.r)

                self.r.session().commit()

                QMessageBox().information(self, "Успешно добавлено", "Успешно добавлена информация о пропуске")
                self.close()
        else:
            msg = f"В записи для {self.student.short_name()} о пропуске занятия будет изменено"
            changed = False
            if self.reason.current() != self.r.reason:
                msg += f'\n Причина: с {self.r.reason} на {self.reason.current()}'
                changed = True
            if file != self.r.file:
                if self.r.file is None:
                    msg += f'\n Добавлен файл подтверждения'
                else:
                    msg += f'\n Выбран другой файл'
                changed = True

            if changed:
                res = QMessageBox().question(
                    self,
                    "Подтвердите изменения",
                    msg
                )

                if res:
                    self.r.reason = self.reason.current()
                    self.r.set_file(self.file_attach.get_path())
                    self.r.session().commit()
                    QMessageBox().information(self, "Успешно изменено", "Успешно изменена информация о пропуске")
                    self.close()
            else:
                self.close()

    def close(self):
        for file_path in self.remove_file_on_close:
            file_path.unlink()

        super().close()
