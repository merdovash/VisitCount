class OneHot:
    def __init__(self, size, func=None):
        self.size = size
        self.func = func
        self.data = {}

    def __getitem__(self, lesson):
        r = [0 for _ in range(self.size)]
        r[self.index(self.func(lesson))] = 1
        return r

    def index(self, value):
        if value not in self.data:
            self.data[value] = len(self.data)
        return self.data[value]


class OneHotLessonIndex(OneHot):
    def __init__(self):
        super().__init__(6)

    def __getitem__(self, lesson):
        r = [0 for _ in range(self.size)]
        r[lesson.index()] = 1
        return r


class OneHotLessonType(OneHot):
    def __getitem__(self, lesson):
        r = [0 for _ in range(self.size)]
        r[lesson.type_id] = 1
        return r


class OneHotLessonWeek(OneHot):
    def __getitem__(self, lesson):
        r = [0 for _ in range(self.size)]
        r[lesson.week] = 1
        return r


class OneHotDiscipline(OneHot):
    def __getitem__(self, lesson):
        r = [0 for _ in range(self.size)]
        r[lesson.week] = 1
        return r

