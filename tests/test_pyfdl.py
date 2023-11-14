import os
import sys
import pytest
from pathlib import Path

import pyfdl
from conftest import sample_header

FDL_SCHEMA_FILE = Path("../fdl/FDL_Validation_Tooling/Python_FDL_Checker")
SAMPLE_FDL_DIR = Path("/home/daniel/Code/fdl/Test_Scenarios-20231110T150107Z-001")
SAMPLE_FDL_FILE = Path(
    SAMPLE_FDL_DIR,
    "Test_Scenarios/Creating_FDLs/Scenario-9__Canvas_Template_UsedToDo_VFXPull/Scenario-9_results/Scenario-9__FDL_DeliveredToVFXVendor.fdl"
    # "Test_Scenarios/Receiving_FDLs/Scenario-1__OneFramingDecision/Scenario-1_sources/Scenario-1__1FramingDecision.fdl"
)


def test_header_instance_from_object(sample_header):
    header = pyfdl.Header.from_object(sample_header)
    assert isinstance(header, pyfdl.Header)
    assert header.to_json() == sample_header
    assert str(header) == str(sample_header)


def test_header_instance():
    header = pyfdl.Header()
    assert isinstance(header, pyfdl.Header)


def test_load_unverified():
    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=False)

    assert isinstance(fdl, pyfdl.FDL)
    assert isinstance(fdl.header, pyfdl.Header)
    assert fdl.header.uuid != ""


def test_load_verified_no_schema():
    if 'FDL_SCHEMA' in os.environ:
        del os.environ['FDL_SCHEMA']

    with pytest.raises(pyfdl.errors.FDLError) as err:
        with SAMPLE_FDL_FILE.open('rb') as fdl_file:
            pyfdl.load(fdl_file, validate=True)

    assert err.type == pyfdl.errors.FDLError
    assert str(err.value) == "No FDL_SCHEMA environment variable set. Please provide a path to the current FDL schema."


def test_load_verified_with_schema():
    os.environ['FDL_SCHEMA'] = FDL_SCHEMA_FILE.as_posix()

    with SAMPLE_FDL_FILE.open('rb') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=True)

    assert isinstance(fdl, pyfdl.FDL)


def test_init_empty_header():
    header = pyfdl.Header()

    assert isinstance(header, pyfdl.Header)
    assert header.fdl_creator == 'pyfdl'


def test_init_empty_fdl():
    fdl = pyfdl.FDL()

    assert isinstance(fdl, pyfdl.FDL)
