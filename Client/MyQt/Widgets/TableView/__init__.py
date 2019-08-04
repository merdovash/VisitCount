import sys

from PyQt5.QtCore import QRect, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QWidget, \
    QMessageBox

from Client.MyQt.Widgets.TableView.Model import PercentHorizontalModel, PercentVerticalModel, VisitModel
from Client.MyQt.Widgets.TableView.View import VisitView, PercentView, PercentHorizontalView
from DataBase2 import Lesson, Auth, Student, Group, Visitation
from Domain.functools.Format import agree_to_number, agree_to_gender
from Domain.functools.Format import format_name

COLUMN_WIDTH = 48
ROW_HEIGHT = 20
HEADER_HEIGHT = 65
SCROLL_BAR_SIZE = 20


class VisitTableWidget(QWidget):
    set_current_lesson = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    select_current_lesson = pyqtSignal('PyQt_PyObject')
    new_visit = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    lesson_start = pyqtSignal('PyQt_PyObject')
    lesson_finish = pyqtSignal()

    view_show_color_rate = pyqtSignal(bool)  # управляет цветовой подсветкой результатов студентов

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        lesson.completed = True
        lesson.session().commit()

    @pyqtSlot(name='on_lesson_stop')
    def on_lesson_stop(self):
        pass

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.view = VisitView(self)
        self.view.show()

        self.percent_vertical_view = PercentView(self)
        self.percent_vertical_view.show()

        self.percent_horizontal_view = PercentHorizontalView(self)
        self.percent_horizontal_view.show()

        self.percent_horizontal_view.horizontalScrollBar().valueChanged.connect(
            self.view.horizontalScrollBar().setValue)
        self.percent_vertical_view.verticalScrollBar().valueChanged.connect(self.view.verticalScrollBar().setValue)
        self.view.horizontalScrollBar().valueChanged.connect(
            self.percent_horizontal_view.horizontalScrollBar().setValue)
        self.view.verticalScrollBar().valueChanged.connect(self.percent_vertical_view.verticalScrollBar().setValue)

        self.view.select_current_lesson.connect(self.select_current_lesson)
        self.set_current_lesson.connect(self.view.set_current_lesson)

        self.view.show_student_card_id.connect(
            lambda x:
            QMessageBox().information(
                self,
                "Информация",
                f'Карта студента {format_name(x, {"gent"})}:\n'
                f'{"не зарегистрирована" if x.card_id is None else x.card_id}')
        )

        def student_summary(student, professor, discipline):
            lessons = list(filter(lambda x: x.completed, Lesson.intersect(professor, discipline, student)))
            visitation = Visitation.journal(student, lessons)
            QMessageBox().information(
                self,
                "Информация",
                f'Студент {student.full_name()} {agree_to_gender("посетил", student.full_name())} '
                f'{len(visitation)} из {len(lessons)} {agree_to_number("занятий", len(lessons))} '
                f'({round(len(visitation)/len(lessons)*100 if len(visitation) else 0)})'
                + (' превысив допустимое количество пропусков.' if len(visitation)<len(lessons)-3 else '.')
            )
        self.view.show_student_summary.connect(student_summary)

        self.lesson_start.connect(self.on_lesson_start)
        self.lesson_start.connect(self.view.lesson_start)
        self.lesson_finish.connect(self.view.lesson_finish)
        self.lesson_finish.connect(self.on_lesson_stop)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        rect: QRect = self.contentsRect()
        self.view.setGeometry(
            rect.left(),
            rect.top(),
            rect.width() - COLUMN_WIDTH * 2 - SCROLL_BAR_SIZE,
            rect.height() - ROW_HEIGHT * 2 - SCROLL_BAR_SIZE)

        self.percent_vertical_view.setGeometry(
            rect.width() - COLUMN_WIDTH * 2 - SCROLL_BAR_SIZE,
            rect.top(),
            COLUMN_WIDTH * 2 + SCROLL_BAR_SIZE,
            rect.height() - ROW_HEIGHT * 2 - SCROLL_BAR_SIZE)

        self.percent_horizontal_view.setGeometry(
            rect.left(),
            rect.height() - ROW_HEIGHT * 2 - SCROLL_BAR_SIZE,
            rect.width() - COLUMN_WIDTH * 2 - SCROLL_BAR_SIZE,
            ROW_HEIGHT * 2 + SCROLL_BAR_SIZE)

    def setData(self, lessons, groups):
        if groups is None or len(groups) == 0 or lessons is None or len(lessons) == 0:
            return

        students = sorted(Student.of(groups), key=lambda x: format_name(x))
        model = VisitModel(lessons, students)
        self.new_visit.connect(model.on_new_visit)
        self.lesson_start.connect(model.on_lesson_start)
        self.view.setModel(model)

        percent_vertical_model = PercentVerticalModel(lessons, students)
        percent_vertical_model.mimic(self.view.model())
        self.view_show_color_rate.connect(percent_vertical_model.view_show_color_rate)
        self.percent_vertical_view.setModel(percent_vertical_model)

        percent_horizontal_model = PercentHorizontalModel(lessons, students)
        percent_horizontal_model.mimic(self.view.model())
        self.percent_horizontal_view.setModel(percent_horizontal_model)

        model.item_changed.connect(percent_horizontal_model.data_updated)
        model.item_changed.connect(percent_vertical_model.data_updated)
        self.view.select_row.connect(model.select_row)
        # self.view.select_row.connect(percent_vertical_model.select_row)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    auth = Auth.log_in('VAE', '123456')
    group = Group.of(auth.user)[0]

    v = VisitTableWidget()
    v.setData(sorted(Lesson.of(group), key=lambda x: x.date), sorted(Student.of(group), key=lambda x: format_name(x)))

    v.view.selectColumn(2)

    v.show()

    sys.exit(app.exec_())
