import pytest

from pyfdl.handlers import get_handler
from pyfdl.plugins import get_registry
from pyfdl.errors import UnknownHandlerError


@pytest.mark.parametrize(
    'path, handler_name, expected_name',
    (
        ['/some/filename.fdl', None, 'fdl'],
        [None, 'fdl', 'fdl'],
        [None, 'simple', 'simple'],
        ['/some/filename.ext', None, 'simple']
    )
)
def test_get_handler(simple_handler, path, handler_name, expected_name):
    reg = get_registry(reload=True)
    reg.add_handler(simple_handler())

    handler = get_handler(func_name='read_from_string', path=path, handler_name=handler_name)
    assert handler.name == expected_name

    with pytest.raises(RuntimeError):
        get_handler(func_name='read_from_string')

    with pytest.raises(UnknownHandlerError):
        get_handler(func_name='read_from_string', handler_name='bogus')
