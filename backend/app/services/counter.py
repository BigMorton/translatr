import math

SWORN_PAGE_SIZE = 1125


def calculate_sworn_pages(text: str) -> dict:
    char_count = len(text)
    if char_count == 0:
        return {"characters": 0, "billable_pages": 0}

    pages = math.ceil(char_count / SWORN_PAGE_SIZE)
    return {"characters": char_count, "billable_pages": pages}
