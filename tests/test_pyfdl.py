import json
from pathlib import Path

import pydantic
import pytest

import fdl

SAMPLE_FDL_DIR = Path(__file__).parent.joinpath("sample_data")
SAMPLE_FDL_FILE = Path(SAMPLE_FDL_DIR, "Scenario-9__FDL_DeliveredToVFXVendor.fdl")


def test_read_from_file_unvalidated():
    result = fdl.read_from_file(SAMPLE_FDL_FILE, validate=False)

    assert isinstance(result, fdl.FDL)


def test_read_from_file_validated():
    result = fdl.read_from_file(SAMPLE_FDL_FILE, validate=True)

    assert isinstance(result, fdl.FDL)


def test_read_from_string():
    raw = SAMPLE_FDL_FILE.read_text()
    result = fdl.read_from_string(raw)
    assert isinstance(result, fdl.FDL)
    assert result.model_dump()


def test_write_to_file(tmp_path):
    my_path = Path(tmp_path, "myfdl.fdl")
    fdl1 = fdl.read_from_file(SAMPLE_FDL_FILE)

    fdl.write_to_file(fdl1, my_path)
    fdl2 = fdl.read_from_file(my_path)

    assert fdl1.model_dump() == fdl2.model_dump()


def test_write_to_string():
    raw = SAMPLE_FDL_FILE.read_text()
    result = fdl.read_from_string(raw)

    assert fdl.FDL.model_validate_json(fdl.write_to_string(result))


def test_init_empty_fdl():
    result = fdl.FDL()
    assert isinstance(result, fdl.FDL)


def test_setting_default_framing_id(sample_framing_intent_obj):
    my_fdl = fdl.FDL()

    my_fdl.framing_intents.append(sample_framing_intent_obj)
    my_fdl.default_framing_intent = sample_framing_intent_obj.id

    assert my_fdl.default_framing_intent == sample_framing_intent_obj.id

    my_fdl.default_framing_intent = "nogood"
    with pytest.raises(ValueError) as err:
        my_fdl._check_default_framing_intent(my_fdl.default_framing_intent)

    assert 'Default framing intent: "nogood" ' in str(err.value)


def test_place_canvas_in_context(sample_canvas_obj, sample_context_obj):
    my_fdl = fdl.FDL()
    my_fdl.contexts.append(sample_context_obj)

    my_fdl.place_canvas_in_context(
        context_label=sample_context_obj.label, canvas=sample_canvas_obj
    )
    assert sample_canvas_obj in my_fdl.contexts.get_by_id(sample_context_obj.label).canvases

    my_fdl.place_canvas_in_context(
        context_label="nonexistent", canvas=sample_canvas_obj
    )
    new_context = my_fdl.contexts.get_by_id("nonexistent")
    assert isinstance(new_context, fdl.Context)
    assert new_context.canvases.get_by_id(sample_canvas_obj.id) == sample_canvas_obj


def test_validate_missing_requirements():
    my_fdl = fdl.FDL()
    # This raises FDLError as header is missing required attributes
    my_fdl.uuid = None
    with pytest.raises(fdl.FDLValidationError):
        my_fdl.validate_fdl()


def test_validate_schema_rule(sample_framing_intent_obj):
    my_fdl = fdl.FDL()

    # This is id is too long and will fail schema validation
    framing_intent = sample_framing_intent_obj
    framing_intent.id = "x" * 33
    my_fdl.framing_intents.append(framing_intent)
    with pytest.raises(fdl.FDLValidationError):
        my_fdl.validate_fdl()


def test_validate_missing_source_framing_intent(sample_framing_intent_obj, sample_canvas_obj):
    my_fdl = fdl.FDL()

    # Source framing intent of framing decision is not in framing intents and will fail validation
    my_fdl.place_canvas_in_context(context_label="test", canvas=sample_canvas_obj)
    sample_canvas_obj.place_framing_intent(sample_framing_intent_obj)
    with pytest.raises(fdl.FDLValidationError):
        my_fdl.validate_fdl()


def test_validate_missing_source_canvas_id(sample_canvas_obj):
    my_fdl = fdl.FDL()
    my_fdl.place_canvas_in_context(context_label="test", canvas=sample_canvas_obj)

    # Change source canvas id to provoke validation error
    sample_canvas_obj.source_canvas_id = "shouldnotbethere"
    with pytest.raises(fdl.FDLValidationError):
        my_fdl.validate_fdl()
