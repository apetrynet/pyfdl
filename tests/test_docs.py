import pathlib
import pytest

from mktestdocs import check_md_file


@pytest.mark.parametrize('fpath', pathlib.Path("docs").glob("**/*.md"), ids=str)
def test_all_docs(fpath):
    check_md_file(fpath=fpath)
