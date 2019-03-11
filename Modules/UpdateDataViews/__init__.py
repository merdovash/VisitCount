from typing import List

from DataBase2 import DataView
from Domain.Structures.DictWrapper import Structure

address = '/data_views'


class DataViewsResponse(Structure):
    views: List[DataView]

    def __init__(self, views):
        self.views = list()

        for view in views:
            if isinstance(view, dict):
                view = DataView.get_or_create(**view)
            self.views.append(view)
