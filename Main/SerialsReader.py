import serial
import threading

try:
    ser = serial.Serial('COM3')
except serial.serialutil.SerialException as e:
    print(e)
    exit(code=3)


class SerialThread(threading.Thread):
    def __init__(self, method):
        self.state = True
        self.method = method
        super().__init__()

    def run(self):
        while self.state:
            if ser.read():
                a = ser.readline().decode('UTF-8')
                if (len(a)) > 10:
                    number = a.split(",")[1].replace("\r\n","")
                    self.method(number)
