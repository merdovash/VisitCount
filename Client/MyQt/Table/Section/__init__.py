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

    @classmethod
    def setup(cls, table: 'VisitSection'):
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

        # print(f"width:{cls.window_width}, height:{cls.window_height}, count_col:{cls.visit_count_col}")
