import re

from cross_word.utils import DIR_ACROSS, DIR_DOWN, can_place, place_word

END_PUNCT = {".", "?", "!"}  # приклеиваются к слову
SPLIT_PUNCT = {",", "—", ";", ":"}  # в отдельную колонку


def build_block(
    tokens: list[str], min_bridge_len: int = 3
) -> tuple[dict[tuple[int, int], str], list[str], str]:
    """
    Строит блок из токенов.
    Возвращает:
    - grid: словарь {(row, col): char} в локальных координатах
    - remaining_tokens: список токенов, которые остались неиспользованными
    - end_punct: конечный или разделительный знак, который закрыл блок ("" если нет)
    """
    grid: dict[tuple[int, int], str] = {}
    if not tokens:
        return grid, [], ""

    # первый токен всегда вертикаль
    vertical = tokens[0]
    place_word(grid, vertical, DIR_DOWN, 0, 0)
    v_len = len(vertical)

    row_ptr = 0
    i = 1
    while i < len(tokens):
        token = tokens[i]

        # если это пунктуация — закрываем блок
        if re.match(r"[^\wА-Яа-яЁё]", token):
            return grid, tokens[i + 1 :], token

        placed = False
        # пытаемся вставить горизонталь
        for r in range(row_ptr, v_len):
            if token[0] == vertical[0]:
                continue
            max_left = len(token) // 2
            for j, ch in enumerate(token):
                if ch == grid[(r, 0)]:
                    start_col = -j
                    if abs(start_col) > max_left:
                        continue
                    if can_place(grid, token, DIR_ACROSS, r, start_col):
                        place_word(grid, token, DIR_ACROSS, r, start_col)
                        placed = True
                        row_ptr = r + 1
                        break
            if placed:
                break

        if not placed:
            # не смогли вставить — закрываем блок и оставляем оставшиеся токены
            return grid, tokens[i:], ""

        i += 1

    return grid, [], ""


def merge_blocks(
    blocks: list[dict[tuple[int, int], str]], puncts: list[str]
) -> dict[tuple[int, int], str]:
    grid: dict[tuple[int, int], str] = {}
    col_offset = 0

    for i, block in enumerate(blocks):
        if not block:
            continue
        b_rows = [r for (r, c) in block]
        b_cols = [c for (r, c) in block]
        min_c, max_c = min(b_cols), max(b_cols)

        # копируем блок с учётом смещения
        for (r, c), ch in block.items():
            grid[(r, c + col_offset)] = ch

        punct = puncts[i]
        if punct in END_PUNCT:
            # приклеиваем к последней букве вертикали
            v_cols = [c for (r, c) in block if c == min_c]
            last_row = max(r for (r, c) in block if c == min_c)
            grid[(last_row, min_c + col_offset + 1)] = punct
            col_offset += max_c - min_c + 2
        elif punct in SPLIT_PUNCT:
            # отдельная колонка
            grid[(0, max_c + 1 + col_offset)] = punct
            col_offset += max_c - min_c + 3
        else:
            col_offset += max_c - min_c + 2

    return grid


def build_grid(phrase: str) -> tuple[dict[tuple[int, int], str], list[dict]]:
    # токенизация — слова и отдельные символы
    tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9]+|[^\s]", phrase)
    tokens = [t.upper() if re.match(r"[\wА-Яа-яЁё]", t) else t for t in tokens]

    blocks: list[dict[tuple[int, int], str]] = []
    puncts: list[str] = []

    remaining = tokens
    while remaining:
        block, remaining, punct = build_block(remaining)
        blocks.append(block)
        puncts.append(punct)

    grid = merge_blocks(blocks, puncts)
    return grid, blocks
