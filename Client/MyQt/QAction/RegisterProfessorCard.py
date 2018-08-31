from PyQt5.QtWidgets import QAction

from Client.IProgram import IProgram
from Client.Reader import IReader


class RegisterProfessorCard(QAction):
    def __init__(self, program: IProgram, parent):
        super().__init__('Зарегистрирвоать карту', parent)

        self.program: IProgram = program
        self.triggered.connect(self._run_register)

    def _run_register(self):
        reader: IReader = self.program.reader()
        if reader is not None:
            self.program.window.message.emit('Приложите вашу карту для регистрации')
            reader.on_read_once(self._register)

    def _register(self, card_id):
        professor_id = self.program['professor']['id']
        self.program.database().register_professor_card(professor_id=professor_id, card_id=card_id)
        self.program.window.message.emit('Карта успешно зарегистрирована за вами')
        self.setDisabled(True)
