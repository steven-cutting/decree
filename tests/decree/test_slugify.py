import pytest

from decree.utils import slugify


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Hello, World!", "hello-world"),
        ("Ünicode → ASCII", "uenicode-ascii"),
        ("  many---separators___ ", "many-separators"),
        ("déjà vu!", "deja-vu"),
        ("café “au lait”", "cafe-au-lait"),
        ("multi — dash", "multi-dash"),
        ("¿Qué tal?", "que-tal"),
        ("Rocket 🚀 science", "rocket-science"),
    ],
)
def test_slugify_rules(title: str, expected: str) -> None:
    assert slugify(title) == expected
