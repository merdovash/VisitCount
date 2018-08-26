import traceback

from PyQt5.QtWidgets import QAction

from Client.MyQt.Program import MyProgram
from Client.test import safe


class DataAction(QAction):
    def __init__(self, name: list, row: int, window: 'MyMainWindow'):
        """
        :type name: list[str]
        :type row: int
        :type program: MainWindow
        """
        self.name = name
        self.table = window.centralWidget().table
        self.program = window.program
        super().__init__(name[0] if self.table.visit_table.isRowHidden(row) else name[1], window)
        self.row = row
        self.triggered.connect(self.action)
        # self.setCheckable(True)
        # self.setChecked(True)

    def action(self):
        print("action", not self.table.visit_table.isRowHidden(self.row))
        row_visible = not self.table.visit_table.isRowHidden(self.row)
        if row_visible:
            self.setText(self.name[0])
            self.table.visit_table.setRowHidden(self.row, True)
            self.table.percent_table.setRowHidden(self.row, True)
        else:
            self.setText(self.name[1])
            self.table.visit_table.setRowHidden(self.row, False)
            self.table.percent_table.setRowHidden(self.row, False)

        self._save_changes(row_visible)

    @safe
    def _save_changes(self, row_visible):
        print(self.program.win_config)
        self.program.win_config["table_header"]["lesson_info"][str(self.row)] = not row_visible
        self.program.win_config.sync()
        print(self.program.win_config)

