import json
from pathlib import Path

import pytest

import pyfdl

SAMPLE_FDL_DIR = Path(__file__).parent.joinpath("sample_data")
SAMPLE_FDL_FILE = Path(
    SAMPLE_FDL_DIR,
    "Scenario-9__FDL_DeliveredToVFXVendor.fdl"
)


def test_load_unvalidated():
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=False)

    assert isinstance(fdl, pyfdl.FDL)
    assert isinstance(fdl.header, pyfdl.Header)
    assert fdl.header.uuid == fdl.uuid
    assert fdl.uuid != ""


def test_load_validated():
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=True)

    assert isinstance(fdl, pyfdl.FDL)

    with SAMPLE_FDL_FILE.open('r') as f:
        raw = json.load(f)

    assert raw == fdl.to_dict()


def test_loads():
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        raw = fdl_file.read()

    fdl = pyfdl.loads(raw)
    assert fdl.to_dict() == json.loads(raw)


def test_dump(tmp_path):
    my_path = Path(tmp_path, 'myfdl.fdl')
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        fdl1 = pyfdl.load(fdl_file)

    with my_path.open('w') as fp:
        pyfdl.dump(fdl1, fp)

    with my_path.open('r') as fp:
        fdl2 = pyfdl.load(fp)

    assert fdl1.to_dict() == fdl2.to_dict()


def test_dumps():
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        raw = fdl_file.read()

    fdl = pyfdl.loads(raw)

    assert json.loads(pyfdl.dumps(fdl)) == json.loads(raw)


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
        fdl.default_framing_intent = 'nogood'

    assert "Default framing intent: \"nogood\" not found in" in str(err.value)


def test_place_canvas_in_context(sample_canvas_obj, sample_context_obj):
    fdl = pyfdl.FDL()
    fdl.contexts.add(sample_context_obj)

    fdl.place_canvas_in_context(context_label=sample_context_obj.label, canvas=sample_canvas_obj)
    assert sample_canvas_obj in fdl.contexts.get(sample_context_obj.label).canvases

    fdl.place_canvas_in_context(context_label="nonexistent", canvas=sample_canvas_obj)
    new_context = fdl.contexts.get("nonexistent")
    assert isinstance(new_context, pyfdl.Context)
    assert new_context.canvases.get(sample_canvas_obj.id) == sample_canvas_obj


def test_validate(sample_framing_intent_obj, sample_canvas_obj):
    fdl = pyfdl.FDL()
    # This raises FDLError as  header is missing required attributes
    with pytest.raises(pyfdl.FDLError):
        fdl.validate()

    fdl.apply_defaults()

    # This is id is too long and will fail schema validation
    framing_intent = sample_framing_intent_obj
    framing_intent.id = "x" * 33
    fdl.framing_intents.add(framing_intent)
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()

    # Source framing intent of framing decision is not in framing intents and will fail validation
    fdl.place_canvas_in_context(context_label="test", canvas=sample_canvas_obj)
    sample_canvas_obj.place_framing_intent(framing_intent)
    fdl.framing_intents.remove(framing_intent.id)
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()

    # Change source canvas id to provoke validation error
    sample_canvas_obj.source_canvas_id = "shouldnotbethere"
    with pytest.raises(pyfdl.FDLValidationError):
        fdl.validate()
