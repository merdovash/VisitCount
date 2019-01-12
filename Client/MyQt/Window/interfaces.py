import warnings

from DataBase2 import Session


class IChildWindow():
    def showAsChild(self, *args):
        raise NotImplementedError()

    def closeSelf(self):
        print('closing self')
        if isinstance(self, IParentWindow) and self.child_window is not None:
            self.child_window.closeSelf()
        self._parentWindow.closeDialog(self)
        self.close()

    def setParentWindow(self, window):
        self._parentWindow = window


class IParentWindow:
    def __init__(self):
        self.child_window = None
        self.child_pool = []

    def setDialog(self, dialog, *args):
        if dialog == self:
            dialog.showNormal()
            dialog.activateWindow()

        elif self.child_window is not None:
            if isinstance(self.child_window, IChildWindow):
                self.child_window = [self.child_window]
                dialog.setParentWindow(self)
                dialog.showAsChild(*args)
                self.child_window.append(dialog)

            elif isinstance(self.child_window, list):
                dialog.setParentWindow(self)
                dialog.showAsChild(*args)
                self.child_window.append(dialog)

        else:
            if isinstance(dialog, IChildWindow):
                self.child_window = dialog
                self.child_window.setParentWindow(self)
                self.child_window.showAsChild(*args)

            else:
                raise NotImplementedError(type(dialog))

    def closeDialog(self, dialog):
        if self.child_window is not None:
            if isinstance(self.child_window, list):
                if dialog in self.child_window:
                    self.child_window.remove(dialog)
                    if len(self.child_window) == 1:
                        self.child_window = self.child_window[0]
                else:
                    # raise AttributeError(f'no such child ({dialog}) in {self.child_window}')
                    pass

            elif isinstance(self.child_window, IChildWindow):
                if self.child_window == dialog:
                    self.child_window = None

            else:
                raise Exception('idk')
        else:
            warnings.warn('no dialog to close (already None)')

        self.raise_()

    def hasDialog(self):
        return self.child_window is not None


class IDataBaseUser:
    def __init__(self, session=None):
        if session is None:
            self.session = Session()
        else:
            self.session = Session()
