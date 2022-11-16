
0. A po co komu framework do testów?

Bo pisanie testów jest nudne, uruchamiają się wolno, trzeba spędzać czas na
przygotowaniu raportów, wykresów itp.

Im więcej zrobi za nas automat, tym lepiej.

1. Wyszukiwanie testów

 - pliki nazwane `test_*.py` (ale można podać plik wprost)
 - funkcje nazwane `test_*`
 - klasy nazwane `Test*` i ich metody `test_*`

Nie ma znaczenia gdzie to wszystko leży.

2. Asercje

Pytest *nie uruchamia kodu wprost*.

Zamiast tego, ładuje znalezione moduły jako
[https://docs.python.org/3/library/ast.html](AST), następnie wykonuje na nich
_magiczne_ transformacje i odpala dopiero zmodyfikowany kod.

Główna transformacja to tzw "assertion rewriting", dzięki której nie trzeba
używać specjalnych funkcji typu
[https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertEqual](unittest.TestCase.assertEqual),
a nieprzechodzące asercje raportują znacznie więcej informacji niż tylko
`AssertionError`

Można też dodawać swoje własne
[https://docs.pytest.org/en/7.1.x/how-to/assert.html#defining-your-own-explanation-for-failed-assertions](szczegóły
błędów)

Lektura do poduszki:
- [https://www.pythoninsight.com/2018/01/assertion-rewriting-in-pytest-part-1](Assertion rewriting in Pytest #1)
- [https://www.pythoninsight.com/2018/02/assertion-rewriting-in-pytest-part-2-simple-workarounds](Assertion rewriting in Pytest #2 - simple workarounds)
- [https://www.pythoninsight.com/2018/02/assertion-rewriting-in-pytest-part-3-the-ast](Assertion rewriting in Pytest #3 - the AST)
- [https://www.pythoninsight.com/2018/02/assertion-rewriting-in-pytest-part-4-the-implementation](Assertion rewriting in Pytest #4 - the implementation)

3. Setup/teardown

```python3
class TestClass:
    def setup_method(self):
        print("SETUP")

    def test_one(self):
        pass

    def test_two(self):
        pass

    def teardown_method(self):
        print("TEARDOWN")
```

Czemu klasycznie jest niedobrze?

 - żeby wykonać trzeba trzymać stan w instancji `self`
 - wszystkie test case'y w obrębie klasy współdzielą setup i teardown, mimo że
   może to być nadmiarowe
 - dziedziczenie klas testowych zaciemnia obraz

4. Fixturki (aka "armatura")

Pytest *nie uruchamia kodu wprost!*

Druga magiczna transformacja AST to ewaluacja argumentów funkcji testowych.

Binding odbywa się *po nazwie* (można też `fixture(name="foo")`)

```python3
import pytest

@pytest.fixture
def setup():
    print("SETUP")
    yield
    print("TEARDOWN")

def test_one(setup):
    pass

def test_two(setup):
    pass
```

Czemu magicznie jest niedobrze?

 - IDE mają problem żeby to zrozumieć
 - nazwy fixturek są globalne


5. Mockowanie

Python jest językiem z plasteliny i pozwala modyfikować kod w runtime.

Nie trzeba refaktoryzować kodu żeby umożliwić
[https://en.wikipedia.org/wiki/Dependency_injection](dependency injection) -
zamiast tego używamy [https://en.wikipedia.org/wiki/Monkey_patch](monkey
patching).

Pytest ma do tego wbudowany mechanizm, fixturkę `monkeypatch`:

```python3
@pytest.fixture
def no_requests(monkeypatch):
    def request(*args, **kwargs):
        raise NotImplementedError("Requests are disabled during the test run")

    monkeypatch.setattr("requests.api.request", request)
```

6. Magic mock

W `unittest` jest przydatna klasa `MagicMock` która automatycznie mockuje prawie wszystko:

```python3
@pytest.fixture
def mock_requests(monkeypatch):
    request = MagicMock()
    monkeypatch.setattr("requests.api.request", request)
    return request

def test_frobnicate(mock_requests):
    mock_requests.return_value = MagicMock(text="foo")
    assert frob.frobnicate() == "foo"
```

7. Data-driven tests

Jeśli mamy test który sprawdza wiele przypadków w ten sam sposób, można je
zwinąć - zwracam uwagę na binding argumentów funkcji testowej *po nazwie*:

```python3
@pytest.mark.parametrize("input, output",
    [
        pytest.param("one", "ONE"),
        pytest.param("tWo", "TwO"),
        pytest.param("THREE", "three"),
    ]
)
def test_swapcase(input, output):
    assert input.swapcase() == output
```

8. Przesłanianie fixtur

Co się stanie gdy zrobimy tak:

```python3
@pytest.fixture
def setup():
    print("SETUP")

@pytest.mark.parametrize("setup",
    [
        pytest.param("override"),
    ]
)
def test_foo(setup):
    pass
```

To czasem jest dobre, a czasem nie. Czy da się zrobić fixturę która będzie
przyjmować różne "opcje" podane przez test?

```python3
@pytest.fixture
def mock_requests(request, monkeypatch):
    request = MagicMock(return_value=MagicMock(text=request.param)
    monkeypatch.setattr("requests.api.request", request)
    return request

@pytest.mark.parametrize("mock_requests",
    [
        pytest.param("bar"),
    ],
    indirect=["mock_requests"]
)
def test_frobnicate(mock_requests):
    assert frob.frobnicate() == "bar"
```


