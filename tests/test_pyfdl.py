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
    # TODO Is this a valid approach to test the dumps?
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


def test_setting_default_framing_id(sample_framing_intent):
    fdl = pyfdl.FDL()

    fi = pyfdl.FramingIntent.from_dict(sample_framing_intent)
    fdl.framing_intents.add(fi)
    fdl.default_framing_intent = fi.id

    assert fdl.default_framing_intent == fi.id

    with pytest.raises(pyfdl.FDLError) as err:
        fdl.default_framing_intent = 'nogood'

    assert "Default framing intent: \"nogood\" not found in" in str(err.value)


def test_place_canvas_in_context(sample_canvas, sample_context):
    fdl = pyfdl.FDL()
    canvas = pyfdl.Canvas.from_dict(sample_canvas)
    context = pyfdl.Context.from_dict(sample_context)
    fdl.contexts.add(context)

    fdl.place_canvas_in_context(context_label=context.label, canvas=canvas)
    assert canvas in fdl.contexts.get(context.label).canvases

    fdl.place_canvas_in_context(context_label="nonexistent", canvas=canvas)
    new_context = fdl.contexts.get("nonexistent")
    assert isinstance(new_context, pyfdl.Context)
    assert new_context.canvases.get(canvas.id) == canvas
