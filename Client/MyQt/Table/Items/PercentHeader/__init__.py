from PyQt5.QtWidgets import QMenu, QTableWidgetItem

from Client.MyQt.Table.Items import AbstractContextItem
from Client.MyQt.Table.Items.PercentItem import PercentItem


class PercentHeaderItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, percents: list, orientation=None, *__args):
        super().__init__(*__args)
        self.percents = percents
        self.mask = "Итого на занятии{}" if orientation != PercentItem.Orientation.ByStudents else "Итого{}"
        self.setText(self.mask.format("" if PercentItem.absolute else ", %"))

    def show_context_menu(self, pos):
        menu = QMenu()
        print(pos)
        menu.move(pos)
        menu.addAction(
            "Отобразить в виде процентов" if PercentItem.absolute else "Отобразить в виде количества",
            self.change(not PercentItem.absolute))
        menu.exec_()

    def change(self, b):
        def f():
            self.setText(self.mask.format("" if b else ", %"))
            PercentItem.absolute = b
            for i in self.percents:
                i.updateText()

        return f
