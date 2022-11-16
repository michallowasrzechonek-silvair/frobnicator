from frobnicator import frobnicate


def test_frobnicate():
    partner, documents = frobnicate("silvair")

    assert partner["partnerId"] == "silvair"
