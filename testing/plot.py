from DataBase2 import Student
from Domain.Plot.plot import plot

if __name__ == '__main__':
    plot(Student.get(id=22))
