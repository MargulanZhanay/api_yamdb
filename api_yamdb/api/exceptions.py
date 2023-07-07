from rest_framework.exceptions import APIException


class CustomValidation(APIException):
    def __init__(self, detail, field, status_code):
        self.detail = detail
        self.field = field
        self.status_code = status_code
