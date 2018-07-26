import serial
import threading


def nothing(card_id):
    pass


class RFIDReaderNotFoundException(Exception):
    def __init__(self):
        self.args = ["RFID Reader not found"]


class RFIDReader(threading.Thread):
    inst = None

    NotFound = 0
    Found = 1

    @staticmethod
    def instance() -> 'RFIDReader':
        print("getting instance", RFIDReader.inst)
        if RFIDReader.inst is None:
            print("create new instance")
            RFIDReader.inst = RFIDReader(lambda x: 0)
            if RFIDReader.inst.status == RFIDReader.Found:
                RFIDReader.inst.start()
            else:
                RFIDReader.inst = None
                raise RFIDReaderNotFoundException()
        return RFIDReader.inst

    def __init__(self, method=nothing):
        self.state = True
        self.onRead = method
        self.connection = None
        super().__init__()
        self.status = RFIDReader.NotFound

        for i in range(12):
            try:
                self.connection = serial.Serial('COM' + str(i))
                print("Connected to COM" + str(i))
                self.status = RFIDReader.Found
                break
            except serial.serialutil.SerialException as e:
                print(e)

    def run(self):
        while self.state:
            if self.connection.read():
                a = self.connection.readline().decode('UTF-8')
                if (len(a)) > 10:
                    number = a.split(",")[1].replace("\r\n", "")
                    self.onRead(number)

    def onReadOnce(self, method):
        self.temp = self.onRead
        print(self.temp)

        def f(card_id):
            method(card_id)
            self.onRead = self.temp

        self.onRead = f
        print(self.temp)

    def remove_temporary_function(self):
        self.onRead = self.temp
