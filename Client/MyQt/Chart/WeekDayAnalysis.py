from Client.MyQt.Chart.QAnalysisDialog import QAnalysisDialog
from Domain.Aggregation import WeekDaysAggregation, Column


class WeekDayChart(QAnalysisDialog):
    def __init__(self, program, parent=None):
        self.data_type = QAnalysisDialog.DataType.WEEK_DAY
        super().__init__(program, parent)

        self.data = WeekDaysAggregation.by_professor(self.program.professor)

        self.draw()

        self.plot_types[0]['xlabel'] = 'День недели'

    def get_data(self):
        return self.data

    def refresh_data(self):
        self.data = WeekDaysAggregation.by_professor(self.program.professor,
                                                     groups=[i for i in self.groups.keys() if self.groups[i]],
                                                     disciplines=[i for i in self.disciplines.keys() if self.disciplines[i]])

    def _draw(self, plot_type, ax, **kwargs):
        if plot_type == 'line':
            kwargs['xticks'] = ['Пн', 'Вт', "Ср", "Чт", "Пт", "Сб", "Вс"]
        if plot_type == 'bar':
            self.get_data().plot.bar(
                x=Column.date,
                y=Column.visit_rate,
                ax=ax,
                title='Посещения',
                xlim=[1, 7] if plot_type == 'line' else None,
                **kwargs)
        elif plot_type == 'hist':
            self.get_data().plot(
                x=Column.date,
                y=Column.visit_rate,
                ax=ax,
                title='Посещения',
                xlim=[1, 7] if plot_type == 'line' else None,
                **kwargs)
