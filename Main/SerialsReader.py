import serial
import threading


def nothing(card_id):
    pass


class RFIDReader(threading.Thread):
    inst = None

    @staticmethod
    def instance():
        print("getting instance", RFIDReader.inst)
        if RFIDReader.inst is None:
            print("create new instance")
            RFIDReader.inst = RFIDReader(lambda x: 0)
            RFIDReader.inst.start()
        return RFIDReader.inst

    def __init__(self, method=nothing):
        self.state = True
        self.method = method
        self.connection = None
        super().__init__()

        for i in range(12):
            try:
                self.connection = serial.Serial('COM' + str(i))
                print("Connected to COM" + str(i))
                break
            except serial.serialutil.SerialException as e:
                print(e)

    def run(self):
        while self.state:
            if self.connection.read():
                a = self.connection.readline().decode('UTF-8')
                if (len(a)) > 10:
                    number = a.split(",")[1].replace("\r\n", "")
                    self.method(number)
