from app.services.counter import calculate_sworn_pages


def test_exact_page():
    text = "x" * 1125
    res = calculate_sworn_pages(text)
    assert res["characters"] == 1125
    assert res["billable_pages"] == 1


def test_overflow_page():
    text = "x" * 1126
    res = calculate_sworn_pages(text)
    assert res["characters"] == 1126
    assert res["billable_pages"] == 2


def test_empty_string():
    res = calculate_sworn_pages("")
    assert res["characters"] == 0
    assert res["billable_pages"] == 0
