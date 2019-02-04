import threading
from typing import Callable

import serial
from PyQt5.QtCore import QThread, pyqtSignal
from serial import SerialException

from Client.Reader import IReader
from Domain.Exception.RFIDReader import RFIDReaderNotFoundException, RFIDReaderHasGoneAwayException


def nothing(card_id):
    print(card_id)


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


class RFIDReader(IReader, QThread):
    inst = None

    NotFound = 0
    Found = 1

    card_id = pyqtSignal('PyQt_PyObject')

    @staticmethod
    def instance(case="найти считыватель", **kwargs) -> 'RFIDReader':
        if RFIDReader.inst is None:
            RFIDReader.inst = RFIDReader(**kwargs)
            if RFIDReader.inst.status == RFIDReader.Found:
                RFIDReader.inst.start()
            else:
                RFIDReader.inst = None
                # traceback.print_stack()
                raise RFIDReaderNotFoundException(case, **kwargs)

        RFIDReader.inst.case = case
        return RFIDReader.inst

    def __init__(self, **kwargs):
        self.case = ''
        self.state = True
        self.connection = None
        super().__init__()
        self.status = RFIDReader.NotFound

        self.daemon = True
        self.card_id.connect(kwargs.get('method', nothing))
        self.error_callback = kwargs.get('error_callback', None)

        for i in range(12):
            try:
                self.connection = serial.Serial(f'COM{i}')
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException as e:
                pass

            try:
                self.connection = serial.Serial(f"/dev/ttyUSB{i}")
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException as e:
                pass

    def run(self):
        while self.state:
            try:
                if self.connection.read():
                    a = self.connection.readline().decode('UTF-8')
                    if (len(a)) > 10:
                        number = a.split(",")[1].replace("\r\n", "")
                        self.card_id.emit(number)
            except SerialException as serial_excpetion:
                RFIDReader.inst = None
                if 'read failed' in str(serial_excpetion):
                    self.state = False
                    RFIDReader.status = RFIDReader.NotFound
                    raise RFIDReaderHasGoneAwayException(self.case, callback=self.error_callback)
                else:
                    print(serial_excpetion)

        self.terminate()
        RFIDReader.inst = None

    def on_read(self, method: Callable[[int], None]):
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

    def close(self):
        self.state = False
