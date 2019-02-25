from collections import namedtuple

from Modules.AutoNotification.ServerSide import init

student_loss = namedtuple('student_loss', 'student loss total_lessons')

if __name__ == '__main__':
    init()
