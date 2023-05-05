import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
import pyytlounge


@pytest.fixture
def wrapper():
    return pyytlounge.YtLoungeApi("Tester")
