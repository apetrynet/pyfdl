import pyfdl


def test_header_instance_from_dict(sample_header):
    # Simulate reading header form fdl file
    header = pyfdl.Header.from_dict(sample_header)
    assert isinstance(header, pyfdl.Header)
    assert header.to_dict() == sample_header
    assert str(header) == str(sample_header)


def test_header_instance_from_kwargs(sample_header, sample_header_kwargs):
    # Simulate creating one with kwargs
    header = pyfdl.Header(**sample_header_kwargs)
    assert isinstance(header, pyfdl.Header)
    assert str(header) == str(sample_header)


def test_header_instance_defaults():
    # Test empty header and apply defaults
    header = pyfdl.Header()
    assert isinstance(header, pyfdl.Header)

    # Confirm missing required attributes
    assert header.check_required() == header.required

    # Test applying defaults
    assert header.version is None
    header.apply_defaults()
    assert header.version == pyfdl.FDL_SCHEMA_VERSION
    assert header.check_required() == []
