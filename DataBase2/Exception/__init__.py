class VisitationAlreadyExist(Exception):
    def __init__(self):
        super().__init__('Visitation already exist in database')
