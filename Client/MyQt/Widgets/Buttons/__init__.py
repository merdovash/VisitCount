from PyQt5.QtWidgets import QToolButton, QMessageBox

from DataBase2.Types import format_name
from Domain import Action


class DeleteContactButton(QToolButton):
    def __init__(self, user, table, index):
        super().__init__()

        self.user = user
        self.index = index
        self.table = table

        self.setText('Удалить')

        self.clicked.connect(self.on_clcik)

    def on_clcik(self):
        reply = QMessageBox.question(self, 'Удаление',
                                     f"Вы действительно хотите удалить контакт ({format_name(self.user)})",
                                     QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            Action.delete_contact(self.user, self.table.professor.id)
            self.table.removeRow(self.index)
