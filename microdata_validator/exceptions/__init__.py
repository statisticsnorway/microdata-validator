class UnregisteredUnitTypeError(Exception):
    ...


class ParseMetadataError(Exception):
    ...


class InvalidTemporalityType(Exception):
    ...


class InvalidIdentifierType(Exception):
    ...


class InvalidDatasetName(Exception):
    ...


class InvalidDataException(Exception):

    def __init__(self, message: str, data_errors: list):
        self.data_errors = data_errors
        Exception.__init__(self, message)
