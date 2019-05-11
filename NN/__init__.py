from typing import Set

import keras
from keras import Model, Input, Sequential
from keras.layers import Dense

import numpy as np
from pandas import DataFrame

from DataBase2 import Student, Semester, Lesson, Professor, Discipline, Visitation, LessonType, Group
from Domain.Aggregation.Lessons import lessons_by_date
from Domain.Aggregation.Visitations import visitations_rate
from NN.OneHot import OneHotLessonIndex, OneHotLessonType, OneHotLessonWeek, OneHot


def make_train_data(lessons, student, semester):
    visitations = set(Visitation.of(student))

    X = []
    Y = []

    professor_one_hot = OneHot(len(Professor.of(lessons)), lambda x: x.professor.full_name())
    discipline_one_hot = OneHot(len(Discipline.of(lessons)), lambda x: x.discipline.full_name())

    lesson_day_one_hot = OneHot(6, lambda x: x.date.weekday())

    lesson_index_one_hot = OneHotLessonIndex()
    lesson_type_one_hot = OneHotLessonType(4)
    lesson_week_one_hot = OneHotLessonWeek(18)

    group_rate = visitations_rate(Group.of(student, semester)).rate(2)

    for index, lesson in enumerate(lessons):
        lesson_count_one_hot = OneHot(6, lambda x: len(lessons_by_date(student, lesson.date.date())))
        if lesson.completed:
            input_data = []
            input_data.extend(lesson_index_one_hot[lesson])
            input_data.extend(lesson_type_one_hot[lesson])
            input_data.extend(lesson_week_one_hot[lesson])
            input_data.extend(lesson_day_one_hot[lesson])
            input_data.extend(professor_one_hot[lesson])
            input_data.extend(discipline_one_hot[lesson])
            input_data.append(group_rate)
            input_data.append(visitations_rate(lessons[:index]).rate())
            input_data.extend(lesson_count_one_hot[lesson])

            output_data = [int(bool(len(set(Visitation.of(lesson)) & visitations)))]

            X.append(input_data)
            Y.append(output_data)

    return X, Y


def ananlyse_student(student: Student, semester: Semester):
    """

    Входы сети:
        время занятия 6 входов [0 или 1],
        тип занятия 4 входа [0 или 1],
        неделя занятия 18 входов [0 или 1],
        преподаватель N входов [0 или 1],
        дисциплина M входов [0 или 1],
        общий уровень посещений в группе 1 вход [0;1],
        уровень посещений в группе до текущего занятия [0;1],
        количество занятий в день 6 входов [0 или 1].

    Выход системы:
        посещений 1 выход [0 или 1]
        уважительный пропуск 1 выход [0 или 1]

    :param student:
    :param semester:
    :return:
    """

    def one_hot(values: Set, size: int = None):
        if size is None:
            size = len(values)
        d = dict()
        for i, item in enumerate(values):
            p = [0 for _ in range(size)]
            p[i] = 1
            d[item] = p

        return d

    lessons = Lesson.of(student, semester=semester)
    disciplines = Discipline.of(lessons)
    professors = Professor.of(lessons)

    input_size = 6 + 4 + 18 + 6 + len(professors) + len(disciplines) + 1 + 1 + 6
    input_layer = Input((input_size,))

    output_layer = Dense(1, activation='sigmoid', kernel_initializer=keras.initializers.Zeros())(input_layer)

    model = Model(inputs=input_layer, outputs=output_layer)

    model.compile('adam', loss='mean_squared_error')

    X, Y = make_train_data(lessons, student, semester)

    X = np.array(X)
    Y = np.array(Y)

    res = model.fit(X, Y, epochs=2500, shuffle=True, verbose=0)
    acc = model.evaluate(X, Y)

    def param(index):
        if index < 6:
            return f'Занятие №{index + 1}', 'Время занятия'
        if index < 10:
            lesson_type = LessonType.get(id=index - 6)
            if lesson_type is None:
                return 'None', 'None'
            return lesson_type.full_name(), 'Тип занятия'
        if index < 28:
            return f'{index - 10} неделя', 'Номер недели'
        if index < 34:
            return ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"][34 - index-1], 'День недели'
        if index < 34 + len(professors):
            return professors[index - 34].short_name(), 'Преподаватель'
        if index < 34 + len(professors) + len(disciplines):
            return disciplines[index - 34 - len(professors)].short_name(), 'Дисциплина'
        if index < 34 + len(professors) + len(disciplines) + 2:
            return f'Посещения в группе {["всего", "до этого дня"][index - (len(professors) + len(disciplines) + 2)]}', \
                   "Общая атмосфера"
        return f"{index - (34 + len(professors) + len(disciplines) + 2)+1} занятий", "Кол-во занятий"

    weights = model.get_weights()
    df = DataFrame({
                       'Влияние': weight[0],
                       'Параметр': param(index)[0],
                       'Тип': param(index)[1]
                   } for index, weight in enumerate(weights[0]))
    return df, acc


if __name__ == '__main__':

    total = None
    count = 0
    accs = []
    for student in Student.of(Group.get(id=3)):
        df, acc = ananlyse_student(student, Semester.of(student))
        accs.append(acc)
        if total is None:
            print(df)
            total = df
        else:
            total['Влияние'] += df['Влияние']
        count += 1
        print(student, acc)
        # print(df)
    total['Влияние'] = total['Влияние'] / count
    total = total.sort_values('Влияние')
    print(max(accs), sum(accs) / len(accs), min(accs))
    print(total)
