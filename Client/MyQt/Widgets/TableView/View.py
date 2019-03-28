from typing import List

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QPoint, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QTableView, QHeaderView, QMenu, QMessageBox, QInputDialog

from Client.MyQt.Widgets.Dialogs.QRequesUncompleteLesson import QRequestUncompleteLesson
from Client.MyQt.Widgets.TableView import VisitModel
from Client.MyQt.Widgets.TableView.Model import VisitItemDelegate
from Client.Reader.Functor.RegisterCardProcess import RegisterCardProcess
from DataBase2 import Lesson, Visitation, Student
from Domain.functools.Format import agree_to_gender


class VisitView(QTableView):
    show_student_card_id = pyqtSignal('PyQt_PyObject')
    show_student_summary = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    set_current_lesson = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    select_current_lesson = pyqtSignal('PyQt_PyObject')

    lesson_start = pyqtSignal("PyQt_PyObject")
    lesson_finish = pyqtSignal()

    lesson_started = False

    lesson_changed = pyqtSignal('PyQt_PyObject', str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setItemDelegate(VisitItemDelegate())
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().show()
        self.horizontalHeader().show()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.customMenuRequested)

        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self.verticalHeaderMenuRequested)

        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.horizontalHeaderMenuRequested)

        self.set_current_lesson.connect(self.set_offset_on_set_current_lesson)

        self.lesson_start.connect(self.on_lesson_start)
        self.lesson_finish.connect(self.on_lesson_finish)

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        self.lesson_started = True
        self.current_lesson_started = lesson

    @pyqtSlot(name='on_lesson_finish')
    def on_lesson_finish(self):
        self.lesson_started = False
        self.current_lesson_started = None

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='set_offset_on_set_current_lesson')
    def set_offset_on_set_current_lesson(self, lessons: List[Lesson], lesson: Lesson):
        if self.model() is not None:
            col = self.model().getColumnIndex(lesson)
            self.scrollTo(self.model().createIndex(0, col))

    def customMenuRequested(self, pos: QPoint):
        def show_status():
            if not lesson.completed:
                msg = "Занятие не проведено"
            elif self.model().data(index, role=VisitModel.VisitRole):
                msg = f"Студент {student.full_name()} {agree_to_gender('посетил', student.last_name)} {lesson.repr()}"
            else:
                msg = f"Студент {student.full_name()} не {agree_to_gender('посетил', student.last_name)} {lesson.repr()}"

            QMessageBox().information(self, "Информация о посещении", msg)

        index: QModelIndex = self.indexAt(pos)

        menu = QMenu(self)

        lesson = self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole)
        student = self.model().headerData(index.row(), Qt.Vertical, VisitModel.ValueRole)

        menu.addSection("Информация")
        menu.addAction("Показать статус", show_status)

        if self.model().data(index, role=VisitModel.LessonCompletedRole) \
                and (not self.lesson_started or self.current_lesson_started == lesson):
            menu.addSection('Изменить данные')
            print(self.model().data(index, role=VisitModel.VisitRole))
            if self.model().data(index, role=VisitModel.VisitRole):
                menu.addAction('Исключить посещение', lambda: self.model().setData(index, False, Qt.EditRole))
            else:
                menu.addAction('Отметить посещение', lambda: self.model().setData(index, True, Qt.EditRole))
        else:
            menu.addSection('Занятие не проведено')

        menu.popup(QCursor().pos())

    def verticalHeaderMenuRequested(self, pos: QPoint):
        index = self.indexAt(pos)
        student = self.model().headerData(index.row(), Qt.Vertical, VisitModel.ValueRole)
        discipline = self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole).discipline
        professor = self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole).professor

        menu = QMenu(self)

        menu.addSection('Показать данные')
        menu.addAction(
            'Информация о карте',
            lambda: self.show_student_card_id.emit(student))

        menu.addAction(
            'Сводка',
            lambda: self.show_student_summary.emit(student, professor, discipline)
        )

        if not self.lesson_started:
            menu.addSection('Изменить данные')
            if student.card_id is None or student.card_id == '':
                menu.addAction(
                    'Зарегистрировать карту',
                    lambda: RegisterCardProcess(student, self)
                )
            else:
                menu.addAction(
                    'Изменить карту',
                    lambda: RegisterCardProcess(student, self)
                )
                menu.addAction(
                    'Удалить карту',
                    lambda: setattr(student, 'card_id', None)
                )

        menu.popup(QCursor().pos())

    def horizontalHeaderMenuRequested(self, pos: QPoint):
        def request_type_of_uncompliting_lessons(lesson):
            def delete_all():
                visitations: List[Visitation] = lesson.visitations
                for visit in visitations:
                    visit.delete()

                lesson.completed = False
                lesson.session().commit()

            def save_all():
                lesson.completed = False
                lesson.session().commit()

            if len(Visitation.of(lesson, with_deleted=False)) == 0:
                save_all()
            else:
                self.request = QRequestUncompleteLesson(lesson)
                self.request.save_all.connect(save_all)
                self.request.delete_all.connect(delete_all)
                self.request.show()

        def show_stats():
            visits = Visitation.of(lesson)
            students = Student.of(lesson)

            if lesson.completed:
                msg = f"Посетило {len(visits)} из {len(students)} ({round(len(visits) * 100 / (len(students)))}%)."
            else:
                msg = "Занятие не проведено."
            QMessageBox().information(
                self,
                "Статистика",
                msg
            )

        def request_new_lesson_type(lesson):
            result = QInputDialog().getItem(
                self,
                "Выберите новый тип занятия",
                f"Выберите новый тип занятия из выпадающего спсика ниже.\nТекущий тип занятия {lesson.type}",
                [Lesson.Type.types()[i] if i in Lesson.Type.types().keys() else ''
                 for i in range(max(Lesson.Type.types().keys())+1)]
            )
            if result[1]:
                lesson.type = result[0]
                self.lesson_changed.emit(lesson, 'type')
                lesson.session().commit()

        index = self.indexAt(pos)

        lesson = self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole)

        menu = QMenu(self)

        menu.addSection("Показать данные")
        menu.addAction('Показать статистику', show_stats)

        if not self.lesson_started:
            menu.addSection('Управление')
            menu.addAction(
                'Выбрать занятие',
                lambda: self.select_current_lesson.emit(
                    self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole))
            )

            menu.addSection("Редактирование данных")
            menu.addAction(
                'Отменить проведение',
                lambda: request_type_of_uncompliting_lessons(lesson))
            menu.addAction(
                'Изменить тип занятия',
                lambda: request_new_lesson_type(lesson)
            )

        menu.popup(QCursor().pos())

    def setModel(self, model: VisitModel):
        super().setModel(model)
        self.set_current_lesson.connect(model.setCurrentLesson)
        self.lesson_changed.connect(model.on_lesson_change)

    def model(self) -> VisitModel:
        return super().model()


class PercentView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.horizontalHeader().show()
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setItemDelegate(VisitItemDelegate())

        self.resizeRowsToContents()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


class PercentHorizontalView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().show()
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setItemDelegate(VisitItemDelegate())

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setModel(self, model):
        super().setModel(model)
        self.verticalHeader().setFixedWidth(self.parent().view.verticalHeader().width())
        self.resizeRowsToContents()
