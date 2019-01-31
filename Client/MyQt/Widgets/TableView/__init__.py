import sys
from operator import xor
from typing import List

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize, QRect, QVariant, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QResizeEvent, QCursor, QFont
from PyQt5.QtWidgets import QApplication, QTableView, QStyledItemDelegate, QStyleOptionViewItem, QHeaderView, QWidget, \
    QAbstractItemView, QScrollArea, QMenu, QMessageBox
from sqlalchemy import inspect

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Dialogs.QOkMsg import QOkMsg
from Client.Reader.Functor.RegisterCardProcess import RegisterCardProcess
from DataBase2 import Lesson, Auth, Student, Group, Visitation
from Domain.Validation.Values import Validate
from Domain.functools.Decorator import memoize
from Domain.functools.Format import format_name


def rept(lesson):
    return f"{lesson.week}\n" \
        f"{lesson.date.day:02d}.{lesson.date.month:02d}\n" \
        f"{lesson.date.hour}:{lesson.date.minute}\n" \
        f"{['Л', 'лр', 'пр'][lesson.type]}"


COLUMN_WIDTH = 48
ROW_HEIGHT = 20
HEADER_HEIGHT = 65
SCROLL_BAR_SIZE = 20


class VisitModel(QAbstractTableModel):
    DEFAULT_FONT = QFont()

    CURRENT_LESSON_FONT = QFont(DEFAULT_FONT)
    CURRENT_LESSON_FONT.setBold(True)

    NotVisited = 0
    Visited = 1
    NotCompleted = 2

    LessonCompletedRole = Qt.UserRole + 1
    VisitRole = Qt.UserRole + 2
    CardIdRole = Qt.UserRole + 3
    ValueRole = Qt.UserRole + 4

    item_changed = pyqtSignal(int, int)

    def __init__(self, lessons, students):
        super().__init__()

        self.lessons: List[Lesson] = lessons
        self.students: List[Student] = students

        self.current_lesson: Lesson = lessons[3]

    def setData(self, index: QModelIndex, value, role=None):
        if role == Qt.EditRole:
            item = self.itemData(index)
            if value == True:
                if item is None:
                    student = self.students[index.row()]
                    lesson = self.lessons[index.column()]
                    session = inspect(student).session
                    visit = Visitation.new(student_id=student.id, lesson_id=lesson.id)

                    session.add(visit)

                    session.commit()

                    session.expire(lesson)
                    session.expire(student)
                else:
                    item._is_deleted = False
            else:
                item.delete()

            self.item_changed.emit(index.row(), index.column())

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='setCurrentLesson')
    def setCurrentLesson(self, lessons: List[Lesson], lesson: Lesson):
        column = self.getColumnIndex(lesson)
        if column > 0:
            self.current_lesson = lesson
            self.dataChanged.emit(
                self.createIndex(0, column),
                self.createIndex(self.rowCount() - 1, column),
                [Qt.BackgroundColorRole | Qt.FontRole] * self.rowCount()
            )

    def data(self, index: QModelIndex, role=None):
        def item() -> int:
            lesson = self.lessons[index.column()]
            if lesson.completed:
                d = self.itemData(index)
                if d is not None and not d._is_deleted:
                    return VisitModel.Visited
                return VisitModel.NotVisited
            return VisitModel.NotCompleted

        lesson = self.lessons[index.column()]
        student = self.students[index.row()]
        status = item()
        is_current = self.current_lesson == lesson
        if role == Qt.DisplayRole:
            return ['-', '+', ''][item()]

        if role == Qt.BackgroundColorRole:
            return (
                (QColor(255, 255, 255), QColor(225, 225, 255)),
                (QColor(200, 200, 0), QColor(255, 255, 0)),
                (QColor(200, 200, 200), QColor(255, 255, 255))
            )[status][int(is_current)]

        if role == Qt.TextAlignmentRole:
            return xor(Qt.AlignHCenter, Qt.AlignVCenter)

        if role == Qt.FontRole:
            if self.current_lesson == lesson:
                return self.CURRENT_LESSON_FONT
            return self.DEFAULT_FONT

        if role == VisitModel.LessonCompletedRole:
            return lesson.completed

        if role == VisitModel.VisitRole:
            data = self.itemData(index)
            if data == None or data._is_deleted:
                return VisitModel.NotVisited
            return VisitModel.Visited

    def itemData(self, index: QModelIndex):
        lesson = self.lessons[index.column()]
        if lesson.completed:
            student = self.students[index.row()]
            visits = [item for item in lesson.visitations if item.student_id == student.id]
            if len(visits) == 1:
                return visits[0]
            if len(visits) == 0:
                return None
            raise ValueError('too many vistations')
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.students)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.lessons)

    def setHeaderData(self, p_int, orientation, value, role=None):
        if orientation == Qt.Horizontal:
            lesson = self.lessons[p_int]
            if role == self.LessonCompletedRole:
                if lesson.completed:
                    if value == True:
                        return False
                    else:
                        lesson.completed = True
                        return True

    def headerData(self, p_int, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return format_name(self.students[p_int])
            if orientation == Qt.Horizontal:
                return rept(self.lessons[p_int])
        if role == self.CardIdRole:
            if orientation == Qt.Vertical:
                return self.students[p_int].card_id
        if role == Qt.SizeHintRole:
            if orientation == Qt.Vertical:
                return QVariant()
            if orientation == Qt.Horizontal:
                return QVariant(QSize(COLUMN_WIDTH, HEADER_HEIGHT))
        if role == Qt.BackgroundColorRole:
            if orientation == Qt.Vertical:
                return [Color.primary_light, Color.secondary_light][Validate.card_id(self.students[p_int].card_id)]
        if role == self.ValueRole:
            if orientation == Qt.Horizontal:
                return self.lessons[p_int]
            if orientation == Qt.Vertical:
                return self.students[p_int]

    def flags(self, index: QModelIndex):
        if self.lessons[index.column()].completed:
            return Qt.ItemIsEnabled
        else:
            return Qt.NoItemFlags

    def getColumnIndex(self, lesson: Lesson):
        try:
            return self.lessons.index(lesson)
        except ValueError:
            return -1


class VisitItemDelegate(QStyledItemDelegate):
    pass
    # def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
    #     painter.fillRect(option.rect, index.data(Qt.DecorationRole))
    #     painter.drawText(option.rect, xor(Qt.AlignHCenter, Qt.AlignVCenter), index.data(Qt.DisplayRole))


class AbstractPercentModel(QAbstractTableModel):
    def __init__(self, lessons, students):
        super().__init__()

        self.lessons = lessons
        self.students = students

        self.other_model = None

    def mimic(self, other_model):
        self.other_model = other_model

    def headerData(self, p_int, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if p_int == 0:
                    return 'Итого,\n%'
                else:
                    return f'Всего,\nиз {len(list(filter(lambda x: x.completed, self.lessons)))}'
            if orientation == Qt.Vertical:
                if p_int == 0:
                    return 'Итого, %'
                if p_int == 1:
                    return f'Всего из {len(self.students)}'
        if role == Qt.SizeHintRole:
            if orientation == Qt.Horizontal:
                return QVariant(QSize(COLUMN_WIDTH, HEADER_HEIGHT))
            if orientation:
                return self.other_model.headerData(p_int, orientation, role)


class PercentVerticalModel(AbstractPercentModel):
    @pyqtSlot(int, int, name='data_updated')
    def data_updated(self, row, col):
        self.dataChanged.emit(
            self.createIndex(row, 0),
            self.createIndex(row, self.columnCount() - 1),
            [Qt.EditRole] * self.columnCount())

    def data(self, index: QModelIndex, role=None):
        if role == Qt.DisplayRole:
            visits = len(
                [item for item in Visitation.of(self.lessons) if item.student_id == self.students[index.row()].id])
            count = len(list(filter(lambda x: x.completed, self.lessons)))
            if index.column() == 0:
                return round(100 * visits // count)
            if index.column() == 1:
                return visits

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.students)


class PercentHorizontalModel(AbstractPercentModel):
    @pyqtSlot(int, int, name='data_updated')
    def data_updated(self, row, col):
        self.dataChanged.emit(
            self.createIndex(0, col),
            self.createIndex(self.rowCount() - 1, col),
            [Qt.EditRole] * self.rowCount())

    def data(self, index: QModelIndex, role=None):
        lesson = self.lessons[index.column()]
        if index.isValid():
            if role == Qt.DisplayRole:
                visitations = [visit for visit in lesson.visitations if not visit._is_deleted]
                if index.row() == 0:
                    return round(100 / len(self.students) * len([item for item in visitations
                                                                 if item.student in self.students]))
                if index.row() == 1:
                    return len([item for item in visitations if item.student in self.students])

    def rowCount(self, parent=None, *args, **kwargs):
        return 2

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.lessons)


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


class VisitView(QTableView):
    show_student_card_id = pyqtSignal('PyQt_PyObject')
    set_current_lesson = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    select_current_lesson = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(VisitItemDelegate())
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

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='set_offset_on_set_current_lesson')
    def set_offset_on_set_current_lesson(self, lessons: List[Lesson], lesson: Lesson):
        if self.model() is not None:
            col = self.model().getColumnIndex(lesson)
            self.scrollTo(self.model().createIndex(0, col))

    def customMenuRequested(self, pos: QPoint):
        index: QModelIndex = self.indexAt(pos)

        menu = QMenu(self)

        if self.model().data(index, role=VisitModel.LessonCompletedRole):
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

        menu = QMenu(self)

        menu.addSection('Показать данные')
        menu.addAction(
            'Показать карту',
            lambda: self.show_student_card_id.emit(student))

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
        menu.popup(QCursor().pos())

    def horizontalHeaderMenuRequested(self, pos: QPoint):
        index = self.indexAt(pos)

        menu = QMenu(self)

        menu.addAction(
            'Выбрать занятие',
            lambda: self.select_current_lesson.emit(
                self.model().headerData(index.column(), Qt.Horizontal, VisitModel.ValueRole))
        )

        menu.popup(QCursor().pos())

    def setModel(self, model: VisitModel):
        super().setModel(model)
        self.set_current_lesson.connect(model.setCurrentLesson)

    def model(self) -> VisitModel:
        return super().model()


class VisitTableWidget(QWidget):
    set_current_lesson = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    select_current_lesson = pyqtSignal('PyQt_PyObject')

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        lesson.completed = True
        inspect(lesson).session.commit()

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
        students = sorted(Student.of(groups), key=lambda x:format_name(x))
        model = VisitModel(lessons, students)
        self.view.setModel(model)

        percent_vertical_model = PercentVerticalModel(lessons, students)
        percent_vertical_model.mimic(self.view.model())
        self.percent_vertical_view.setModel(percent_vertical_model)

        percent_horizontal_model = PercentHorizontalModel(lessons, students)
        percent_horizontal_model.mimic(self.view.model())
        self.percent_horizontal_view.setModel(percent_horizontal_model)

        model.item_changed.connect(percent_horizontal_model.data_updated)
        model.item_changed.connect(percent_vertical_model.data_updated)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    auth = Auth.log_in('VAE', '123456')
    group = Group.of(auth.user)[0]

    v = VisitTableWidget()
    v.setData(sorted(Lesson.of(group), key=lambda x: x.date), sorted(Student.of(group), key=lambda x: format_name(x)))

    v.view.selectColumn(2)

    v.show()

    sys.exit(app.exec_())
