import pytest
from unittest.mock import MagicMock
from frobnicator import frob


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    def request(*args, **kwargs):
        raise NotImplementedError("Requests are disabled during the test run")

    monkeypatch.setattr(
        "requests.api.request", MagicMock(side_effect=NotImplementedError)
    )


def test_frobnicate(mock_requests):
    mock_requests.return_value = MagicMock(text="foo")
    assert frob.frobnicate() == "foo"


@pytest.mark.parametrize(
    "input, output",
    [
        pytest.param("one", "ONE"),
        pytest.param("tWo", "TwO"),
        pytest.param("THREE", "three"),
    ],
)
def test_swapcase(input, output):
    assert input.swapcase() == output


@pytest.fixture
def setup():
    print("SETUP")


@pytest.mark.parametrize(
    "setup",
    [
        pytest.param("override"),
    ],
    indirect=True,
)
def test_foo(setup):
    pass


@pytest.fixture
def mock_requests(request, monkeypatch):
    request = MagicMock(return_value=MagicMock(text=request.param))
    monkeypatch.setattr("requests.api.request", request)
    return request


@pytest.mark.parametrize(
    "mock_requests",
    [
        pytest.param("bar"),
    ],
    indirect=True,
)
def test_frobnicate(mock_requests):
    assert frob.frobnicate() == "bar"
