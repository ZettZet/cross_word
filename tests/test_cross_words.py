import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cross_word.cross_words import (
    build_grid,
    tokenize_with_end_punct,
    build_single_block,
    merge_blocks,
)
from cross_word.utils import (
    can_place_word,
    place_word_in_grid,
    DIRECTION_DOWN,
    DIRECTION_ACROSS,
    render_grid,
)


class TestTokenization:
    """Tests for tokenize_with_end_punct function"""

    @pytest.mark.parametrize(
        "phrase,expected",
        [
            ("Привет, мир!", ["ПРИВЕТ", ",", "МИР!"]),
            ("Ааа… и Б-был; но!", ["ААА", "…", "И", "Б-БЫЛ", ";", "НО!"]),
            (
                "?Привет, — как: дела!.",
                ["?", "ПРИВЕТ", ",", "—", "КАК", ":", "ДЕЛА!", "."],
            ),
            ("Single-word", ["SINGLE-WORD"]),
            ("", []),
        ],
    )
    def test_tokenize_various_cases(self, phrase, expected):
        result = tokenize_with_end_punct(phrase)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_tokenize_with_hyphenated_words(self):
        assert tokenize_with_end_punct("state-of-the-art") == ["STATE-OF-THE-ART"]

    def test_tokenize_with_numbers(self):
        assert tokenize_with_end_punct("Version 2.0!") == ["VERSION", "2.", "0!"]


class TestGridPlacement:
    """Tests for word placement and grid operations"""

    def test_place_vertical_word(self):
        grid = {}
        place_word_in_grid(grid, "TEST", DIRECTION_DOWN, 2, 3)
        assert grid == {(2, 3): "T", (3, 3): "E", (4, 3): "S", (5, 3): "T"}

    def test_place_horizontal_word(self):
        grid = {}
        place_word_in_grid(grid, "CODE", DIRECTION_ACROSS, 5, 10)
        assert grid == {(5, 10): "C", (5, 11): "O", (5, 12): "D", (5, 13): "E"}

    @pytest.mark.parametrize(
        "word,direction,row,col,expected",
        [
            ("TEST", DIRECTION_DOWN, 0, 0, True),
            ("TEST", DIRECTION_ACROSS, 0, 0, True),
            ("", DIRECTION_DOWN, 0, 0, True),  # Empty word
        ],
    )
    def test_can_place_in_empty_grid(self, word, direction, row, col, expected):
        grid = {}
        assert can_place_word(grid, word, direction, row, col) == expected

    def test_can_place_conflicting_words(self):
        grid = {}
        place_word_in_grid(grid, "TEST", DIRECTION_DOWN, 0, 0)
        vertical_coords = {(r, 0) for r in range(4)}

        # Should allow crossing at matching letter
        assert can_place_word(
            grid, "EXAMPLE", DIRECTION_ACROSS, 1, 0, vertical_coords=vertical_coords
        ), "Should allow crossing at matching letter"

        # Should reject conflicting placement
        assert not can_place_word(
            grid, "XXXX", DIRECTION_ACROSS, 0, 0, vertical_coords=vertical_coords
        ), "Should reject conflicting letters"


# [Rest of the test classes remain the same...]


class TestBlockBuilding:
    """Tests for build_single_block function"""

    def test_build_empty_block(self):
        grid, remaining = build_single_block([])
        assert grid == {}
        assert remaining == []

    def test_build_single_word_block(self):
        grid, remaining = build_single_block(["HELLO"])
        assert len(grid) == 5
        assert remaining == []
        assert all(grid.get((i, 0), None) == c for i, c in enumerate("HELLO"))

    def test_build_block_with_crossing_words(self):
        grid, remaining = build_single_block(["TEST", "EXAMPLE"])
        assert remaining == []
        # Verify vertical word
        assert all(grid.get((i, 0), None) == c for i, c in enumerate("TEST"))
        # Verify horizontal word crosses at some point
        assert any(
            grid.get((r, c), None) == "E" and grid.get((r, c + 1), None) == "X"
            for r, c in grid
        )

    def test_build_block_with_punctuation(self):
        grid, remaining = build_single_block(["HELLO", "!", "WORLD"])
        assert remaining == ["!", "WORLD"]
        assert len(grid) == 5  # Only "HELLO" placed


class TestBlockMerging:
    """Tests for merge_blocks function"""

    def test_merge_empty_blocks(self):
        assert merge_blocks([]) == {}

    def test_merge_single_block(self):
        block = {(0, 0): "A", (1, 0): "B"}
        assert merge_blocks([block]) == block

    def test_merge_multiple_blocks(self):
        blocks = [
            {(0, 0): "T", (1, 0): "E", (2, 0): "S", (3, 0): "T"},  # Vertical TEST
            {(0, 0): "C", (0, 1): "O", (0, 2): "D", (0, 3): "E"},  # Horizontal CODE
        ]
        merged = merge_blocks(blocks)

        # Verify all letters are present
        assert set(merged.values()) == {"T", "E", "S", "C", "O", "D"}

        # Verify proper spacing between blocks
        test_col = min(c for (r, c) in merged if merged[(r, c)] == "T")
        code_col = min(c for (r, c) in merged if merged[(r, c)] == "C")
        assert code_col > test_col  # CODE should be to the right of TEST


class TestGridBuilding:
    """Tests for build_grid function"""

    def test_build_empty_grid(self):
        grid, blocks = build_grid("")
        assert grid == {}
        assert blocks == []

    def test_build_simple_grid(self):
        grid, blocks = build_grid("TEST EXAMPLE")
        assert len(blocks) >= 1
        assert "T" in grid.values() and "E" in grid.values()

    def test_build_grid_with_punctuation(self):
        grid, blocks = build_grid("Hello, world!")
        assert "," in grid.values() or "!" in grid.values()


class TestGridRendering:
    """Tests for render_grid function"""

    def test_render_empty_grid(self):
        assert render_grid({}) == ""

    def test_render_single_letter(self):
        assert render_grid({(0, 0): "A"}) == "A"

    def test_render_multiline_grid(self):
        grid = {
            (0, 0): "T",
            (1, 0): "E",
            (2, 0): "S",
            (3, 0): "T",  # Vertical
            (1, -1): "E",
            (1, 0): "E",
            (1, 1): "X",  # Horizontal crossing
        }
        rendered = render_grid(grid)
        lines = rendered.splitlines()
        assert len(lines) == 4
        assert "E X" in lines[1]  # Horizontal word


class TestEdgeCases:
    """Tests for various edge cases"""

    def test_single_character_words(self):
        grid, _ = build_grid("A I")
        assert "A" in grid.values() and "I" in grid.values()

    def test_unicode_characters(self):
        grid, _ = build_grid("Привет мир")
        assert "П" in grid.values() and "М" in grid.values()

    def test_long_words(self):
        grid, _ = build_grid("PNEUMONOULTRAMICROSCOPICSILICOVOLCANOCONIOSIS")
        assert len(grid) > 30


class TestPerformance:
    """Performance-related tests"""

    @pytest.mark.timeout(1)
    def test_large_grid_performance(self):
        # Should handle reasonably large input quickly
        phrase = " ".join(["TEST"] * 100)
        build_grid(phrase)
