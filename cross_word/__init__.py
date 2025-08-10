"""Cross Word Generator Package

This package provides functionality to generate crossword puzzles.
"""

from .cross_words import build_grid, build_block
from .utils import render_grid, DIR_ACROSS, DIR_DOWN

__all__ = [
    "build_grid",
    "build_block",
    "render_grid",
    "DIR_ACROSS",
    "DIR_DOWN",
]
