from Client.MyQt.Chart.QAnalysisDialog import QAnalysisDialog
from Domain.Aggregation import WeekDays, Column


class WeekDayChart(QAnalysisDialog):
    def __init__(self, program, parent=None):
        self.data_type = QAnalysisDialog.DataType.WEEK_DAY
        super().__init__(program, parent)

        self.data = WeekDays.by_professor(self.program.professor)

        self.draw()

        self.plot_types[0]['xlabel'] = 'День недели'

    def get_data(self):
        return self.data

    def _draw(self, plot_type, ax, **kwargs):
        # if plot_type == 'line':
        #     kwargs['xticks'] = ['Пн', 'Вт', "Ср", "Чт", "Пт", "Сб", "Вс"]
        self.get_data().plot(
            x=Column.date,
            y=Column.visit_rate,
            ax=ax,
            kind=plot_type,
            title='Посещения',
            xlim=[1, 7] if plot_type == 'line' else None,
            **kwargs)
