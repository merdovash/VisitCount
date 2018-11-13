from Domain.functools import List


class ExcelValidation:
    @staticmethod
    def group_name(raw: str) -> str or List[str]:
        assert isinstance(raw, str), TypeError(type(raw))

        splited = raw.split(' ')

        group_names = splited[1]

        groups = group_names.split(',')

        print(groups)

        return groups
