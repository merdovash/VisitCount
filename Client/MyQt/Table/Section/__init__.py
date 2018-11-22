from PyQt5.QtCore import QSize


class Markup:
    window_width: int = None
    window_height: int = None

    visit_count_col: int = None
    visit_count_col_index: int

    visit_count_row: int = None
    visit_count_row_index: int

    visit_rate_col: int = None
    visit_rate_col_index: int

    visit_rate_row: int = None
    visit_rate_row_index: int

    lessons_count: int = None
    students_count: int = None

    # последние настройки окна, проверяем совпадения с текущими чтобы не перерасчитывать остальное
    last_horizontal_offset: int = None
    last_vertical_offset: int = None
    size: QSize = None

    @classmethod
    def setup(cls, table: 'VisitSection'):
        cls.last_vertical_offset = table.verticalOffset()
        cls.last_horizontal_offset = table.horizontalOffset()

        cls.window_width = table.width() - table.verticalHeader().width() - 1 - table.verticalScrollBar().width()
        cls.window_height = table.height() - table.horizontalHeader().height() - 1 - table.horizontalScrollBar().height()

        cls.visit_count_col_index = len(table.lessons)
        cls.visit_rate_col_index = cls.visit_count_col_index + 1

        cls.visit_count_row_index = len(table.students)
        cls.visit_rate_row_index = cls.visit_count_row_index + 1

        cls.lessons_count = table.columnCount() - 2
        cls.students_count = table.rowCount() - 2

        cls.visit_rate_col = cls.window_width - table.columnWidth(table.columnCount() - 1)
        cls.visit_count_col = cls.visit_rate_col - table.columnWidth(table.columnCount() - 2)

        cls.visit_rate_row = cls.window_height - table.rowHeight(table.rowCount() - 1)
        cls.visit_count_row = cls.visit_rate_row - table.rowHeight(table.rowCount() - 2)

        assert cls.window_height >= cls.visit_rate_row >= cls.visit_count_row

        # print(f"width:{cls.window_width}, height:{cls.window_height}, count_col:{cls.visit_count_col}")
