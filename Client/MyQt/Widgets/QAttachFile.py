from pathlib import Path

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QFileDialog, QGridLayout

from Domain.FileManager import openFile


class QAttachFile(QWidget):
    filters = {
        'pdf': 'PDF Файлы (*.pdf)',
        'docx': 'Документы (*.docx, *.doc)',
        'img': 'Изображения (*.png, *.jpg, *.jpeg)'
    }

    def __init__(self, read_mode, filter):
        super().__init__()
        self.read_mode = read_mode
        self._filter = filter
        self.filter = ";;".join(self.filters[f] for f in filter) if isinstance(filter, (list, tuple)) else self.filters[filter]

        self.grid = QGridLayout()

        self.file_name_title = QLabel('Выбранный файл: ')
        self.grid.addWidget(self.file_name_title, 0, 0, 1, 1)

        self.file_name = QLabel()
        self.file_name.setWordWrap(True)
        self.grid.addWidget(self.file_name, 0, 1, 1, 3)

        self.file_data = None

        self.remove_file_button = QPushButton("Отменить выбор файла")
        self.remove_file_button.clicked.connect(self._unselect_file)
        self.remove_file_button.setVisible(False)
        self.grid.addWidget(self.remove_file_button, 1, 0, 1, 2)

        self.show_file_button = QPushButton('Открыть файл')
        self.show_file_button.setVisible(False)
        self.show_file_button.clicked.connect(self._show_file)
        self.grid.addWidget(self.show_file_button, 1, 2, 1, 2)

        self.load_button = QPushButton('Прикрепить документ')
        self.load_button.clicked.connect(self._attach_document)
        self.grid.addWidget(self.load_button, 2, 1, 1, 2)

        self.setLayout(self.grid)

    def set_file(self, file_path: Path):
        with open(str(file_path), 'rb') as file:
            self.file_data = file.read()
        self.file_name.setText(str(file_path))
        self.remove_file_button.setVisible(True)
        self.show_file_button.setVisible(True)

    def get_file(self):
        return self.file_data

    def get_path(self):
        return Path(self.file_name.text())

    def _unselect_file(self):
        self.file_data = None
        self.file_name.setText('')
        self.remove_file_button.setVisible(False)
        self.show_file_button.setVisible(False)

    def _attach_document(self):
        name, _ = QFileDialog.getOpenFileName(
            self,
            'Open File',
            'Выберите файл',
            filter=self.filter)
        if name not in {'', None}:
            self.file_name.setText(str(name))
            with open(name, self.read_mode) as file:
                self.file_data = file.read()

            self.remove_file_button.setVisible(True)
            self.show_file_button.setVisible(True)

    def _show_file(self):
        openFile(self.file_name.text())