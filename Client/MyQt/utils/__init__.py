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
        url = parse.urlparse(Args().host)
        print(url)
        if url.netloc == '':
            socket.create_connection((Args().host.split(':')[0], Args().host.split(':')[1]))
        else:
            socket.create_connection((url.hostname, url.port))
        return True
    except OSError:
        pass
    return False
