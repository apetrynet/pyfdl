import pathlib
import pytest

from mktestdocs import check_md_file

# files listed here will set memory to True for sequential code blocks
USE_MEM = ["plugins.md"]


@pytest.mark.parametrize('fpath', pathlib.Path("docs").glob("**/*.md"), ids=str)
def test_all_docs(fpath):
    mem = False
    if fpath.name in USE_MEM:
        mem = True
    check_md_file(fpath=fpath, memory=mem)
