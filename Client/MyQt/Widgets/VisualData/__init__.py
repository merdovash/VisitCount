from collections import defaultdict
from typing import Type, List, Any, Dict

from PyQt5.QtWidgets import QWidget, QFormLayout

from DataBase2 import Lesson, Visitation, Student
from Domain.Structures import NamedVector


class _VisualData(QWidget):
    group_by = None
    name = None
    description = None

    def __new__(cls, *args, **kwargs):
        assert all(x is not None for x in [cls.group_by, cls.name, cls.description])
        return super(_VisualData, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def subclasses(cls)-> List[Type['_VisualData']]:
        return cls.__subclasses__()

    def remove_all_rows(self, form_layout: QFormLayout):
        while form_layout.rowCount()-1>0:
            try:
                form_layout.removeRow(0)
            except:
                break

    def group(self, lesson: Lesson)-> Any:
        raise NotImplementedError()

    def calculate_visitations(self, lessons: List[Lesson])-> (Dict[Any, NamedVector], int):
        visitations = defaultdict(lambda: NamedVector(visit=0, total=0))
        completed = 0
        for lesson in lessons:
            if lesson.completed:
                completed += 1

                visitations[self.group(lesson)] += NamedVector(
                    visit=len(Visitation.of(lesson)),
                    total=len(Student.of(lesson))
                )
        return visitations, completed
