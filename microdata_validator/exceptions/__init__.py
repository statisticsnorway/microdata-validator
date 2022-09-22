class UnregisteredUnitTypeError(Exception):
    pass


class ParseMetadataError(Exception):
    pass


class InvalidDataException(Exception):

    def __init__(self, message: str, data_errors: list):
        self.data_errors = data_errors
        Exception.__init__(self, message)
