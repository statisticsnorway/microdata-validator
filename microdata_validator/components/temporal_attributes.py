from copy import deepcopy

from microdata_validator.exceptions import InvalidTemporalityType


DESCRIPTIONS = {
    "FIXED": {
        "START": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
        },
        "STOP": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
        },
    },
    "ACCUMULATED": {
        "START": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
        },
        "STOP": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
        },
    },
    "STATUS": {
        "START": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
        },
        "STOP": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
        },
    },
    "EVENT": {
        "START": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Startdato"},
                {"languageCode": "en", "value": "Start date"},
            ],
        },
        "STOP": {
            "description": [
                {
                    "languageCode": "no",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
                {
                    "languageCode": "en",
                    "value": "Startdato/måletidspunktet for hendelsen",
                },
            ],
            "name": [
                {"languageCode": "no", "value": "Stoppdato"},
                {"languageCode": "en", "value": "Stop date"},
            ],
        },
    },
}

START_VARIABLE_DEFINITION = {
    "variableRole": "START_TIME",
    "shortName": "START",
    "dataType": "DATE",
    "valueDomain": {
        "description": [
            {
                "languageCode": "no",
                "value": "Dato oppgitt i dager siden 1970-01-01"
            }
        ]
    },
}
STOP_VARIABLE_DEFINITION = {
    "variableRole": "STOP_TIME",
    "shortName": "STOP",
    "dataType": "DATE",
    "valueDomain": {
        "description": [
            {
                "languageCode": "no",
                "value": "Dato oppgitt i dager siden 1970-01-01"
            }
        ]
    },
}


def generate_start_time_attribute(temporality_type: str):
    try:
        start_attribute = deepcopy(START_VARIABLE_DEFINITION)
        start_attribute.update(DESCRIPTIONS[temporality_type]["START"])
        return start_attribute
    except KeyError as e:
        raise InvalidTemporalityType(temporality_type) from e


def generate_stop_time_attribute(temporality_type: str):
    try:
        stop_attribute = deepcopy(STOP_VARIABLE_DEFINITION)
        stop_attribute.update(DESCRIPTIONS[temporality_type]["STOP"])
        return stop_attribute
    except KeyError as e:
        raise InvalidTemporalityType(temporality_type) from e
