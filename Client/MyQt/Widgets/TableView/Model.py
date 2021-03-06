from operator import xor
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt, QModelIndex, QAbstractTableModel, QVariant, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QStyledItemDelegate
from sqlalchemy import inspect

from Client.MyQt.ColorScheme import Color
from Client.Settings import Settings
from DataBase2 import Visitation, Lesson, Student
from Domain.Validation.Values import Validate

COLUMN_WIDTH = 48
ROW_HEIGHT = 20
HEADER_HEIGHT = 65
SCROLL_BAR_SIZE = 20


class AbstractPercentModel(QAbstractTableModel):
    color_rate: bool = False

    def __init__(self, lessons, students):
        super().__init__()

        self.lessons: List[Lesson] = lessons
        self.students: List[Student] = students

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
                visitations = Visitation.of(lesson)
                if index.row() == 0:
                    return round(100 / len(self.students) * len([item for item in visitations
                                                                 if item.student in self.students])) if len(
                        self.students) else 0
                if index.row() == 1:
                    return len([item for item in visitations if item.student in self.students])

    def rowCount(self, parent=None, *args, **kwargs):
        return 2

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.lessons)


class PercentVerticalModel(AbstractPercentModel):
    @pyqtSlot(bool, name='view_show_color_rate')
    def view_show_color_rate(self, state: bool):
        PercentVerticalModel.color_rate = state
        # print('style_changed', state)
        self.dataChanged.emit(self.index(0, 0), self.index(len(self.students) - 1, 1), (Qt.BackgroundColorRole,))

    @pyqtSlot(int, int, name='data_updated')
    def data_updated(self, row, col):
        self.dataChanged.emit(
            self.createIndex(row, 0),
            self.createIndex(row, self.columnCount() - 1),
            [Qt.EditRole] * self.columnCount())

    def count_visits(self, row: int) -> int:
        """
        Возвращает количество посещений для указанной строки
        :param row: индекс строки
        :return: колчиество посещений
        """
        return len([item for item in Visitation.of(self.lessons) if item.student_id == self.students[row].id])

    def data(self, index: QModelIndex, role=None):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignHCenter
        if role == Qt.DisplayRole:
            visits = self.count_visits(index.row())
            count = len(list(filter(lambda x: x.completed, self.lessons)))
            if index.column() == 0:
                return round(100 * visits // count) if count else 0
            if index.column() == 1:
                return visits
        if role == Qt.BackgroundColorRole:
            if PercentVerticalModel.color_rate:
                s = Settings.inst().colors
                total = len([l for l in self.lessons if l.completed])
                visit = self.count_visits(index.row())

                # если количество пропусков меньше 3х - студент хороший
                if total <= visit + 3:
                    return QColor(s.good_student)

                # если пропусков больше половины - студент плохой
                elif visit / total < 0.5 if total > 0 else False:
                    return QColor(s.bad_student)

                return QColor(s.avg_student)
        return QVariant()

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
    REASON = 3

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
        self.selected_row = None

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
                item.session().commit()

            self.item_changed.emit(index.row(), index.column())

    @pyqtSlot(int, name='select_row')
    def select_row(self, row: int):
        if self.selected_row == row:
            self.selected_row = None
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, len(self.lessons)),
                (Qt.BackgroundColorRole,))
        else:
            if self.selected_row is not None:
                self.dataChanged.emit(
                    self.index(self.selected_row, 0),
                    self.index(self.selected_row, len(self.lessons)),
                    (Qt.BackgroundColorRole,))
            self.selected_row = row
            self.dataChanged.emit(
                self.index(self.selected_row, 0),
                self.index(self.selected_row, len(self.lessons)),
                (Qt.BackgroundColorRole,))

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
            [Qt.DisplayRole | Qt.BackgroundColorRole | VisitModel.VisitRole] * 9)

        self.item_changed.emit(index.row(), index.column())

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        column = self.lessons.index(lesson)

        self.dataChanged.emit(
            self.createIndex(0, column),
            self.createIndex(self.rowCount() - 1, column),
            [Qt.DisplayRole | VisitModel.LessonCompletedRole] * self.rowCount()
        )

        for row in range(self.rowCount()):
            self.item_changed.emit(row, column)

    def data(self, index: QModelIndex, role=None):
        def item() -> int:
            if lesson.completed:
                d = self.itemData(index)
                if d:
                    return VisitModel.Visited
                if len([x for x in lesson.loss_reasons if x.student == student]):
                    return VisitModel.REASON
                return VisitModel.NotVisited
            return VisitModel.NotCompleted

        lesson = self.lessons[index.column()]
        student = self.students[index.row()]
        status = item()
        is_current = self.current_lesson == lesson
        if role == Qt.DisplayRole:
            return ['-', '+', '', ''][item()]

        if role == Qt.BackgroundColorRole:
            s = Settings.inst().colors
            main_color = (
                s.not_visited,
                s.visit,
                s.not_completed,
                s.sub_visit
            )[status]

            if is_current:
                main_color = Color.to_select(main_color)
            else:
                main_color = QColor(main_color)

            if index.row() == self.selected_row:
                main_color = Color.to_accent(main_color)

            return main_color

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
            if not data:
                return VisitModel.NotVisited
            return VisitModel.Visited

        if role == Qt.ToolTipRole:
            return (
                'Не посещено',
                'Посещено',
                'Не проведено',
                'Не посещено (уважительная причина)'
            )[status]

    def itemData(self, index: QModelIndex) -> Visitation or None:
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
                return self.students[p_int].short_name()
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
                s = Settings.inst().colors

                if not Validate.card_id(self.students[p_int].card_id):
                    return QColor(s.missing_card)

                total = len([l for l in self.lessons if l.completed])
                visit = len([item for item in Visitation.of(self.lessons) if item.student_id == self.students[p_int].id])

                # если количество пропусков меньше 3х - студент хороший
                if total <= visit + 3:
                    return QColor(s.good_student)

                # если пропусков больше половины - студент плохой
                elif visit / total < 0.5 if total > 0 else False:
                    return QColor(s.bad_student)

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
        f"{lesson.type.abbreviation}"


class VisitItemDelegate(QStyledItemDelegate):
    pass
    # def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
    #     painter.fillRect(option.rect, index.data(Qt.DecorationRole))
    #     painter.drawText(option.rect, xor(Qt.AlignHCenter, Qt.AlignVCenter), index.data(Qt.DisplayRole))
