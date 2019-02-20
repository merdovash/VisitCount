from collections import namedtuple, defaultdict
from typing import Callable, Any, List, Dict

from DataBase2 import Visitation, Lesson, Student, Group, Discipline
from Domain.functools.Decorator import memoize


class Vector:
    def __init__(self, *args):
        assert all(map(lambda x: isinstance(x, int), args)), "values must be int"

        self.list_ = list(args)

    def __add__(self, other):
        assert len(other) == len(self), "different sizes"

        return Vector(*[self[i] + other[i] for i in range(len(self))])

    def __iadd__(self, other):
        assert len(other) == len(self)

        return Vector(*[self[i] + other[i] for i in range(len(self))])

    def __len__(self):
        return len(self.list_)

    def __getitem__(self, item):
        assert isinstance(item, int), "indexes must be int"
        assert item < len(self), "index is out of range"

        return self.list_[item]

    def __setitem__(self, key, value):
        assert isinstance(key, int), "index must be int"
        assert isinstance(value, int), "value must be int"
        assert key < len(self), "index is out of range"

        self.list_[key] = value

    def __repr__(self):
        return f"<Vector {len(self)} ({', '.join(str(i) for i in self.list_)})>"


class NamedVector:
    def __init__(self, **kwargs):
        self._dict = kwargs

    def __add__(self, other: 'NamedVector'):
        assert self._dict.keys() == other._dict.keys()
        return NamedVector(**{key: self._dict[key] + other._dict[key] for key in self._dict.keys()})

    def __getitem__(self, item):
        assert isinstance(item, int)
        assert len(self._dict.keys()) < item
        return self._dict[list(self._dict.keys())[item]]

    @classmethod
    def rate(cls, first, second):
        return round(first * 100 / second) if second else 0

    def __repr__(self):
        return "<Vector ("+', '.join([f'{key}={value}' for key, value in self._dict.items()])+")>"

    def __getattr__(self, item):
        return self._dict[item]


row = namedtuple('row', 'value lesson student')


class Data:
    def __init__(self, professor=None, groups=None, disciplines=None):
        lessons = Lesson.of(professor)
        if groups is not None:
            lessons &= Lesson.of(groups)
        if disciplines is not None:
            lessons &= Lesson.of(disciplines)

        self.rows: List[row] = []
        for lesson in lessons:
            students = self._get_students(lesson.groups, groups)

            for student in students:
                visitation = Visitation.get(professor.session(), student_id=student.id, lesson_id=lesson.id)
                status = 0 if visitation is None or visitation.is_deleted() else 1
                self.rows.append(row(Vector(status, int(lesson.completed)), lesson, student))

        self.data: Dict[Any, List[row]] = {}
        self.ignored = []

    @memoize
    def _get_students(self, lesson_groups, groups):
        students = Student.of(lesson_groups)
        if groups is not None:
            students &= Student.of(groups)
        return students

    def addRow(self, row):
        self.rows.append(row)

    def group_by(self, group_by: Callable[[row], Any]):
        self.data = defaultdict(list)

        for item in self.rows:
            self.data[group_by(item)].append(item)

        return self

    def filter(self, func: Callable[[row], bool]):
        self.rows = list(filter(func, self.rows))
        return self

    def _filter(self, ignored):
        # TODO: не фильтрует по граппам лекций
        def _case(obj: row):
            for item in ignored:
                if isinstance(item, list):
                    if Group.of(obj.lesson) == item:
                        return False
                    elif len(item) == 1 and item[0] in obj.student.groups:
                        return False
                elif isinstance(item, Discipline):
                    if item == obj.lesson.discipline:
                        return False
            return True

        return _case

    def avg(self, ignored=None):
        if self.data == {}:
            self.group_by(lambda x: 'total')

        result = {key: None for key in self.data.keys()}
        for key in self.data:
            if ignored is not None and len(ignored) > 0:
                values = filter(self._filter(ignored), self.data[key])
            else:
                values = self.data[key]

            values = list(map(lambda x: x.value, values))
            res = sum(values, Vector(0, 0))
            if res[1] == 0:
                result[key] = 0
            else:
                result[key] = res[0] / res[1]

        return result
