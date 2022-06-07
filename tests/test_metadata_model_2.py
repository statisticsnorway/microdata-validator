import json

import pytest

from microdata_validator import Metadata, PatchingError

PATCH_METADATA_DIR = 'tests/resources/metadata_model'
WITH_CODE_LIST_DIR = f'{PATCH_METADATA_DIR}/dataset_with_code_list'
WITHOUT_CODE_LIST_DIR = f'{PATCH_METADATA_DIR}/dataset_without_code_list'
INVALID_DIR = f'{PATCH_METADATA_DIR}/invalid'


def test_patch_metadata_with_code_list():
    source = load_file(f'{WITH_CODE_LIST_DIR}/source_SYNT_BEFOLKNING_KJOENN.json')
    destination = load_file(f'{WITH_CODE_LIST_DIR}/destination_SYNT_BEFOLKNING_KJOENN.json')
    expected = load_file(f'{WITH_CODE_LIST_DIR}/expected_SYNT_BEFOLKNING_KJOENN.json')

    s = Metadata(destination)
    s.patch(Metadata(source))
    assert s.to_dict() == expected


def test_patch_metadata_without_code_list():
    source = load_file(f'{WITHOUT_CODE_LIST_DIR}/source_SYNT_PERSON_INNTEKT.json')
    destination = load_file(f'{WITHOUT_CODE_LIST_DIR}/destination_SYNT_PERSON_INNTEKT.json')
    expected = load_file(f'{WITHOUT_CODE_LIST_DIR}/expected_SYNT_PERSON_INNTEKT.json')

    s = Metadata(destination)
    s.patch(Metadata(source))
    assert s.to_dict() == expected


def test_patch_metadata_illegal_fields_changes():
    """
    The source contains randomly chosen fields that are not allowed to be changed.
    """
    source = load_file(f'{INVALID_DIR}/source_SYNT_BEFOLKNING_KJOENN.json')
    destination = load_file(f'{INVALID_DIR}/destination_SYNT_BEFOLKNING_KJOENN.json')

    with pytest.raises(PatchingError) as e:
        s = Metadata(destination)
        s.patch(Metadata(source))

    assert 'Can not change these metadata fields [name, temporality, languageCode]' in str(e)


def load_file(file_name: str):
    with open(file_name) as f:
        source = json.load(f)
    return source
