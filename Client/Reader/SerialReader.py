from typing import Callable

import serial
from PyQt5.QtCore import QThread, pyqtSignal
from serial import SerialException

from Client.Reader import IReader
from Domain.Exception.RFIDReader import RFIDReaderNotFoundException, RFIDReaderHasGoneAwayException


def nothing(card_id):
    print(card_id)


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

        RFIDReader.inst._case = case
        return RFIDReader.inst

    def __init__(self, **kwargs):
        self._case = ''
        self._state = True
        self._connection = None

        self._method = None
        self._temp = None
        super().__init__()
        self.status = RFIDReader.NotFound

        self.daemon = True
        self.card_id.connect(kwargs.get('method', nothing))
        self.error_callback = kwargs.get('error_callback', None)

        for i in range(12):
            try:
                self._connection = serial.Serial(f'COM{i}')
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException:
                pass

            try:
                self._connection = serial.Serial(f"/dev/ttyUSB{i}")
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException:
                pass

    def run(self):
        while self._state:
            try:
                if self._connection.read():
                    a = self._connection.readline().decode('UTF-8')
                    if (len(a)) > 10:
                        number = a.split(",")[1].replace("\r\n", "")
                        self.card_id.emit(number)
            except SerialException as serial_exception:
                RFIDReader.inst = None
                if 'read failed' in str(serial_exception):
                    self._state = False
                    RFIDReader.status = RFIDReader.NotFound
                    raise RFIDReaderHasGoneAwayException(self._case, callback=self.error_callback)
                else:
                    print(serial_exception)

        self.terminate()
        RFIDReader.inst = None

    def on_read(self, method: Callable[[int], None]):
        self._method = method

    def stop_read(self):
        self._method = nothing

    def on_read_once(self, method):
        self._temp = self._method

        def f(card_id):
            method(card_id)
            self._method = self._temp

        self._method = f

    def remove_temporary_function(self):
        self._method = self._temp

    def close(self):
        self._state = False
