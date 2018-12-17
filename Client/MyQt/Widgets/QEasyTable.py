from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class QEasyTable(QTableWidget):
    def __init__(self, header=None, *__args):
        super().__init__(*__args)

        self.header_title = {}

        if header is not None:
            self.setHeader(header)

    def setHeader(self, header):
        self.header_title = {}
        self.header = header

        if isinstance(self.header, list):
            self.setColumnCount(len(header))

            for col, item in enumerate(header):
                if isinstance(item, (str, int)):
                    self.setHorizontalHeaderItem(col, QTableWidgetItem(str(item)))
                    self.header_title[str(item)] = col
                elif isinstance(item, dict):
                    self.setHorizontalHeaderItem(col, QTableWidgetItem(str(item['value'])))
                    self.header_title[str(item['name'])] = col
                elif hasattr(item, 'value') and hasattr(item, 'name'):
                    self.setHorizontalHeaderItem(col, QTableWidgetItem(str(item.value)))
                    self.header_title[str(item.name)] = col
                else:
                    raise AttributeError(f'cannot insert header {col}, {item}')
        else:
            raise TypeError(f'header must be list, but {type(header)} instead')

    def insertRowData(self, data, row=None):
        if len(data) == len(self.header_title):
            if row is None:
                row = self.rowCount()

            self.insertRow(row)

            if isinstance(data, list):
                for col, value in enumerate(data):
                    self.setItem(row, col, QTableWidgetItem(value))
            elif isinstance(data, dict):
                for col_header in data.keys():
                    value = data[col_header]
                    self.setItem(row, self.header_title[col_header], QTableWidgetItem(value))
            else:
                raise TypeError(f'row must be list or dict, but {type(data)} instead')
            self.resizeColumnsToContents()
        else:
            raise AttributeError(f'lengths of header({len(self.header)} and row({len(self.data)} mismatch ')
