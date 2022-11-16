from dataclasses import dataclass
from typing import List
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
    partner = request.getfixturevalue("partner")

    def request_mock(url, *args, **kwargs):
        if url == f"https://api.platform-prod.silvair.com/partners/{partner.name}":
            json = dict(
                partnerId=partner.name,
                latestDocuments=[
                    dict(label=doc.label, url=doc.url) for doc in partner.documents
                ],
            )
            return mock.MagicMock(json=lambda: json)

        document = partner.get_document(url)

        if document:
            return mock.MagicMock(raw=mock.MagicMock(read=lambda: document))

        raise NotImplementedError(url)

    request_mock = mock.MagicMock(side_effect=request_mock)
    monkeypatch.setattr("frobnicator.requests.get", request_mock)
    return request_mock


@dataclass
class Document:
    label: str
    url: str
    content: bytes


@dataclass
class Partner:
    name: str
    documents: List[Document]

    def get_document(self, url):
        return next((doc.content for doc in self.documents if url == doc.url), None)

    def __pytestid__(self):
        documents = ",".join(doc.label for doc in self.documents) or "no documents"
        return f"{self.name} ({documents})"


@pytest.mark.parametrize(
    "partner",
    [
        Partner(
            name="silvair",
            documents=[
                Document(
                    label="License",
                    url="https://af.mil/license.pdf",
                    content=b"Lorem ipsum",
                )
            ],
        ),
        Partner(
            name="mcwong",
            documents=[
                Document(
                    label="License",
                    url="https://af.mil/license.pdf",
                    content=b"Lorem ipsum",
                ),
                Document(
                    label="Terms of Use",
                    url="https://af.mil/terms.pdf",
                    content=b"Dolor sit amet",
                ),
            ],
        ),
        Partner(
            name="zumtobel",
            documents=[],
        ),
    ],
)
def test_frobnicate(partner, mock_requests):
    json, documents = frobnicate(partner.name)

    mock_requests.assert_any_call(
        f"https://api.platform-prod.silvair.com/partners/{partner.name}"
    )

    for doc in partner.documents:
        mock_requests.assert_any_call(doc.url, stream=True)
        assert documents[doc.label] == doc.content

    assert json["partnerId"] == partner.name
