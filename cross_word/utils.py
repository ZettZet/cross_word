DIR_DOWN = "down"
DIR_ACROSS = "across"


def render_grid(grid: dict[tuple[int, int], str]) -> str:
    rows = [r for (r, c) in grid.keys()]
    cols = [c for (r, c) in grid.keys()]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    lines = []
    for r in range(min_r, max_r + 1):
        row_chars = []
        for c in range(min_c, max_c + 1):
            row_chars.append(grid.get((r, c), " "))
        lines.append(" ".join(row_chars).rstrip())
    return "\n".join(lines)


def can_place(
    grid: dict[tuple[int, int], str],
    word: str,
    direction: str,
    row: int,
    col: int,
    vertical_coords=None,
) -> bool:
    """Проверка, можно ли поставить слово, без затирания вертикали"""
    dr, dc = (1, 0) if direction == DIR_DOWN else (0, 1)
    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i
        if (r, c) in grid:
            if grid[(r, c)] != ch:
                return False
            # запрет на перетирание вертикали
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
