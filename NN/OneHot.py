import keras
from keras import Input, Model
from keras.layers import Dense
from pandas import DataFrame

from DataBase2 import Professor, Student, Discipline, Visitation, Group, Lesson, LessonType
from Domain.Aggregation.Lessons import lessons_by_date
from Domain.Aggregation.Visitations import visitations_rate


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


class GroupAccOneHot(OneHot):
    def __init__(self):
        super().__init__(2)

    def __getitem__(self, item):
        r = [0 for _ in range(self.size)]
        r[round(visitations_rate(item).rate())] = 1
        return r


class Inputer:
    def __init__(self, obj, semester):
        self.semester = semester
        students = Student.of(obj)
        self.professors = Professor.of(students, semester=semester)
        self.disciplines = Discipline.of(students, semester=semester)

        self.discipline_one_hot = OneHot(len(self.disciplines), lambda x: x.discipline)
        self.professor_one_hot = OneHot(len(self.professors), lambda x: x.professor)
        self.lesson_index_one_hot = OneHotLessonIndex()
        self.lesson_day_one_hot = OneHot(6, lambda x: x.date.weekday())
        self.lesson_week_one_hot = OneHotLessonWeek(18)
        self.lesson_type_one_hot = OneHotLessonType(4)

        self.group_acc_one_hot = GroupAccOneHot()

        self.input_size = 6 + 4 + 18 + 6 + len(self.professors) + len(self.disciplines) + 1 + 2 + 6 + 1

    def make(self, student):
        visitations = set(Visitation.of(student))
        lessons = Lesson.of(student)

        X = []
        Y = []

        lesson_count_one_hot = OneHot(6, lambda x: len(lessons_by_date(student, x.date.date())))

        group_rate = visitations_rate(Group.of(student, self.semester)).rate(2)
        for index, lesson in enumerate(lessons):
            if lesson.completed:
                input_data = []
                input_data.extend(self.lesson_index_one_hot[lesson])
                input_data.extend(self.lesson_type_one_hot[lesson])
                input_data.extend(self.lesson_week_one_hot[lesson])
                input_data.extend(self.lesson_day_one_hot[lesson])
                input_data.extend(self.professor_one_hot[lesson])
                input_data.extend(self.discipline_one_hot[lesson])
                input_data.append(group_rate)
                input_data.extend(self.group_acc_one_hot[lessons[:index]])
                input_data.extend(lesson_count_one_hot[lesson])
                input_data.append(1)

                output_data = [int(bool(len(set(Visitation.of(lesson)) & visitations)))]

                X.append(input_data)
                Y.append(output_data)
        return X, Y

    def description(self):
        def param(index):
            if index < 6:
                return f'Занятие №{index + 1}', 'Время занятия'
            index -= 6

            if index < 4:
                lesson_type = LessonType.get(id=index)
                if lesson_type is None:
                    return 'None', 'None'
                return lesson_type.full_name(), 'Тип занятия'
            index -= 4

            if index < 18:
                return f'{index} неделя', 'Номер недели'
            index -= 18

            if index < 6:
                return ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"][index], 'День недели'
            index -= 6

            if index < len(self.professors):
                return self.professors[index].short_name(), 'Преподаватель'
            index -= len(self.professors)

            if index < len(self.disciplines):
                return self.disciplines[index].short_name(), 'Дисциплина'
            index -= len(self.disciplines)

            if index < 3:
                return [
                    ('Уровень посещений', 'Уровень посещений'),
                    ('Низкий уровень раньше', 'Уровень посещений'),
                    ("Высокий уровень раньше", 'Уровень посещений')][index]
            index -= 3

            if index < 6:
                return f"{index + 1} занятий сегодня", \
                       "Кол-во занятий"
            index -= 6

            return 'Деловой подход', 'Всегда Фактор'

        weights = self.model.get_weights()
        df = DataFrame(
            {
                'Влияние': weight[0],
                'Параметр': param(index)[0],
                'Тип': param(index)[1]
            } for index, weight in enumerate(weights[0]))
        return df

    def make_model(self):
        input_layer = Input((self.input_size,))

        output_layer = Dense(1, activation='sigmoid', kernel_initializer=keras.initializers.Zeros())(input_layer)

        model = Model(inputs=input_layer, outputs=output_layer)

        model.compile('adam', loss='mean_squared_error')

        self.model = model

        return model
