import pytest


@pytest.fixture()
def sample_header() -> dict:
    header = {
        "uuid": "0E6D12BB-5D9A-461C-803E-5696E9CC8989",
        "version": {"major": 0, "minor": 1},
        "fdl_creator": "ASC FDL Committee",
        "default_framing_intent": "FDLSMP03"
    }
    yield header


@pytest.fixture()
def sample_header_kwargs() -> dict:
    header = {
        "_uuid": "0E6D12BB-5D9A-461C-803E-5696E9CC8989",
        "version": {"major": 0, "minor": 1},
        "fdl_creator": "ASC FDL Committee",
        "default_framing_intent": "FDLSMP03"
    }
    yield header
