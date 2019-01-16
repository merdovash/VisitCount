import sys
from operator import xor
from typing import List

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QSize, QRect, QVariant, QPoint
from PyQt5.QtGui import QColor, QResizeEvent, QCursor
from PyQt5.QtWidgets import QApplication, QTableView, QStyledItemDelegate, QStyleOptionViewItem, QHeaderView, QWidget, \
    QAbstractItemView, QScrollArea, QMenu

from Client.MyQt.ColorScheme import Color
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
    NotVisited = 0
    Visited = 1
    NotCompleted = 2

    LessonCompletedRole = Qt.UserRole + 1
    VisitRole = Qt.UserRole + 2

    def __init__(self, lessons, students):
        super().__init__()

        self.lessons: List[Lesson] = lessons
        self.students = students

    def data(self, index: QModelIndex, role=None):
        def item() -> int:
            lesson = self.lessons[index.column()]
            if lesson.completed:
                d = self.itemData(index)
                if d is not None and not d._is_deleted:
                    return VisitModel.Visited
                return VisitModel.NotVisited
            else:
                return VisitModel.NotCompleted

        if role == Qt.DisplayRole:
            return ['-', '+', ''][item()]
        if role == Qt.BackgroundColorRole:
            return [QColor(255, 255, 255), QColor(255, 255, 0), QColor(225, 225, 225)][item()]
        if role == Qt.TextAlignmentRole:
            return xor(Qt.AlignHCenter, Qt.AlignVCenter)
        if role == VisitModel.LessonCompletedRole:
            return self.lessons[index.column()].completed
        if role == VisitModel.VisitRole:
            data = self.itemData(index)
            if data == None or data._is_deleted:
                return VisitModel.NotVisited
            return VisitModel.Visited

    def itemData(self, index:QModelIndex):
        lesson = self.lessons[index.column()]
        if lesson.completed:
            student = self.students[index.row()]
            visits = [item for item in lesson.visitations if item.student_id == student.id]
            if len(visits)==1:
                return visits[0]
            if len(visits) == 0:
                return None
            raise ValueError('too many vistations')
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.students)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.lessons)

    def headerData(self, p_int, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return format_name(self.students[p_int])
            if orientation == Qt.Horizontal:
                return rept(self.lessons[p_int])
        if role == Qt.SizeHintRole:
            if orientation == Qt.Vertical:
                return QVariant()
            if orientation == Qt.Horizontal:
                return QVariant(QSize(COLUMN_WIDTH, HEADER_HEIGHT))

        if role == Qt.BackgroundColorRole:
            if orientation == Qt.Vertical:
                return [Color.primary_light, Color.secondary_light][Validate.card_id(self.students[p_int].card_id)]

    def flags(self, index: QModelIndex):
        if self.lessons[index.column()].completed:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.NoItemFlags


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
    def data(self, index: QModelIndex, role=None):
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.row() == 0:
                    return 100 / len(self.students) * len([item for item in Visitation.of(self.lessons[index.column()])
                                                           if item.student in self.students])
                if index.row() == 1:
                    return len([item for item in Visitation.of(self.lessons[index.column()])
                                if item.student in self.students])

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
        self.verticalHeader().customContextMenuRequested.connect(self.customMenuRequested)

    def customMenuRequested(self, pos: QPoint):
        c_pos = QCursor().pos()
        # c_f_pos = QCursor().pos()-QPoint(self.view.verticalHeader().width(), self.view.horizontalHeader().height())
        calc_pos = c_pos-self.tablePos()
        print(calc_pos)
        index: QModelIndex = self.indexAt(pos)
        menu = QMenu(self)
        if index.column()==0:
            menu.addAction('Студент')
        else:
            #print(index.row(), index.column())
            #index = index.sibling(index.row()+1, index.column()+1)
            print(index.row(), index.column())
            if self.model().data(index, role=VisitModel.LessonCompletedRole):
                menu.addSection('Из менить данные')
                print(self.model().data(index, role=VisitModel.VisitRole))
                if self.model().data(index, role=VisitModel.VisitRole):
                    menu.addAction('Исключить посещение')
                else:
                    menu.addAction('Отметить посещение')
            else:
                menu.addSection('Занятие не проведено')
        menu.popup(QCursor().pos())

    def tablePos(self):
        return self.mapToGlobal(self.pos())


class VisitTableWidget(QWidget):
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

    def setData(self, lessons, students):
        self.view.setModel(VisitModel(lessons, students))

        percent_vertical_model = PercentVerticalModel(lessons, students)
        percent_vertical_model.mimic(self.view.model())
        self.percent_vertical_view.setModel(percent_vertical_model)

        percent_horizontal_model = PercentHorizontalModel(lessons, students)
        percent_horizontal_model.mimic(self.view.model())
        self.percent_horizontal_view.setModel(percent_horizontal_model)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    auth = Auth.log_in('VAE', '123456')
    group = Group.of(auth.user)[0]

    v = VisitTableWidget()
    v.setData(sorted(Lesson.of(group), key=lambda x: x.date), Student.of(group))

    v.view.selectColumn(2)

    v.show()

    sys.exit(app.exec_())
