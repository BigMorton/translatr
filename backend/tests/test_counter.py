from app.services.counter import calculate_sworn_pages


def test_exact_page():
    text = "x" * 1125
    res = calculate_sworn_pages(text)
    assert res["raw_character_count"] == 1125
    assert res["sworn_page_count"] == 1


def test_overflow_page():
    text = "x" * 1126
    res = calculate_sworn_pages(text)
    assert res["raw_character_count"] == 1126
    assert res["sworn_page_count"] == 2


def test_empty_string():
    res = calculate_sworn_pages("")
    assert res["raw_character_count"] == 0
    assert res["sworn_page_count"] == 0
