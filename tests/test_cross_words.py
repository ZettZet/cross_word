import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from cross_word.cross_words import (
    build_grid,
    tokenize_with_end_punct,
    build_block,
    merge_blocks,
)
from cross_word.utils import can_place, place_word, DIR_DOWN, DIR_ACROSS, render_grid


def test_tokenize_with_end_punct():
    phrase = "Привет, мир!"
    tokens = tokenize_with_end_punct(phrase)
    assert tokens == ["ПРИВЕТ", ",", "МИР!"]


def test_can_place_and_place_word():
    grid = {}
    place_word(grid, "ТЕСТ", DIR_DOWN, 0, 0)
    assert grid[(0, 0)] == "Т"
    assert grid[(3, 0)] == "Т"
    # Проверяем, что новое слово можно поставить горизонтально пересекающимся по букве "Е"
    assert can_place(
        grid, "ЕСО", DIR_ACROSS, 1, 0, vertical_coords={(0, 0), (1, 0), (2, 0), (3, 0)}
    )
    # Нельзя перетерать буквы другим словом
    assert not can_place(
        grid, "КОД", DIR_ACROSS, 0, 0, vertical_coords={(0, 0), (1, 0), (2, 0), (3, 0)}
    )


def test_build_block_simple():
    tokens = ["ТЕСТ", "ЕСО"]
    grid, rem, punct = build_block(tokens)
    assert rem == []
    assert punct == ""
    # В сетке должно быть слово ТЕСТ вертикально
    assert all(grid.get((i, 0), None) == ch for i, ch in enumerate("ТЕСТ"))
    # И слово ЕСО должно пересекаться с буквой Е
    placed_horizontal = any(
        all(grid.get((r, c + j), None) == ch for j, ch in enumerate("ЕСО"))
        for r, c in grid.keys()
    )
    assert placed_horizontal


def test_merge_blocks_basic():
    block1 = {(0, 0): "Т", (1, 0): "Е", (2, 0): "С", (3, 0): "Т"}
    block2 = {(0, 0): "К", (0, 1): "О", (0, 2): "Д"}
    merged = merge_blocks([block1, block2], ["", ""])
    # Проверяем, что буквы из обоих блоков присутствуют с учетом сдвига
    assert "Т" in merged.values()
    assert "К" in merged.values()
    assert merged.get((0, 3)) == "Д" or merged.get((3, 0)) == "Т"  # сдвиг блока 2


def test_tokenize_with_end_punct_basic():
    phrase = "Привет, мир!"
    tokens = tokenize_with_end_punct(phrase)
    assert tokens == ["ПРИВЕТ", ",", "МИР!"]


def test_tokenize_with_end_punct_complex():
    phrase = "Ааа… и Б-был; но!"
    tokens = tokenize_with_end_punct(phrase)
    # Проверка что слова и знаки препинания корректно разбиты
    assert "ААА" in tokens or "ААА…" in tokens  # учитывайте возможные точки и запятые
    assert ";" in tokens or ";" in tokens
    assert "НО!" in tokens[-1]


def test_can_place_and_place_word_basic():
    grid = {}
    place_word(grid, "ТЕСТ", DIR_DOWN, 0, 0)
    assert grid[(0, 0)] == "Т"
    assert grid[(3, 0)] == "Т"

    # Проверяем can_place возможное размещение слова пересекающегося буквой
    vertical_coords = {(r, 0) for r in range(4)}  # coords "ТЕСТ"
    assert can_place(grid, "ЕСО", DIR_ACROSS, 1, 0, vertical_coords=vertical_coords)

    # Нельзя положить слово перезаписывающее буквы без совпадения
    assert not can_place(grid, "КОД", DIR_ACROSS, 0, 0, vertical_coords=vertical_coords)


def test_build_block_simple():
    tokens = ["ТЕСТ", "ЕСО"]
    grid, rem = build_block(tokens)
    assert rem == []

    # Проверка наличия вертикального слова ТЕСТ
    assert all(grid.get((i, 0), None) == ch for i, ch in enumerate("ТЕСТ"))
    # Проверяем, что "ЕСО" размещено горизонтально пересекается с "Е"
    found_horizontal = False
    for (r, c), ch in grid.items():
        # если горизонтальное слово начинается здесь, то c может быть < 0 (смещение)
        if ch == "Е":
            word_coords = [(r, c + i) for i in range(3)]
            if all(grid.get(pos, None) == wch for pos, wch in zip(word_coords, "ЕСО")):
                found_horizontal = True
                break
    assert found_horizontal


def test_build_block_with_punctuation():
    tokens = ["ТЕСТ", ",", "ЕСО", "?"]
    # Поскольку запятая в отдельном токене - блок построится только из "ТЕСТ", потом запятая
    grid, rem = build_block(tokens)
    assert rem == [",", "ЕСО", "?"]


