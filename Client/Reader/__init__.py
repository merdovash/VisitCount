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
