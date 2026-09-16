import math

SWORN_PAGE_SIZE = 1125


def calculate_sworn_pages(text: str) -> dict:
    char_count = len(text)
    if char_count == 0:
        return {"raw_character_count": 0, "sworn_page_count": 0}

    pages = math.ceil(char_count / SWORN_PAGE_SIZE)
    return {"raw_character_count": char_count, "sworn_page_count": pages}
