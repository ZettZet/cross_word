from cross.utils import DIR_ACROSS, DIR_DOWN, can_place, place_word


def build_grid(
    phrase: str, min_bridge_len: int = 3
) -> tuple[dict[tuple[int, int], str], list[tuple[str, str, int, int]]]:
    import re

    # Разбиваем на слова и пунктуацию
    tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9]+|[^\s]", phrase)
    words = [t.upper() for t in tokens]

    grid: dict[tuple[int, int], str] = {}
    placed: list[tuple[str, str, int, int]] = []  # (word, dir, row, col)

    def is_vertical(word_info):
        return word_info[1] == DIR_DOWN

    # Первое слово всегда вертикаль в (0,0)
    place_word(grid, words[0], DIR_DOWN, 0, 0)
    placed.append((words[0], DIR_DOWN, 0, 0))

    # Вспомогательное — проверка визуального веса
    def has_visual_weight(col, word_len, start_col):
        right_count = sum(1 for k in range(word_len) if start_col + k > col)
        return right_count >= word_len / 2

    # Поиск позиции для слова
    for word_idx in range(1, len(words)):
        word = words[word_idx]
        placed_flag = False

        # Ищем пересечение: сначала с последним вертикальным
        vertical_indices = [i for i, w in enumerate(placed) if is_vertical(w)]
        last_vertical_idx = vertical_indices[-1] if vertical_indices else None
        search_indices = []
        if last_vertical_idx is not None:
            search_indices.append(last_vertical_idx)
        # затем — с предыдущими вертикалями в порядке появления
        for vi in vertical_indices[::-1]:
            if vi != last_vertical_idx:
                search_indices.append(vi)

        for ref_idx in search_indices:
            ref_word, ref_dir, rr, rc = placed[ref_idx]

            # если оба вертикальные и горизонталь слишком короткая — пропустить
            if is_vertical((ref_word, ref_dir, rr, rc)) and len(word) < min_bridge_len:
                continue

            for j, ch_ref in enumerate(ref_word):
                for i, ch in enumerate(word):
                    if ch != ch_ref:
                        continue
                    if ref_dir == DIR_DOWN:
                        # горизонталь
                        row = rr + j
                        col = rc - i
                        if not has_visual_weight(rc, len(word), col):
                            continue
                        if can_place(grid, word, DIR_ACROSS, row, col):
                            place_word(grid, word, DIR_ACROSS, row, col)
                            placed.append((word, DIR_ACROSS, row, col))
                            placed_flag = True
                            break
                    else:
                        # вертикаль
                        row = rr - i
                        col = rc + j
                        if can_place(grid, word, DIR_DOWN, row, col):
                            place_word(grid, word, DIR_DOWN, row, col)
                            placed.append((word, DIR_DOWN, row, col))
                            placed_flag = True
                            break
                if placed_flag:
                    break
            if placed_flag:
                break

        # если не удалось — ставим вертикаль в следующий свободный столбец
        if not placed_flag:
            max_c = max(c for (_, c) in grid.keys())
            start_col = max_c + 2
            row_try = 0
            while not can_place(grid, word, DIR_DOWN, row_try, start_col):
                row_try += 1
            place_word(grid, word, DIR_DOWN, row_try, start_col)
            placed.append((word, DIR_DOWN, row_try, start_col))

    # Постобработка — отступы только там, где справа есть другая вертикаль
    vertical_cols = set(c for (_, dir, _, c) in placed if dir == DIR_DOWN)
    min_r = min(r for r, _ in grid.keys())
    max_r = max(r for r, _ in grid.keys())
    min_c = min(c for _, c in grid.keys())
    max_c = max(c for _, c in grid.keys())

    # Определяем, где нужны пробелы
    cols_sorted = sorted(range(min_c, max_c + 1))
    shift_map = {}
    shift = 0
    for col in cols_sorted:
        shift_map[col] = col + shift
        if col in vertical_cols:
            # смотрим, есть ли вертикаль правее
            if any(vc > col for vc in vertical_cols):
                shift += 1

    new_grid = {}
    for (r, c), ch in grid.items():
        new_grid[(r, shift_map[c])] = ch

    return new_grid, placed
