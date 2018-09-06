from PyQt5.QtWidgets import QTableWidgetItem

from Client.MyQt.Table.Items.PercentItem import PercentItem


class PercentHeaderItem(QTableWidgetItem):
    def __init__(self, student_count, orientation=None, absolute=False, *__args):
        super().__init__(*__args)
        self.mask = "Итого на занятии{}" if orientation != PercentItem.Orientation.ByStudents else "Итого{}"
        self.setText(self.mask.format(f" из {student_count}" if absolute else ", %"))
