import numpy as np

from DataBase2 import Student, Semester, Professor
from NN.OneHot import OneHotLessonIndex, OneHotLessonType, OneHotLessonWeek, OneHot, Inputer


def ananlyse_student(student: Student, semester: Semester):
    """

    Входы сети:
        время занятия 6 входов [0 или 1],
        тип занятия 4 входа [0 или 1],
        неделя занятия 18 входов [0 или 1],
        преподаватель N входов [0 или 1],
        дисциплина M входов [0 или 1],
        общий уровень посещений в группе 1 вход [0;1],
        уровень посещений в группе до текущего занятия 2 входа мало или много [0,1],
        количество занятий в день 6 входов [0 или 1],
        деловой подход 1 вход [1].

    Выход системы:
        посещений 1 выход [0 или 1]
        уважительный пропуск 1 выход [0 или 1]

    :param student:
    :param semester:
    :return:
    """

    data = Inputer(obj=student, semester=semester)

    model = data.make_model()

    X, Y = data.make(student)

    X = np.array(X)
    Y = np.array(Y)

    acc = None

    for i in range(10):
        res = model.fit(X, Y, epochs=2500, shuffle=True, verbose=0)
        acc = model.evaluate(X, Y)
        if acc <= 0.05:
            break

    df = data.description()

    return df, acc


class MeanCounter:
    def __init__(self):
        self.df = None
        self.acc = 0
        self.count = 0

    def add(self, df, acc):
        if self.df is None:
            self.df = df
        else:
            self.df['Влияние'] += df['Влияние']

        self.count += 1
        self.acc += acc

    def calc(self):
        df = self.df
        df['Влияние'] = self.df['Влияние'] / self.count
        return df, self.acc / self.count


def analyze(obj, semester):
    mean = MeanCounter()
    data = Inputer(obj, semester)

    for student in Student.of(obj, semester=semester):

        model = data.make_model()

        X, Y = data.make(student)

        X, Y = np.array(X), np.array(Y)

        for i in range(10):
            res = model.fit(X, Y, epochs=500+i*500, initial_epoch=i*500, shuffle=True, verbose=0)
            acc = model.evaluate(X, Y)
            if acc <= 0.05:
                break

        mean.add(data.description(), model.evaluate(X, Y))

    return mean.calc()


if __name__ == '__main__':
    professor = Professor.get(id=1)
    df, acc = analyze(professor, Semester.of(professor))

    df.to_excel('res.xlsx')
    print(acc)
