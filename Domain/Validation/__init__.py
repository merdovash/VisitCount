class ExcelValidation:
    @staticmethod
    def group_name(raw: str) -> str:
        assert isinstance(raw, str), TypeError(type(raw))

        return raw.split(' ')[1]
