import json

import pytest

from microdata_validator import Metadata, PatchingError

RESOURCE_DIR = 'tests/resources/metadata_model'


def test_patch_metadata_with_code_list():
    updated = load_file(f'{RESOURCE_DIR}/SYNT_BEFOLKNING_KJOENN_enumerated_update.json')
    original = load_file(f'{RESOURCE_DIR}/SYNT_BEFOLKNING_KJOENN_enumerated.json')
    expected = load_file(f'{RESOURCE_DIR}/SYNT_BEFOLKNING_KJOENN_enumerated_patched.json')

    orig = Metadata(original)
    orig.patch(Metadata(updated))
    assert orig.to_dict() == expected


def test_patch_metadata_without_code_list():
    updated = load_file(f'{RESOURCE_DIR}/SYNT_PERSON_INNTEKT_described_update.json')
    original = load_file(f'{RESOURCE_DIR}/SYNT_PERSON_INNTEKT_described.json')
    expected = load_file(f'{RESOURCE_DIR}/SYNT_PERSON_INNTEKT_described_patched.json')

    orig = Metadata(original)
    orig.patch(Metadata(updated))
    assert orig.to_dict() == expected


def test_patch_metadata_illegal_fields_changes():
    """
    The "updated" contains randomly chosen fields that are not allowed to be changed.
    """
    updated = load_file(f'{RESOURCE_DIR}/SYNT_BEFOLKNING_KJOENN_enumerated_illegal_update.json')
    original = load_file(f'{RESOURCE_DIR}/SYNT_BEFOLKNING_KJOENN_enumerated.json')

    with pytest.raises(PatchingError) as e:
        orig = Metadata(original)
        orig.patch(Metadata(updated))

    assert 'Can not change these metadata fields [name, temporality, languageCode]' in str(e)


def load_file(file_name: str):
    with open(file_name) as f:
        source = json.load(f)
    return source
