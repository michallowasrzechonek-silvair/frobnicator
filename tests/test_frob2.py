import pytest
from frobnicator import frobnicate


@pytest.fixture
def partner_name():
    return "silvair"


def test_frobnicate(partner_name):
    partner, documents = frobnicate(partner_name)

    assert partner["partnerId"] == partner_name
