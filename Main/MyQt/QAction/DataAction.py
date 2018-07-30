import traceback

from PyQt5.QtWidgets import QAction


class DataAction(QAction):
    def __init__(self, name: list, row: int, window: "MainWindow"):
        """

        :type window: MainWindow
        """
        self.name = name
        self.table = window.centralWidget().table
        self.window = window
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

    def _save_changes(self, row_visible):
        try:
            print(self.window.config)
            self.window.config["table_header"]["lesson_info"][str(self.row)] = not row_visible
            self.window.config.sync()
            print(self.window.config)
        except Exception:
            traceback.print_exc()
