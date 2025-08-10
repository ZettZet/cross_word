from cross.utils import DIR_ACROSS, DIR_DOWN, can_place, place_word


def build_grid(
    phrase: str,
) -> tuple[dict[tuple[int, int], str], list[tuple[str, str, int, int]]]:
    import re

    # Разбиваем на слова, включая тире как отдельный токен
    tokens = re.findall(r"[А-Яа-яЁёA-Za-z0-9]+|—", phrase)
    words = [t.upper() for t in tokens]

    grid: dict[tuple[int, int], str] = {}
    placed: list[tuple[str, str, int, int]] = []

    # Первое слово всегда вертикально
    place_word(grid, words[0], DIR_DOWN, 0, 0)
    placed.append((words[0], DIR_DOWN, 0, 0))

    for word in words[1:]:
        # TODO Добавить попытку поставить второе и далее горизонтальное слово по последнему вертикальному
        prev_word, prev_dir, pr, pc = placed[-1]
        placed_flag = False

        # Ищем пересечение только с предыдущим словом
        for j, ch_pw in enumerate(prev_word):
            for i, ch in enumerate(word):
                if ch != ch_pw:
                    continue
                if prev_dir == DIR_DOWN:
                    row = pr + j
                    col = pc - i
                    if can_place(grid, word, DIR_ACROSS, row, col):
                        place_word(grid, word, DIR_ACROSS, row, col)
                        placed.append((word, DIR_ACROSS, row, col))
                        placed_flag = True
                        break
                else:
                    row = pr - i
                    col = pc + j
                    if can_place(grid, word, DIR_DOWN, row, col):
                        place_word(grid, word, DIR_DOWN, row, col)
                        placed.append((word, DIR_DOWN, row, col))
                        placed_flag = True
                        break
            if placed_flag:
                break

        # Если не пересеклось — ставим вертикально справа
        if not placed_flag:
            max_c = max(c for (_, c) in grid.keys())
            start_col = max_c + 2
            row_try = 0
            while not can_place(grid, word, DIR_DOWN, row_try, start_col):
                row_try += 1
            place_word(grid, word, DIR_DOWN, row_try, start_col)
            placed.append((word, DIR_DOWN, row_try, start_col))

    return grid, placed
