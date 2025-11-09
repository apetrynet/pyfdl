import pytest

from pyfdl.errors import FDLError
from pyfdl.clipid import ClipID, FileSequence


def test_file_sequence_init():
    seq = FileSequence("A002_C307_0523JT.####.exr", "#", 0, 100)
    assert seq.value == "A002_C307_0523JT.####.exr"
    assert seq.idx == "#"
    assert seq.min == 0
    assert seq.max == 100


@pytest.mark.parametrize(
    ("min_", "max_", "expect_fail"),
    [
        (0, 100, False),
        (-1, 100, True),
        (100, 200, False),
        (10, -10, True),
    ],
)
def test_file_sequence_min_max_not_negative(min_, max_, expect_fail):
    if expect_fail:
        with pytest.raises(FDLError):
            FileSequence("A002_C307_0523JT.####.exr", "#", min_, max_)
    else:
        assert FileSequence("A002_C307_0523JT.####.exr", "#", min_, max_)


@pytest.mark.parametrize(
    ("clip_name", "file", "sequence"),
    [
        ("A002_C307_0523JT", None, None),
        ("A002_C307_0523JT", "A002_C307_0523JT.mov", None),
         ("A002_C307_0523JT", None, FileSequence("A002_C307_0523JT.####.exr", "#", 0, 100)),
    ]
)
def test_clip_id_init(clip_name, file, sequence):
    cid = ClipID(clip_name=clip_name, file=file, sequence=sequence)

    assert cid.clip_name == clip_name
    assert cid.file == file
    assert cid.sequence == sequence


def test_clip_id_raise_on_two_identifiers():
    cid1 = ClipID(clip_name="A002_C307_0523JT", file="A002_C307_0523JT.mov")
    with pytest.raises(FDLError) as err:
        cid1.sequence = FileSequence("A002_C307_0523JT.####.exr", "#", 0, 100)

    assert "A file is already provided. " in str(err)

    cid2 = ClipID(clip_name="A002_C307_0523JT", sequence=FileSequence("A002_C307_0523JT.####.exr", "#", 0, 100))
    with pytest.raises(FDLError) as err:
        cid2.file = "A002_C307_0523JT.mov"

    assert "A sequence is already provided. " in str(err)
