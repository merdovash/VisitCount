from Client.MyQt.Chart.QAnalysisDialog import QAnalysisDialog, LessonData
from Domain.Aggregation import Weeks, Column


class WeekChart(QAnalysisDialog):
    def __init__(self, program, parent=None):
        super().__init__(program, parent)

        self.data = Weeks.by_professor(self.program.professor)

        self.draw()

    def refresh_data(self):
        print(self.groups, self.disciplines)
        self.data = Weeks.by_professor(self.program.professor,
                                       groups=[i for i in self.groups.keys() if self.groups[i]],
                                       disciplines=[i for i in self.disciplines.keys() if self.disciplines[i]])

    def get_lessons(self):
        lessons = [LessonData(lesson, lesson.date.isocalendar()[1]) for lesson in self.program.professor.lessons]

        lessons.sort(key=lambda x: x.param)
        start = lessons[0].param - 1

        for lesson in lessons:
            lesson.param -= start

        return lessons

    def get_data(self):
        return self.data

    def _draw(self, plot_type, ax, **kwargs):
        try:
            self.get_data().plot(
                x=Column.date,
                y=Column.visit_rate,
                ax=ax,
                kind=plot_type,
                title='Посещения',

                **kwargs)
        except TypeError as e:
            self.program.window.error.emit('Ошибка гарфика: ' + str(e))
