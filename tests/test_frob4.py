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
    partner = dict(
        partnerId="silvair",
        latestDocuments=[dict(label="License", url="https://af.mil/license.pdf")],
    )
    license = b"Lorem ipsum"

    def request_mock(url, *args, **kwargs):
        if url == "https://api.platform-prod.silvair.com/partners/silvair":
            return mock.MagicMock(json=lambda: partner)

        if url == "https://af.mil/license.pdf":
            return mock.MagicMock(raw=mock.MagicMock(read=lambda: license))

        raise NotImplementedError(url)

    monkeypatch.setattr(
        "frobnicator.requests.get", mock.MagicMock(side_effect=request_mock)
    )


@pytest.fixture
def partner_name():
    return "silvair"


def test_frobnicate(partner_name):
    partner, documents = frobnicate(partner_name)

    assert partner["partnerId"] == partner_name
