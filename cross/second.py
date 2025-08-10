from cross.utils import DIR_ACROSS, DIR_DOWN, can_place, place_word


def build_grid(
    phrase: str,
    min_bridge_len: int = 3,  # минимальная длина горизонтали, соединяющей вертикали
) -> tuple[dict[tuple[int, int], str], list[tuple[str, str, int, int]]]:
    import re

    tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9]+|—", phrase)
    words = [t.upper() for t in tokens]

    grid: dict[tuple[int, int], str] = {}
    placed: list[tuple[str, str, int, int]] = []

    def is_vertical(word_info):
        return word_info[1] == DIR_DOWN

    # Первое слово всегда вертикально в (0,0)
    place_word(grid, words[0], DIR_DOWN, 0, 0)
    placed.append((words[0], DIR_DOWN, 0, 0))

    for word in words[1:]:
        placed_flag = False

        # Перебираем все уже размещённые слова для поиска пересечения
        for ref_idx, (ref_word, ref_dir, rr, rc) in enumerate(placed):
            # Проверка ограничения: если оба вертикальные и соединяет короткая горизонталь — пропустить
            if is_vertical((ref_word, ref_dir, rr, rc)) and len(word) < min_bridge_len:
                continue

            for j, ch_ref in enumerate(ref_word):
                for i, ch in enumerate(word):
                    if ch != ch_ref:
                        continue

                    if ref_dir == DIR_DOWN:
                        # Новое слово горизонталь
                        row = rr + j
                        col = rc - i
                        # Визуальный вес: хотя бы половина символов должна быть правее rc
                        right_count = sum(1 for k in range(len(word)) if col + k > rc)
                        if right_count < len(word) / 2:
                            continue
                        if can_place(grid, word, DIR_ACROSS, row, col):
                            place_word(grid, word, DIR_ACROSS, row, col)
                            placed.append((word, DIR_ACROSS, row, col))
                            placed_flag = True
                            break
                    else:
                        # Новое слово вертикаль
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

        # Если не пересеклось — ставим вертикаль справа
        if not placed_flag:
            max_c = max(c for (_, c) in grid.keys())
            start_col = max_c + 2
            row_try = 0
            while not can_place(grid, word, DIR_DOWN, row_try, start_col):
                row_try += 1
            place_word(grid, word, DIR_DOWN, row_try, start_col)
            placed.append((word, DIR_DOWN, row_try, start_col))

    # Постобработка — вставляем пробелы справа от вертикалей
    vertical_cols = set(c for (_, dir, _, c) in placed if dir == DIR_DOWN)
    min_r = min(r for r, _ in grid.keys())
    max_r = max(r for r, _ in grid.keys())
    min_c = min(c for _, c in grid.keys())
    max_c = max(c for _, c in grid.keys())

    shift_map = {}
    shift = 0
    for col in range(min_c, max_c + 1):
        shift_map[col] = col + shift
        if col in vertical_cols:
            shift += 1

    new_grid = {}
    for (r, c), ch in grid.items():
        new_grid[(r, shift_map[c])] = ch

    return new_grid, placed
