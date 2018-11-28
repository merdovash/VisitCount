from abc import abstractmethod


class OnRead:
    @abstractmethod
    def __call__(self, card_id):
        raise NotImplementedError()
