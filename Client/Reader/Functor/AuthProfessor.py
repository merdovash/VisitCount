from PyQt5.QtCore import Qt

from Client.Reader.Functor import OnRead
from DataBase2 import Professor, Auth, UserType
from DataBase2.Types import format_name
from Domain.functools.List import find


class AuthProfessorOnRead(OnRead):
    """
    Обрабатывает чтение карты
    """
    widget: 'AuthWindow'

    def __init__(self):
        super().__init__()

        self.professors = self.session.query(Professor).all()

    def __call__(self, card_id):
        professor = find(lambda x: x.card_id == card_id, self.professors)

        if professor is not None:
            auth = self.session \
                .query(Auth) \
                .filter(Auth.user_id == professor.id) \
                .filter(Auth.user_type == UserType.PROFESSOR).first()

            self.widget.login_input.set_image_text(auth.login, format_name(professor))
        else:
            self.widget.login_input.setText(card_id)

        self.widget.password_input.setFocus(Qt.ActiveWindowFocusReason)
