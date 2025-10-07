from decree.utils import slugify


def test_slugify_rules():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("Ünicode → ASCII") == "unicode-ascii"
    assert slugify("  many---separators___ ") == "many-separators"
