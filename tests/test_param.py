import pytest
from pytest_cases import parametrize

@pytest.fixture
def foo(request):
    pass

@parametrize("foo", [pytest.param(dict(a=1))], indirect=True)
@parametrize("foo", [pytest.param(dict(b=2))], indirect=True)
def test_override(foo):
    pass
