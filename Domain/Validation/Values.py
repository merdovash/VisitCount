class Validate:
    @staticmethod
    def card_id(val):
        return val is not None and val != '' and val != 'None'
