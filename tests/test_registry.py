import pip
import pytest

import pyfdl.plugins.registry
from pyfdl.errors import UnknownHandlerError
from pyfdl.handlers.fdl_handler import FDLHandler
from pyfdl.plugins import get_registry


@pytest.fixture
def install_plugins():
    pip.main(
        ['install', 'tests/sample_data/handler-plugin', 'tests/sample_data/faulty-handler-plugin']
    )
    yield

    pip.main(
        ['uninstall', '-y', 'handler-plugin', 'faulty-handler-plugin']
    )


def test_loading_registry():
    pyfdl.plugins.registry._REGISTRY = None
    assert isinstance(get_registry(), pyfdl.plugins.registry.PluginRegistry)
    assert pyfdl.plugins.registry._REGISTRY is not None

    id_ = id(get_registry())
    get_registry(reload=True)
    assert id_ != id(get_registry())


def test_load_builtin():
    _registry = get_registry()
    assert isinstance(_registry.handlers['fdl'], FDLHandler)


def test_load_plugin(capsys, install_plugins):
    _registry = get_registry(reload=True)
    assert _registry.handlers.get('myhandler1') is not None
    assert _registry.handlers.get('myhandler2') is not None

    # faulty-handler-plugin intentionally fails importing
    expected_err1 = \
        """Unable to load plugin: "faulty_handler_plugin1" due to: "No module named 'faulty_handler_plugi'"""

    expected_err2 = \
        """Unable to find a registration function in plugin: "faulty_handler_plugin2"."""

    captured_messages = capsys.readouterr().err
    assert expected_err1 in captured_messages
    assert expected_err2 in captured_messages


def test_add_handler(simple_handler):
    _r = get_registry()
    handler = simple_handler()
    _r.add_handler(handler)

    assert handler.name in _r.handlers


def test_get_handler_by_name(simple_handler):
    _r = get_registry(reload=True)
    _handler = simple_handler()
    _r.add_handler(_handler)

    handler = _r.get_handler_by_name(handler_name='simple', func_name='read_from_string')
    assert handler is _handler

    with pytest.raises(UnknownHandlerError):
        _r.get_handler_by_name(handler_name='simple', func_name='bogus')

    with pytest.raises(UnknownHandlerError):
        _r.get_handler_by_name(handler_name='bogus', func_name='bogus')


def test_get_handler_by_suffix(simple_handler):
    _r = get_registry(reload=True)
    _handler = simple_handler()
    _r.add_handler(_handler)

    handler = _r.get_handler_by_suffix(suffix='.ext', func_name='read_from_string')
    assert handler is _handler

    with pytest.raises(UnknownHandlerError):
        _r.get_handler_by_suffix(suffix='.ext', func_name='bogus')

    with pytest.raises(UnknownHandlerError):
        _r.get_handler_by_suffix(suffix='bogus', func_name='bogus')
