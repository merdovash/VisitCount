import threading

import serial

from Client.Reader import IReader


def nothing(card_id):
    pass


class RFIDReaderFunction:
    __slots__ = ('func', 'name', 'on_read', 'on_start', 'on_finish')

    def __init__(self, func, name=None, msg_on_start=None, msg_on_read=None, msg_on_finish=None):
        self.func = func
        self.name = name if name is not None else func.__name__
        self.on_start = msg_on_start
        self.on_read = msg_on_read
        self.on_finish = msg_on_finish

    def start(self):
        self.on_start()
        RFIDReader.instance().on_read(self)

    def finish(self):
        self.on_finish()
        RFIDReader.instance().stop_read()

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
        self.on_read(*args, **kwargs)


class RFIDReaderNotFoundException(Exception):
    def __init__(self):
        self.args = ["RFID Reader not found"]


class RFIDReader(IReader, threading.Thread):
    inst = None

    NotFound = 0
    Found = 1

    @staticmethod
    def instance() -> 'RFIDReader':
        if RFIDReader.inst is None:
            RFIDReader.inst = RFIDReader(lambda x: 0)
            if RFIDReader.inst.status == RFIDReader.Found:
                RFIDReader.inst.start()
            else:
                RFIDReader.inst = None
                # traceback.print_stack()
                raise RFIDReaderNotFoundException()

        return RFIDReader.inst

    def __init__(self, method=nothing):
        self.state = True
        self._method = method
        self.connection = None
        super().__init__()
        self.status = RFIDReader.NotFound

        for i in range(12):
            try:
                self.connection = serial.Serial('COM' + str(i))
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException as e:
                pass

    def run(self):
        while self.state:
            if self.connection.read():
                a = self.connection.readline().decode('UTF-8')
                if (len(a)) > 10:
                    number = a.split(",")[1].replace("\r\n", "")
                    self._method(number)

    def on_read(self, method):
        self._method = method

    def stop_read(self):
        self._method = nothing

    def on_read_once(self, method):
        self.temp = self._method

        def f(card_id):
            method(card_id)
            self._method = self.temp

        self._method = f

    def remove_temporary_function(self):
        self._method = self.temp
