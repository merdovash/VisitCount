import sys

from PyQt5.QtWidgets import QApplication


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
        from Parser import client_args
        from urllib import parse
        url = parse.urlparse(client_args.host)
        if url.netloc =='':
            socket.create_connection((client_args.host.split(':')[0], client_args.host.split(':')[1]))
        else:
            socket.create_connection((client_args.host, 80))
        return True
    except OSError:
        pass
    return False
