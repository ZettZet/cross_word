import re
from itertools import groupby

END_PUNCT = {".", "?", "!"}
SPLIT_PUNCT = {",", "—", ";", ":"}

DIR_DOWN = "down"
DIR_ACROSS = "across"


def can_place(
    grid: dict[tuple[int, int], str],
    word: str,
    direction: str,
    row: int,
    col: int,
    vertical_coords=None,
) -> bool:
    dr, dc = (1, 0) if direction == DIR_DOWN else (0, 1)
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        if (r, c) in grid:
            if grid[(r, c)] != ch:
                return False
            if (
                direction == DIR_ACROSS
                and vertical_coords
                and (r, c) not in vertical_coords
            ):
                return False
    return True


def place_word(
    grid: dict[tuple[int, int], str], word: str, direction: str, row: int, col: int
):
    dr, dc = (1, 0) if direction == DIR_DOWN else (0, 1)
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        grid[(r, c)] = ch


def render_grid(grid: dict[tuple[int, int], str]) -> str:
    if not grid:
        return ""
    rows = [r for (r, c) in grid]
    cols = [c for (r, c) in grid]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    lines = []
    for r in range(min_r, max_r + 1):
        line = []
        for c in range(min_c, max_c + 1):
            line.append(grid.get((r, c), " "))
        lines.append(" ".join(line).rstrip())
    return "\n".join(lines)


def get_first_dict_element[Key, Value](dictionary: dict[Key, Value]):
    first_key = list(dictionary.keys())[0]
    first_value = dictionary[first_key]
    return first_key, first_value


def tokenize_with_end_punct(phrase: str) -> list[str]:
    raw_tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9-]+|[^\s]", phrase)
    tokens = []
    i = 0
    while i < len(raw_tokens):
        tok = raw_tokens[i]
        if is_word(tok):
            if i + 1 < len(raw_tokens) and is_end_punctuation(raw_tokens[i + 1]):
                tokens.append((tok + raw_tokens[i + 1]).upper())
                i += 2
                continue
            else:
                tokens.append(tok.upper())
        else:
            tokens.append(tok)
        i += 1
    return tokens


def is_word(token: str) -> bool:
    return re.match(r"[\wА-Яа-яЁё]", token)


def is_end_punctuation(token: str) -> bool:
    return token[-1] in END_PUNCT


def is_any_punctuation(token) -> bool:
    return is_end_punctuation(token) or token[0] in SPLIT_PUNCT


def build_block(tokens: list[str]) -> tuple[dict[tuple[int, int], str], list[str]]:
    grid: dict[tuple[int, int], str] = {}
    if not tokens:
        return grid, []

    vertical = tokens[0]
    place_word(grid, vertical, DIR_DOWN, 0, 0)
    if is_any_punctuation(vertical):
        return grid, tokens[1:]

    v_len = len(vertical)
    vertical_coords = {(r, 0) for r in range(v_len)}

    row_ptr = 0
    i = 1
    while i < len(tokens):
        tok = tokens[i]

        placed = False
        for r in range(row_ptr, v_len):
            if r == 0:
                continue
            max_left = len(tok) // 2
            for j, ch in enumerate(tok):
                if ch == grid[(r, 0)]:
                    start_col = -j
                    if abs(start_col) > max_left:
                        continue
                    if can_place(grid, tok, DIR_ACROSS, r, start_col, vertical_coords):
                        place_word(grid, tok, DIR_ACROSS, r, start_col)
                        placed = True
                        row_ptr = r + 1
                        break
            if placed:
                break

        if not placed:
            return grid, tokens[i:]
        i += 1

    return grid, []


def merge_blocks(
    blocks: list[dict[tuple[int, int], str]],
) -> dict[tuple[int, int], str]:
    grid: dict[tuple[int, int], str] = {}
    col_offset = 0

    for i, block in enumerate(blocks):
        if not block:
            continue
        b_cols = [c for (r, c) in block]
        min_c, max_c = min(b_cols), max(b_cols)

        if i > 0:
            col_offset -= min_c

        if len(block) == 1:
            for subindex in (-1, 1):
                if 0 <= i + subindex < len(blocks):
                    next_block = blocks[i + subindex]
                    grouped_rows = [
                        k
                        for k, v in groupby(next_block.keys(), lambda p: p[0])
                        if len(list(v)) > 1
                    ]
                    if len(grouped_rows) == 0:
                        continue

                    row = min(grouped_rows)
                    (r, c), ch = get_first_dict_element(block)
                    grid[(row, c + col_offset)] = ch
                    break
            else:
                (r, c), ch = get_first_dict_element(block)
                grid[(r, c + col_offset)] = ch

        else:
            for (r, c), ch in block.items():
                grid[(r, c + col_offset)] = ch

        if 0 <= i + 1 < len(blocks):
            next_block = blocks[i + 1]
            current_value = get_first_dict_element(block)[1]
            next_value = get_first_dict_element(next_block)[1]
            if is_word(current_value) and is_word(next_value):
                col_offset += 1

        col_offset += max_c + 1

    return grid


def build_grid(phrase: str) -> tuple[dict[tuple[int, int], str], list[dict]]:
    tokens = tokenize_with_end_punct(phrase)

    blocks: list[dict[tuple[int, int], str]] = []

    remaining = tokens
    while remaining:
        block, remaining = build_block(remaining)
        blocks.append(block)

    grid = merge_blocks(blocks)
    return grid, blocks
