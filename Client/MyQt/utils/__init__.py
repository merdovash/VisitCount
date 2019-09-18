import sys

from PyQt5.QtWidgets import QApplication

from Parser import Args


def simple_show(widget_class, *args, **kwargs):
    app = QApplication(sys.argv)

    widget = widget_class(*args, **kwargs)
    widget.showMaximized()

    sys.exit(app.exec_())


def check_connection() -> bool:
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        import socket
        from urllib import parse
        address = Args().host.address
        url = parse.urlparse(address)
        print(url)
        if url.netloc == '':
            socket.create_connection((address.split(':')[0], address.split(':')[1]))
        else:
            socket.create_connection((url.hostname, url.port))
        return True
    except OSError:
        pass
    return False
