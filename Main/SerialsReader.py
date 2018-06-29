import serial
import threading

instance = None


class RFIDReader(threading.Thread):
    connection = None

    def __init__(self, method):
        self.state = True
        self.method = method
        super().__init__()

        if RFIDReader.connection is None:
            for i in range(12):
                try:
                    RFIDReader.connection = serial.Serial('COM' + str(i))
                    print("Connected to COM" + str(i))
                    break
                except serial.serialutil.SerialException as e:
                    print(e)
        RFIDReader.instance = self

    def run(self):
        while self.state:
            if RFIDReader.connection.read():
                a = RFIDReader.connection.readline().decode('UTF-8')
                if (len(a)) > 10:
                    number = a.split(",")[1].replace("\r\n", "")
                    self.method(number)


def getReader() -> RFIDReader:
    global instance

    if instance is None:
        instance = RFIDReader(lambda x: 0)
        instance.start()
    return instance
