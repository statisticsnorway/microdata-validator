import json
from typing import List


class PatchingError(Exception):
    pass


class MetadataException(Exception):
    pass


class TimePeriod:
    start: int
    stop: int

    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def to_dict(self) -> dict:
        if self.stop is not None:
            return {"start": self.start, "stop": self.stop}
        else:
            return {"start": self.start}


class KeyType:
    name: str
    label: str
    description: str

    def __init__(self, unit_type_dict: dict):
        self.name = unit_type_dict["name"]
        self.label = unit_type_dict["label"]
        self.description = unit_type_dict["description"]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description
        }

    def patch(self, other: 'KeyType'):
        if other is None:
            raise PatchingError(
                'Can not delete KeyType'
            )
        if self.name != other.name:
            raise PatchingError(
                'Can not change keyType name from '
                f'"{self.name}" to "{other.name}"'
            )
        self.label = other.label
        self.description = other.description


class CodeListItem:
    category: str
    code: str

    def __init__(self, category: str, code: str):
        self.category = category
        self.code = code

    def to_dict(self) -> dict:
        return {"category": self.category, "code": self.code}

    def patch(self, other: 'CodeListItem'):
        if other is None:
            raise PatchingError(
                'Can not delete CodeListItem'
            )
        if self.code != other.code:
            raise PatchingError(
                'Can not change CodeListItem code from '
                f'"{self.code}" to "{other.code}"'
            )
        self.category = other.category


class ValueDomain:
    description: str
    unit_of_measure: str
    code_list: List[CodeListItem]
    missing_values: List[str]
    is_described_value_domain: bool
    is_enumerated_value_domain: bool

    def __init__(self, value_domain_dict: dict):
        self.is_enumerated_value_domain = (
            "codeList" in value_domain_dict
            and "description" not in value_domain_dict
            and "unitOfMeasure" not in value_domain_dict
        )
        self.is_described_value_domain = (
            "description" in value_domain_dict
            and "codeList" not in value_domain_dict
            and "missingValues" not in value_domain_dict
        )
        if self.is_described_value_domain:
            self.description = value_domain_dict.get("description")
            self.unit_of_measure = value_domain_dict.get("unitOfMeasure", None)
            self.code_list = None
            self.missing_values = None
        elif self.is_enumerated_value_domain:
            self.code_list = []
            if "codeList" in value_domain_dict:
                self.code_list = [
                    CodeListItem(item["category"], item["code"])
                    for item in value_domain_dict["codeList"]
                ]
            self.missing_values = []
            if "missingValues" in value_domain_dict:
                self.missing_values = [
                    missing_value for missing_value
                    in value_domain_dict["missingValues"]
                ]
            self.code_list = None if self.code_list == [] else self.code_list
            self.missing_values = (
                None if self.missing_values == [] else self.missing_values
            )
            self.description = None
            self.unit_of_measure = None
        else:
            raise MetadataException('Invalid ValueDomain')

    def to_dict(self) -> dict:
        if self.is_described_value_domain:
            dict_representation = {
                "description": self.description,
                "unitOfMeasure": self.unit_of_measure,
            }
        elif self.is_enumerated_value_domain:
            dict_representation = {
                "codeList": [
                    code_item.to_dict() for code_item in self.code_list
                ],
                "missingValues": [
                    missing_value for missing_value in self.missing_values
                ]
            }
        return {
            key: value for key, value in dict_representation.items()
            if value not in [None]
        }

    def patch(self, other: 'ValueDomain'):
        if other is None:
            raise PatchingError(
                'Can not delete ValueDomain'
            )
        if self.is_described_value_domain:
            self.description = other.description
            if self.unit_of_measure != other.unit_of_measure:
                raise PatchingError(
                    'Can not change ValueDomain unitOfMeasure from '
                    f'"{self.unit_of_measure}" to "{other.unit_of_measure}"'
                )
        elif self.is_enumerated_value_domain:
            if other.code_list is None:
                raise PatchingError(
                    'Can not delete code list'
                )
            if self.missing_values != other.missing_values:
                raise PatchingError(
                    'Can not change ValueDomain missingValues from '
                    f'"{self.missing_values}" to "{other.missing_values}"'
                )
            if len(self.code_list) != len(other.code_list):
                raise PatchingError(
                    'Can not add or remove codes from ValueDomain codeList'
                )
            for idx in range(len(self.code_list)):
                self.code_list[idx].patch(other.code_list[idx])


class RepresentedVariable:
    description: str
    valid_period: TimePeriod
    value_domain: ValueDomain

    def __init__(self, represented_variable_dict: dict):
        self.description = represented_variable_dict["description"]
        self.valid_period = TimePeriod(
            represented_variable_dict["validPeriod"]["start"],
            represented_variable_dict["validPeriod"].get("stop", None)
        )
        self.value_domain = ValueDomain(
            represented_variable_dict["valueDomain"]
        )

    def to_dict(self):
        return {
            "description": self.description,
            "validPeriod": self.valid_period.to_dict(),
            "valueDomain": self.value_domain.to_dict()
        }

    def patch(self, other: 'RepresentedVariable'):
        if other is None:
            raise PatchingError(
                'Can not delete RepresentedVariable'
            )
        self.description = other.description
        self.value_domain.patch(other.value_domain)


