from article_overload.db.utils import get_class_parameters


def test_get_class_parameters() -> None:
    class TestClass:
        def __init__(self, a: int, b: str, c: float) -> None:
            self.a = a
            self.b = b
            self.c = c

    test_class = TestClass(1, "test", 42)
    result = get_class_parameters(test_class)
    expected = ["a", "b", "c"]

    assert result == expected
