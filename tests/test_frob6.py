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
def mock_requests(monkeypatch, request):
    partner_name = request.getfixturevalue("partner_name")
    partner_documents = request.getfixturevalue("partner_documents")

    partner = dict(
        partnerId=partner_name,
        latestDocuments=[
            dict(label=doc["label"], url=doc["url"]) for doc in partner_documents
        ],
    )

    def request_mock(url, *args, **kwargs):
        if url == f"https://api.platform-prod.silvair.com/partners/{partner_name}":
            return mock.MagicMock(json=lambda: partner)

        document = next(
            (doc["content"] for doc in partner_documents if url == doc["url"]), None
        )

        if document:
            return mock.MagicMock(raw=mock.MagicMock(read=lambda: document))

        raise NotImplementedError(url)

    request_mock = mock.MagicMock(side_effect=request_mock)
    monkeypatch.setattr("frobnicator.requests.get", request_mock)
    return request_mock


@pytest.mark.parametrize(
    "partner_name, partner_documents",
    [
        (
            "silvair",
            [
                dict(
                    label="License",
                    url="https://af.mil/license.pdf",
                    content=b"Lorem ipsum",
                )
            ],
        ),
        (
            "mcwong",
            [
                dict(
                    label="Terms of Use",
                    url="https://af.mil/terms.pdf",
                    content=b"Dolor sit amet",
                )
            ],
        ),
    ],
)
def test_frobnicate(partner_name, partner_documents, mock_requests):
    partner, documents = frobnicate(partner_name)

    mock_requests.assert_any_call(
        f"https://api.platform-prod.silvair.com/partners/{partner_name}"
    )

    for doc in partner_documents:
        mock_requests.assert_any_call(doc["url"], stream=True)

    assert partner["partnerId"] == partner_name
