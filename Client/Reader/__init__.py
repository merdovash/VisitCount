import errno
import os
import re
import subprocess
import sys


class IReader:
    def on_read(self, method):
        raise NotImplementedError()

    def stop_read(self):
        raise NotImplementedError()

    def on_read_once(self, method):
        raise NotImplementedError()

    def remove_temporary_function(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class ReaderFinder:
    class UserException(Exception):
        pass

    class NotFoundException(Exception):
        pass

    class ParsingIdException(Exception):
        ...

    class NoPermissionException(Exception):
        ...


    finder = re.compile(r'(?:ID\s([0-9]{4}):([0-9]{4}))')

    def __init__(self):
        pass

    def get_list_of_usb(self):
        return subprocess.getoutput('lsusb').split('\n')

    def request_connect(self):
        v = input('Подключите устройство. После подключения нажмите "д"')
        if v in ['y', 'д']:
            return True

    def request_disconnect(self):
        v = input('Отключите устройство. После отключения нажмите "д"')
        if v in ['y', 'д']:
            return True

    def find(self):
        try:
            os.rename('/etc/foo', '/etc/bar')
        except IOError as e:
            if (e[0] == errno.EPERM):
                raise self.NoPermissionException()

        if self.request_disconnect():
            list_without = self.get_list_of_usb()
        else:
            raise self.UserException()

        if self.request_connect():
            usb = set(self.get_list_of_usb()).difference(list_without)
            if len(usb) == 1:
                usb = usb.pop()
                ids = self.finder.findall(usb)
                if len(ids) == 1:
                    print(ids[0])
                    self.prepare(ids[0])
                else:
                    raise self.ParsingIdException()
            else:
                raise self.NotFoundException()
        else:
            raise self.UserException()

    def prepare(self, ids):
        proc = subprocess.call(['sudo', 'modprobe', 'ftdi_sio'])
        print(proc)


if __name__ == '__main__':
    reader_finder = ReaderFinder()
    reader_finder.find()
