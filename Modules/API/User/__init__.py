from Modules.API import API


class UserAPI(API):
    __address__ = API.__address__ + '/user'