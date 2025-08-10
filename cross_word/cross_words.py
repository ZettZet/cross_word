import re

from cross_word.utils import DIR_ACROSS, DIR_DOWN, can_place, place_word


def build_block(
    tokens: list[str], min_bridge_len: int = 3
) -> dict[tuple[int, int], str]:
    """Строит один блок (вертикаль + горизонтали) в локальных координатах"""
    grid: dict[tuple[int, int], str] = {}
    if not tokens:
        return grid

    vertical = tokens[0]
    place_word(grid, vertical, DIR_DOWN, 0, 0)

    v_len = len(vertical)
    row_ptr = 0  # для контроля порядка горизонталей
    for token in tokens[1:]:
        # FIXME это не проверяет мостик, а запрещает слова меньше 3 символов
        if len(token) < min_bridge_len:
            break
        # ищем место для вставки
        placed = False
        for r in range(row_ptr, v_len):
            if token[0] == vertical[0]:
                continue  # запрещено ставить на первую букву вертикали
            # ограничение выхода влево
            max_left = len(token) // 2
            for i, ch in enumerate(token):
                if ch == grid[(r, 0)]:
                    start_col = -i
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
            # FIXME Если блок закрыт, но токены еще остались, нужно создать следующий блок из оставшихся токенов
            break  # блок закрыт

    return grid


def merge_blocks(
    blocks: list[dict[tuple[int, int], str]], punctuations: list[str]
) -> dict[tuple[int, int], str]:
    """Собирает блоки в общую сетку с учётом пустых колонок и пунктуации"""
    grid: dict[tuple[int, int], str] = {}
    col_offset = 0

    for i, block in enumerate(blocks):
        if not block:
            continue
        # смещаем блок
        b_rows = [r for (r, c) in block]
        b_cols = [c for (r, c) in block]
        min_r, max_r = min(b_rows), max(b_rows)
        min_c, max_c = min(b_cols), max(b_cols)

        for (r, c), ch in block.items():
            grid[(r, c + col_offset)] = ch

        # добавляем пунктуацию после блока, если есть
        if i < len(punctuations) and punctuations[i]:
            punct = punctuations[i]
            grid[(0, max_c + 1 + col_offset)] = punct
            col_offset += 1

        # отступ на одну колонку после блока
        col_offset += max_c - min_c + 2

    return grid


def build_grid(
    phrase: str, min_bridge_len: int = 3
) -> tuple[dict[tuple[int, int], str], list[dict]]:
    # Разбиваем на токены и выделяем блоки
    tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9]+|[^\s]", phrase)
    blocks_tokens: list[list[str]] = []
    punctuations: list[str] = []

    current_block = []
    for tok in tokens:
        if re.match(r"[^\wА-Яа-яЁё]", tok):  # знак препинания
            blocks_tokens.append(current_block)
            current_block = []
            punctuations.append(tok)
        else:
            current_block.append(tok.upper())
    if current_block:
        blocks_tokens.append(current_block)
        punctuations.append("")

    # строим блоки
    blocks = [build_block(bt, min_bridge_len) for bt in blocks_tokens]
    # объединяем блоки
    grid = merge_blocks(blocks, punctuations)
    return grid, blocks
