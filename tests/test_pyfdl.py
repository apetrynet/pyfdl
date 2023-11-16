import json
import os
import pytest
from pathlib import Path

import pyfdl
from conftest import sample_header

SAMPLE_FDL_DIR = Path("/home/daniel/Code/fdl/Test_Scenarios-20231110T150107Z-001")
SAMPLE_FDL_FILE = Path(
    SAMPLE_FDL_DIR,
    "Test_Scenarios/Creating_FDLs/Scenario-9__Canvas_Template_UsedToDo_VFXPull/Scenario-9_results/Scenario-9__FDL_DeliveredToVFXVendor.fdl"
    # "Test_Scenarios/Receiving_FDLs/Scenario-1__OneFramingDecision/Scenario-1_sources/Scenario-1__1FramingDecision.fdl"
)


def test_header_instance(sample_header, sample_header_kwargs):
    # Simulate reading header form fdl file
    header = pyfdl.Header.from_dict(sample_header)
    assert isinstance(header, pyfdl.Header)
    assert header.to_dict() == sample_header
    assert str(header) == str(sample_header)

    # Simulate creating one with kwargs
    header1 = pyfdl.Header(**sample_header_kwargs)
    assert isinstance(header1, pyfdl.Header)
    assert header1.to_dict() == header.to_dict()

    # Test empty header
    header2 = pyfdl.Header()
    assert isinstance(header2, pyfdl.Header)

    # Test applying defaults
    assert header2.uuid is None
    header2.apply_defaults()
    assert header2.uuid is not None
    assert header2.version == pyfdl.FDL_SCHEMA_VERSION


def test_rounding_strategy_default_values():
    rs = pyfdl.RoundStrategy()
    assert rs.even is None
    assert rs.mode is None

    rs.apply_defaults()
    assert rs.even is not None
    assert rs.mode is not None


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


def test_init_empty_fdl():
    fdl = pyfdl.FDL()

    assert isinstance(fdl, pyfdl.FDL)
