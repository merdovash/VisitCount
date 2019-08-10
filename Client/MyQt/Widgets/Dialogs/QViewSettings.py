import json
import sys
from collections import defaultdict

from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGridLayout, QScrollArea, QLabel, QPushButton, QApplication, QSlider

from Client.MyQt.Widgets import BisitorWidget
from Client.MyQt.Widgets.Navigation import QAccentCancelButtons
from Client.MyQt.Widgets.QColorPicker import QColorPicker
from Client.Settings import _Setting, Settings, _SettingQColor, _SettingInt
from Client.src import resource


class QViewSettings(BisitorWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(QSize(800, 600))
        _grid = QGridLayout()

        scroll_area = QScrollArea()
        _grid.addWidget(scroll_area, 0, 0, 1, 4)

        self.grid = QGridLayout()
        grid = self.grid
        for i in range(6):
            grid.setColumnStretch(i, 1)

        scroll_area.setLayout(grid)

        self.data = Settings.inst()
        data = self.data
        print(data)
        row_count = 0
        for area_name, area in data.items():
            if area._type is None:
                continue

            area_label = QLabel(area.title)
            grid.addWidget(area_label, row_count, 2)
            row_count += 1

            for meta_key, row in area.items():
                row = getattr(area, meta_key, None)
                if isinstance(row, _Setting):
                    grid.addWidget(QLabel(row.title), row_count, 0, 1, 2)
                    if isinstance(row, _SettingQColor):
                        color_picker = QColorPicker(row, row.default, meta_key)

                        grid.addWidget(color_picker, row_count, 3, 1, 1)

                        reset_button = QPushButton(QIcon(str(resource("reset_ico.png"))), "")
                        reset_button.setToolTip("Вернуть значение по умолчанию")
                        reset_button.setEnabled(row != row.default)

                        color_picker.color_changed.connect(reset_button.setEnabled)
                        color_picker.color_change.connect(self._add_change)

                        reset_button.clicked.connect(color_picker.reset_color)
                        grid.addWidget(reset_button, row_count, 4, 1, 1)

                    elif isinstance(row, _SettingInt):
                        self.__int_row(row, meta_key, row_count, grid)

                    else:
                        raise NotImplementedError()

                    row_count += 1

        _grid.addWidget(QAccentCancelButtons(self._apply, self.hide), 1, 2, 1, 2)
        self.changes = defaultdict(dict)
        self.setLayout(_grid)

    def __int_row(self, data, name, row_index, layout):
        default = data.default
        slider = QSlider(Qt.Horizontal)
        slider.setMaximum(data.limits[1])
        slider.setMinimum(data.limits[0])
        slider.setValue(data)

        layout.addWidget(slider, row_index, 2, 1, 2)

        reset_button = QPushButton(QIcon(str(resource("reset_ico.png"))), "")
        reset_button.setToolTip("Вернуть значение по умолчанию")
        reset_button.setEnabled(data != data.default)

        slider.valueChanged.connect(lambda x: reset_button.setEnabled(x != default))
        slider.valueChanged.connect(lambda x: self._add_change({
            "value": x,
            "section": "colors",
            "name": str(name)
        }))

        reset_button.clicked.connect(lambda: slider.setValue(default))
        layout.addWidget(reset_button, row_index, 4, 1, 1)


    def _load_settings(self) -> dict:
        return Settings.inst()

    def _add_change(self, info):
        self.changes[info['section']][info['name']] = info['value']
        pass

    def _apply(self):
        print(self.data)
        for section, values in self.changes.items():
            sub_settings = getattr(self.data, section)
            for value_name, new_value in values.items():
                value_settings = getattr(sub_settings, value_name)
                value_settings.set(new_value)
        self.data.save()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QViewSettings()

    w.show()

    sys.exit(app.exec_())