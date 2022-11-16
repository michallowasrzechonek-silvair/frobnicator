import logging
import pytest
from unittest import mock
from frobnicator import frobnicate


@pytest.fixture(autouse=True)
def disable_requests(monkeypatch):
    monkeypatch.setattr(
        "requests.api.request",
        mock.MagicMock(
            side_effect=NotImplementedError("Requests are disabled during the test run")
        ),
    )


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    partner = dict(partnerId="silvair")
    monkeypatch.setattr(
        "frobnicator.requests.get",
        mock.MagicMock(return_value=mock.MagicMock(json=lambda: partner)),
    )


@pytest.fixture
def partner_name():
    return "silvair"


def test_frobnicate(partner_name):
    partner, documents = frobnicate(partner_name)

    assert partner["partnerId"] == partner_name
