from operator import xor
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt, QModelIndex, QAbstractTableModel, QVariant, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QStyledItemDelegate
from sqlalchemy import inspect

from Client.MyQt.ColorScheme import Color
from DataBase2 import Visitation, Lesson, Student
from Domain.Validation.Values import Validate
from Domain.functools.Format import format_name


COLUMN_WIDTH = 48
ROW_HEIGHT = 20
HEADER_HEIGHT = 65
SCROLL_BAR_SIZE = 20


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
                                                                 if item.student in self.students])) if len(self.students) else 0
                if index.row() == 1:
                    return len([item for item in visitations if item.student in self.students])

    def rowCount(self, parent=None, *args, **kwargs):
        return 2

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.lessons)


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
                return round(100 * visits // count) if count else 0
            if index.column() == 1:
                return visits

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.students)


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

        self.current_lesson: Lesson = lessons[0]

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

    @pyqtSlot('PyQt_PyObject', str, name='on_lesson_change')
    def on_lesson_change(self, lesson, field):
        index = self.getColumnIndex(lesson)
        if field in ['type']:
            self.headerDataChanged.emit(Qt.Horizontal, index, Qt.DisplayRole)

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='setCurrentLesson')
    def setCurrentLesson(self, lessons: List[Lesson], lesson: Lesson):
        column = self.getColumnIndex(lesson)
        if column >= 0:
            self.current_lesson = lesson
            self.dataChanged.emit(
                self.createIndex(0, column),
                self.createIndex(self.rowCount() - 1, column),
                [Qt.BackgroundColorRole | Qt.FontRole] * self.rowCount()
            )

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', name='on_new_visit')
    def on_new_visit(self, visit, student, lesson):
        index = self.createIndex(self.students.index(student), self.lessons.index(lesson))
        self.dataChanged.emit(
            index,
            index,
            [Qt.DisplayRole | Qt.BackgroundColorRole | VisitModel.VisitRole]*9)

        self.item_changed.emit(index.row(), index.column())

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        column = self.lessons.index(lesson)

        self.dataChanged.emit(
            self.createIndex(0, column),
            self.createIndex(self.rowCount()-1, column),
            [Qt.DisplayRole | VisitModel.LessonCompletedRole] * self.rowCount()
        )

        for row in range(self.rowCount()):
            self.item_changed.emit(row, column)

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
                (QColor(255, 255, 0, 200), QColor(255, 255, 0)),
                (QColor(200, 200, 200, 255), QColor(255, 255, 255))
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
            if data is None or data._is_deleted:
                return VisitModel.NotVisited
            return VisitModel.Visited

        if role == Qt.ToolTipRole:
            return (
                'Не посещено',
                'Посещено',
                'Не проведено'
            )[status]

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
            if orientation == Qt.Horizontal:
                if self.current_lesson == self.lessons[p_int]:
                    return Color.primary
                else:
                    return QVariant()
        if role == self.ValueRole:
            if orientation == Qt.Horizontal:
                return self.lessons[p_int]
            if orientation == Qt.Vertical:
                return self.students[p_int]
        if role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.lessons[p_int].repr()

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


def rept(lesson):
    return f"{lesson.week}\n" \
        f"{lesson.date.day:02d}.{lesson.date.month:02d}\n" \
        f"{lesson.date.hour}:{lesson.date.minute}\n" \
        f"{['Л', 'лр', 'пр'][lesson.type]}"


class VisitItemDelegate(QStyledItemDelegate):
    pass
    # def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
    #     painter.fillRect(option.rect, index.data(Qt.DecorationRole))
    #     painter.drawText(option.rect, xor(Qt.AlignHCenter, Qt.AlignVCenter), index.data(Qt.DisplayRole))