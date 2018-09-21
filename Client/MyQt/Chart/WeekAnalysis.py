from Client.MyQt.Chart.QAnalysisDialog import QAnalysisDialog, LessonData


class WeekChart(QAnalysisDialog):
    def __init__(self, program, parent=None):
        super().__init__(program, parent)

        self.info_label.setText('На данном графике представлено распредление посещений по неделям')

        self.count = 18
        self.global_acc.data = {1: [100, 43], 2: [100, 49], 3: [100, 57], 4: [100, 68], 5: [100, 67], 6: [100, 75],
                                7: [100, 64], 8: [100, 59], 9: [100, 58], 10: [100, 53], 11: [100, 56], 12: [0, 0],
                                13: [0, 0], 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [0, 0], 18: [0, 0]}

        self.draw()

    def format_ax(self):
        self.ax().set_ylim(0, 100)
        self.ax().set_xlim(0, self.count)

        self.ax().yaxis.grid(True)

        self.ax().set_xticks([i for i in range(self.count)])
        self.ax().set_yticks([i * 10 for i in range(10)])

        self.ax().set_xlabel("Недели")
        self.ax().set_ylabel("Процент посещений")

    def get_lessons(self):
        lessons = [LessonData(lesson, lesson.date.isocalendar()[1]) for lesson in self.program.professor.lessons]

        lessons.sort(key=lambda x: x.param)
        start = lessons[0].param - 1

        for lesson in lessons:
            lesson.param -= start

        return lessons
