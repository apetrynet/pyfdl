import json
from pathlib import Path

import pyfdl

SAMPLE_FDL_DIR = Path("/home/daniel/Code/fdl/Test_Scenarios-20231110T150107Z-001")
SAMPLE_FDL_FILE = Path(
    SAMPLE_FDL_DIR,
    "Test_Scenarios/Creating_FDLs/Scenario-9__Canvas_Template_UsedToDo_VFXPull/Scenario-9_results/Scenario-9__FDL_DeliveredToVFXVendor.fdl"
    # "Test_Scenarios/Receiving_FDLs/Scenario-1__OneFramingDecision/Scenario-1_sources/Scenario-1__1FramingDecision.fdl"
)


def test_load_unverified():
    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=False)

    assert isinstance(fdl, pyfdl.FDL)
    assert isinstance(fdl.header, pyfdl.Header)
    assert fdl.header.uuid != ""


def test_load_verified():
    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=True)

    assert isinstance(fdl, pyfdl.FDL)

    with SAMPLE_FDL_FILE.open('rb') as f:
        raw = json.load(f)

    assert raw == fdl.to_dict()


def test_loads():
    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        raw = fdl_file.read()

    fdl = pyfdl.loads(raw)
    assert fdl.to_dict() == json.loads(raw)


def test_dumps():
    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        raw = fdl_file.read()

    fdl = pyfdl.loads(raw)

    assert pyfdl.dumps(fdl) == raw


def test_init_empty_fdl():
    fdl = pyfdl.FDL()

    assert isinstance(fdl, pyfdl.FDL)
