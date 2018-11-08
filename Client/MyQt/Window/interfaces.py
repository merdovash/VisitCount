class IChildWindow():
    def showAsChild(self, *args):
        raise NotImplementedError()

    def closeSelf(self):
        print('closing self')
        self._parentWindow.closeDialog(self)

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
            if isinstance(self.child_window, IParentWindow):
                self.child_window.setDialog(dialog, *args)
            else:
                self.child_pool.append((dialog, args))
        else:
            if isinstance(dialog, IChildWindow):
                self.child_window = dialog
                self.child_window.setParentWindow(self)
                self.child_window.showAsChild(*args)
            else:
                raise NotImplementedError(type(dialog))

    def closeDialog(self, dialog):
        if self.child_window is not None:
            if dialog == self.child_window:
                self.child_window.close()
                self.child_window = None
            else:
                raise Exception(f'dialog {dialog} closing different dialog {self.child_window}')
        else:
            raise Warning('no dialog to close (already None)')

        if len(self.child_pool) > 0:
            self.setDialog(*self.child_pool.pop(0))

        self.raise_()

    def hasDialog(self):
        return self.child_window is not None
