import json

import pytest
from microdata_validator import Metadata, PatchingError

RESOURCE_DIR = 'tests/resources/metadata_model'
with open(f'{RESOURCE_DIR}/KREFTREG_DS_described.json') as f:
    TRANSFORMED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_described_update.json') as f:
    UPDATED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_enumerated.json') as f:
    ENUMERATED_TRANSFORMED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_enumerated_update.json') as f:
    ENUMERATED_UPDATED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_enumerated_patched.json') as f:
    PATCHED_ENUMERATED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_described_patched.json') as f:
    PATCHED_METADATA = json.load(f)

with open(f'{RESOURCE_DIR}/KREFTREG_DS_described_illegal_update.json') as f:
    # New variable name on line 18
    ILLEGALLY_UPDATED_METADATA = json.load(f)
with open(f'{RESOURCE_DIR}/KREFTREG_DS_described_deleted_object.json') as f:
    # Deleted keyType object line 34
    DELETED_OBJECT_METADATA = json.load(f)


def test_object():
    transformed_metadata = Metadata(TRANSFORMED_METADATA)
    assert (
        transformed_metadata.get_identifier_key_type_name()
        == 'SYKDOMSTILFELLE'
    )
    assert transformed_metadata.to_dict() == TRANSFORMED_METADATA


def test_patch_described():
    transformed_metadata = Metadata(TRANSFORMED_METADATA)
    updated_metadata = Metadata(UPDATED_METADATA)
    transformed_metadata.patch(updated_metadata)
    assert transformed_metadata.to_dict() == PATCHED_METADATA


def test_patch_enumerated():
    transformed_metadata = Metadata(ENUMERATED_TRANSFORMED_METADATA)
    updated_metadata = Metadata(ENUMERATED_UPDATED_METADATA)
    transformed_metadata.patch(updated_metadata)
    assert transformed_metadata.to_dict() == PATCHED_ENUMERATED_METADATA


def test_patch_with_deleted_object():
    with pytest.raises(PatchingError) as e:
        transformed_metadata = Metadata(TRANSFORMED_METADATA)
        updated_metadata = Metadata(DELETED_OBJECT_METADATA)
        transformed_metadata.patch(updated_metadata)
    assert 'Can not delete KeyType' in str(e)


def test_patch_with_None():
    with pytest.raises(PatchingError) as e:
        transformed_metadata = Metadata(TRANSFORMED_METADATA)
        transformed_metadata.patch(None)
    assert 'Can not patch with NoneType Metadata' in str(e)


def test_illegaly_patch():
    with pytest.raises(PatchingError) as e:
        transformed_metadata = Metadata(TRANSFORMED_METADATA)
        illegally_updated_metadata = Metadata(ILLEGALLY_UPDATED_METADATA)
        transformed_metadata.patch(illegally_updated_metadata)
    assert (
        'Illegal change to one of these variable fields: '
        '[name, dataType, format, variableRole]'
    ) in str(e)


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