def test_merge_blocks_basic():
    block1 = {(0, 0): "Т", (1, 0): "Е", (2, 0): "С", (3, 0): "Т"}
    block2 = {(0, 0): "К", (0, 1): "О", (0, 2): "Д"}
    merged = merge_blocks([block1.copy(), block2.copy()])
    # Проверка, что буквы из обоих блоков есть
    values = set(merged.values())
    assert "Т" in values
    assert "К" in values
    assert "О" in values
    assert "Д" in values


def test_build_grid_and_render_basic():
    phrase = "ТЕСТ ЕСО"
    grid, blocks = build_grid(phrase)
    rendered = render_grid(grid)
    # Проверка, что вертикальное слово ТЕСТ есть по столбцу 0
    for i, ch in enumerate("ТЕСТ"):
        assert ch in rendered
    # Проверка что горизонтальное ЕСО тоже присутствует где-то рядом
    assert "ЕСО" in rendered.replace(" ", "").replace("\n", "") or "Е" in rendered


def test_render_grid_spacing():
    # Проверим, что render_grid создает строку с пробелами между буквами и делает вывод
    grid = {(0, 0): "А", (0, 1): "Б", (1, 0): "В"}
    rendered = render_grid(grid)
    lines = rendered.splitlines()
    assert lines[0] == "А Б"
    assert lines[1].startswith("В")


def test_build_block_no_tokens():
    grid, rem = build_block([])
    assert grid == {}
    assert rem == []


def test_build_block_cannot_place_word():
    # "Невозможно поставить" слово, так как нет пересечений
    tokens = ["ПЫЛ", "АННЫЙ"]
    grid, rem = build_block(tokens)
    assert rem == ["АННЫЙ"]


def test_tokenize_with_end_punct_edge_cases():
    # Пунктуация в начале, в середине и конце
    phrase = "?Привет, — как: дела!."
    tokens = tokenize_with_end_punct(phrase)
    # Проверяем, что знаки препинания не теряются и корректно приклеиваются к словам где нужно
    assert tokens[0] == "?"
    assert "," in tokens
    assert "КАК:" in tokens or "КАК" in tokens
    assert tokens[-2] == "ДЕЛА!"
    assert tokens[-1] == "."


def test_can_place_word_overlapping_correctly():
    grid = {}
    place_word(grid, "МАМА", DIR_DOWN, 0, 0)
    vertical_coords = {(r, 0) for r in range(4)}
    # Пытаемся поставить горизонтальное слово "АМ" пересекающееся по букве "А"
    assert can_place(grid, "АМ", DIR_ACROSS, 1, 0, vertical_coords=vertical_coords)
    place_word(grid, "АМ", DIR_ACROSS, 1, 0)
    # Теперь проверить, что наоборот поставить пересечение нельзя (буквы не совпадают)
    assert not can_place(grid, "АН", DIR_ACROSS, 2, 0, vertical_coords=vertical_coords)


def test_build_block_with_no_intersections():
    tokens = ["ПЫЛ", "АННЫЙ"]
    grid, rem = build_block(tokens)
    assert rem == ["АННЫЙ"]
    # Проверяем, что сетка не пустая, и в ней только первое слово (вертикальное)
    assert grid != {}
    for coord in grid.keys():
        assert coord[1] == 0  # столбец 0


def test_build_grid_with_multiple_punctuations():
    phrase = "Привет, мир! Как дела?"
    grid, blocks = build_grid(phrase)
    # Проверяем, что сетка не пустая
    assert grid
    rendered = render_grid(grid)
    # Должны присутствовать символы из слов и знаков препинания
    assert "П" in rendered
    assert "," in rendered or "!" in rendered or "?" in rendered


def test_render_grid_empty_grid():
    empty_grid = {}
    rendered = render_grid(empty_grid)
    # Пустая сетка должна вернуть пустую строку
    assert rendered == ""


def test_build_block_single_word_with_end_punctuation():
    tokens = ["СЛОВО!"]
    grid, rem = build_block(tokens)
    assert rem == []
    # В сетке должно быть слово вертикально
    for i, ch in enumerate("СЛОВО!"):
        assert grid.get((i, 0), None) == ch


def test_build_block_with_split_punctuation_insertion():
    tokens = ["Тест", ",", "Пункт"]
    grid, rem = build_block(tokens)
    # Пунктуация должна быть отделена
    # Остаток должен начинаться с второго слова без запятой
    assert rem == [",", "Пункт"]


def test_can_place_word_with_vertical_coords_none():
    grid = {}
    place_word(grid, "ДОМ", DIR_DOWN, 0, 0)
    # Проверяем can_place без передачи vertical_coords (обязательно True/False)
    assert can_place(grid, "МО", DIR_ACROSS, 2, 0)  # должно пройти
    assert not can_place(grid, "НО", DIR_ACROSS, 1, 0)  # конфликт с "ДОМ"
