import json
from pathlib import Path

import pytest

import pyfdl

SAMPLE_FDL_DIR = Path(__file__).parent.joinpath("sample_data")
SAMPLE_FDL_FILE = Path(SAMPLE_FDL_DIR, "Scenario-9__FDL_DeliveredToVFXVendor.fdl")


def test_read_from_file_unvalidated():
    fdl = pyfdl.read_from_file(SAMPLE_FDL_FILE, validate=False)

    assert isinstance(fdl, pyfdl.FDL)


def test_read_from_file_validated():
    fdl = pyfdl.read_from_file(SAMPLE_FDL_FILE, validate=True)

    assert isinstance(fdl, pyfdl.FDL)


def test_read_from_string():
    raw = SAMPLE_FDL_FILE.read_text()
    fdl = pyfdl.read_from_string(raw)
    assert isinstance(fdl, pyfdl.FDL)
    assert fdl.to_dict() == json.loads(raw)


def test_write_to_file(tmp_path):
    my_path = Path(tmp_path, "myfdl.fdl")
    fdl1 = pyfdl.read_from_file(SAMPLE_FDL_FILE)

    pyfdl.write_to_file(fdl1, my_path)
    fdl2 = pyfdl.read_from_file(my_path)

    assert fdl1.to_dict() == fdl2.to_dict()


def test_write_to_string():
    raw = SAMPLE_FDL_FILE.read_text()
    fdl = pyfdl.read_from_string(raw)

    assert json.loads(pyfdl.write_to_string(fdl)) == json.loads(raw)


def test_init_empty_fdl():
    fdl = pyfdl.FDL()
    assert isinstance(fdl, pyfdl.FDL)


def test_setting_getting_header():
    fdl = pyfdl.FDL()
    header = pyfdl.Header()
    header.apply_defaults()
    fdl.header = header

    assert isinstance(fdl.header, pyfdl.Header)
    assert header.uuid == fdl.uuid


def test_setting_default_framing_id(sample_framing_intent_obj):
    fdl = pyfdl.FDL()

    fdl.framing_intents.add(sample_framing_intent_obj)
    fdl.default_framing_intent = sample_framing_intent_obj.id

    assert fdl.default_framing_intent == sample_framing_intent_obj.id

    with pytest.raises(pyfdl.FDLError) as err:
        fdl.default_framing_intent = "nogood"

    assert 'Default framing intent: "nogood" not found in' in str(err.value)


def test_place_canvas_in_context(sample_canvas_obj, sample_context_obj):
    fdl = pyfdl.FDL()
    fdl.contexts.add(sample_context_obj)

    fdl.place_canvas_in_context(context_label=sample_context_obj.label, canvas=sample_canvas_obj)
    assert sample_canvas_obj in fdl.contexts.get(sample_context_obj.label).canvases

    fdl.place_canvas_in_context(context_label="nonexistent", canvas=sample_canvas_obj)
    new_context = fdl.contexts.get("nonexistent")
    assert isinstance(new_context, pyfdl.Context)
    assert new_context.canvases.get(sample_canvas_obj.id) == sample_canvas_obj


def test_validate_missing_requirements(sample_framing_intent_obj, sample_canvas_obj):
    fdl = pyfdl.FDL()
    # This raises FDLError as  header is missing required attributes
    with pytest.raises(pyfdl.FDLError):
        fdl.validate()


def test_validate_schema_rule(sample_framing_intent_obj, sample_canvas_obj):
    fdl = pyfdl.FDL()
    fdl.apply_defaults()

    # This is id is too long and will fail schema validation
    framing_intent = sample_framing_intent_obj
    framing_intent.id = "x" * 33
    fdl.framing_intents.add(framing_intent)
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()


def test_validate_missing_source_framing_intent(sample_framing_intent_obj, sample_canvas_obj):
    fdl = pyfdl.FDL()
    fdl.apply_defaults()

    # Source framing intent of framing decision is not in framing intents and will fail validation
    fdl.place_canvas_in_context(context_label="test", canvas=sample_canvas_obj)
    sample_canvas_obj.place_framing_intent(sample_framing_intent_obj)
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()


def test_validate_missing_source_canvas_id(sample_framing_intent_obj, sample_canvas_obj):
    fdl = pyfdl.FDL()
    fdl.apply_defaults()
    fdl.place_canvas_in_context(context_label="test", canvas=sample_canvas_obj)

    # Change source canvas id to provoke validation error
    sample_canvas_obj.source_canvas_id = "shouldnotbethere"
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()