class Variable:
    name: str
    label: str
    data_type: str
    format: str
    variable_role: str
    key_type: KeyType
    represented_variables: List[RepresentedVariable]

    def __init__(self, variable_dict: dict):
        self.name = variable_dict["name"]
        self.label = variable_dict["label"]
        self.data_type = variable_dict["dataType"]
        self.variable_role = variable_dict["variableRole"]
        self.format = variable_dict.get("format", None)
        self.key_type = (
            None if "keyType" not in variable_dict
            else KeyType(variable_dict["keyType"])
        )
        self.represented_variables = [
            RepresentedVariable(represented_variable_dict)
            for represented_variable_dict
            in variable_dict["representedVariables"]
        ]

    def get_key_type_name(self):
        return None if self.key_type is None else self.key_type.name

    def to_dict(self) -> dict:
        dict_representation = {
            "name": self.name,
            "label": self.label,
            "dataType": self.data_type,
            "variableRole": self.variable_role,
            "representedVariables": [
                represented_variable.to_dict()
                for represented_variable in self.represented_variables
            ]
        }
        if self.format is not None:
            dict_representation["format"] = self.format
        if self.key_type is not None:
            dict_representation["keyType"] = self.key_type.to_dict()
        return dict_representation

    def patch(self, other: 'Variable'):
        if other is None:
            raise PatchingError(
                'Can not delete Variable'
            )
        if (
            self.name != other.name or
            self.data_type != other.data_type or
            self.format != other.format or
            self.variable_role != other.variable_role
        ):
            raise PatchingError(
                'Illegal change to one of these variable fields: '
                '[name, dataType, format, variableRole]]'
            )
        self.label = other.label
        if self.key_type is None and other.key_type is not None:
            raise PatchingError(
                'Can not change keyType'
            )
        if self.key_type is not None:
            self.key_type.patch(other.key_type)
        if len(self.represented_variables) != len(other.represented_variables):
            raise PatchingError(
                'Can not add or delete represented variables.'
            )
        for idx in range(len(self.represented_variables)):
            self.represented_variables[idx].patch(
                other.represented_variables[idx]
            )


class IdentifierVariable(Variable):
    pass


class MeasureVariable(Variable):
    pass


class AttributeVariable(Variable):
    pass


class Metadata:
    name: str
    temporality: str
    language_code: str
    population_description: str
    subject_fields: List[str]
    temporal_coverage: TimePeriod
    measure_variable: MeasureVariable
    identifier_variable: IdentifierVariable
    start_variable: AttributeVariable
    stop_variable: AttributeVariable

    def __init__(self, metadata_dict: dict):
        self.name = metadata_dict["name"]
        self.temporality = metadata_dict["temporality"]
        self.language_code = metadata_dict["languageCode"]
        self.population_description = (
            metadata_dict["populationDescription"]
        )
        self.subject_fields = metadata_dict["subjectFields"]
        self.temporal_coverage = TimePeriod(
            metadata_dict["temporalCoverage"]["start"],
            metadata_dict["temporalCoverage"].get("stop", None)
        )
        self.measure_variable = MeasureVariable(
            metadata_dict["measureVariable"]
        )
        self.identifier_variable = IdentifierVariable(
            metadata_dict["identifierVariables"][0]
        )
        self.start_variable = AttributeVariable(
            next(
                variable for variable in metadata_dict["attributeVariables"]
                if variable["variableRole"] == "START_TIME"
            )
        )
        self.stop_variable = AttributeVariable(
            next(
                variable for variable in metadata_dict["attributeVariables"]
                if variable["variableRole"] == "STOP_TIME"
            )
        )

    def get_identifier_key_type_name(self):
        return self.identifier_variable.get_key_type_name()

    def get_measure_key_type_name(self):
        return self.measure_variable.get_key_type_name()

    def patch(self, other: 'Metadata'):
        if other is None:
            raise PatchingError(
                'Can not patch with NoneType Metadata'
            )
        if (
            self.name != other.name or
            self.temporality != other.temporality or
            self.language_code != other.language_code
        ):
            raise PatchingError(
                'Can not change these metadata fields '
                '[name, temporality, languageCode]'
            )
        self.population_description = other.population_description
        self.subject_fields = other.subject_fields
        self.measure_variable.patch(other.measure_variable)
        self.identifier_variable.patch(other.identifier_variable)
        self.start_variable.patch(other.start_variable)
        self.stop_variable.patch(other.stop_variable)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "temporality": self.temporality,
            "languageCode": self.language_code,
            "populationDescription": self.population_description,
            "subjectFields": self.subject_fields,
            "temporalCoverage": self.temporal_coverage.to_dict(),
            "measureVariable": self.measure_variable.to_dict(),
            "identifierVariables": [self.identifier_variable.to_dict()],
            "attributeVariables": [
                self.start_variable.to_dict(),
                self.stop_variable.to_dict()
            ]
        }

    def save_to_file(self, file_path: str):
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f)
