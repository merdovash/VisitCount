from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem


class MonthTableItem(QTableWidgetItem):
    """
    item represents month of lesson
    """
    month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')

    def __init__(self, month_index: int = None, month: str = None):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        if month is not None:
            self.setText(month)
        elif month_index is not None:
            self.setText(MonthTableItem.month_names[month_index])
        else:
            self.setText("Месяц")
