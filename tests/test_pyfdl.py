import json
from pathlib import Path

import pyfdl

SAMPLE_FDL_DIR = Path(__file__).parent.joinpath("sample_data")
SAMPLE_FDL_FILE = Path(
    SAMPLE_FDL_DIR,
    "Scenario-9__FDL_DeliveredToVFXVendor.fdl"
)


def test_load_unverified():
    with SAMPLE_FDL_FILE.open('r') as fdl_file:
        fdl = pyfdl.load(fdl_file, validate=False)

    assert isinstance(fdl, pyfdl.FDL)
    assert isinstance(fdl.header, pyfdl.Header)
    assert fdl.header.uuid != ""


def test_load_verified():
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
    # TODO Find a safer way to compare the two. Preferably as strings
    assert eval(pyfdl.dumps(fdl)) == eval(raw)


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
