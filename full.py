import re
from itertools import groupby

# Type aliases for better readability
Grid = dict[tuple[int, int], str]
TokenList = list[str]

# Constants for punctuation and directions
END_PUNCTUATION = {".", "?", "!"}
SPLIT_PUNCTUATION = {",", "—", ";", ":"}

DIRECTION_DOWN = "down"
DIRECTION_ACROSS = "across"

WORD_PATTERN = re.compile(r"[\wА-Яа-яЁё]")
TOKENIZE_PATTERN = re.compile(r"[А-Яа-яЁёA-Za-z0-9-]+|[^\s]")


def is_word(token: str) -> bool:
    """Check if a token is a word (contains letters or numbers)."""
    return WORD_PATTERN.match(token)


def is_end_punctuation(token: str) -> bool:
    """Check if token ends with sentence-ending punctuation."""
    return token[-1] in END_PUNCTUATION


def is_any_punctuation(token: str) -> bool:
    """Check if token is any punctuation (end or split)."""
    return is_end_punctuation(token) or token[0] in SPLIT_PUNCTUATION


def tokenize_with_end_punct(phrase: str) -> TokenList:
    """
    Tokenize input phrase into words with attached end punctuation.

    Args:
        phrase: Input string to tokenize

    Returns:
        List of tokens with punctuation properly attached to words
    """
    raw_tokens = TOKENIZE_PATTERN.findall(phrase)
    tokens: TokenList = []
    i = 0

    while i < len(raw_tokens):
        current_token = raw_tokens[i]

        if is_word(current_token):
            # Check if next token is end punctuation to attach
            if i + 1 < len(raw_tokens) and is_end_punctuation(raw_tokens[i + 1]):
                tokens.append((current_token + raw_tokens[i + 1]).upper())
                i += 2
                continue
            tokens.append(current_token.upper())
        else:
            tokens.append(current_token)
        i += 1

    return tokens


def can_place_word(
    grid: Grid,
    word: str,
    direction: str,
    start_row: int,
    start_col: int,
    vertical_coords: set[tuple[int, int]] | None = None,
) -> bool:
    """
    Check if a word can be placed in the grid at given position and direction.

    Args:
        grid: Current grid state
        word: Word to place
        direction: Placement direction (DIRECTION_DOWN or DIRECTION_ACROSS)
        start_row: Starting row position
        start_col: Starting column position
        vertical_coords: Set of coordinates that must remain vertical

    Returns:
        True if word can be placed without conflicts
    """
    row_step, col_step = (1, 0) if direction == DIRECTION_DOWN else (0, 1)

    for i, character in enumerate(word):
        current_row = start_row + row_step * i
        current_col = start_col + col_step * i

        if (current_row, current_col) in grid:
            if grid[(current_row, current_col)] != character:
                return False
            if (
                direction == DIRECTION_ACROSS
                and vertical_coords
                and (current_row, current_col) not in vertical_coords
            ):
                return False

    return True


def place_word_in_grid(
    grid: Grid, word: str, direction: str, start_row: int, start_col: int
) -> None:
    """
    Place a word in the grid at specified position and direction.

    Args:
        grid: Grid to modify
        word: Word to place
        direction: Placement direction
        start_row: Starting row position
        start_col: Starting column position
    """
    row_step, col_step = (1, 0) if direction == DIRECTION_DOWN else (0, 1)

    for i, character in enumerate(word):
        current_row = start_row + row_step * i
        current_col = start_col + col_step * i
        grid[(current_row, current_col)] = character


def get_grid_boundaries(grid: Grid) -> tuple[int, int, int, int]:
    """Get min/max row and column coordinates from grid."""
    if not grid:
        return 0, 0, 0, 0
    rows = {r for (r, c) in grid}
    cols = {c for (r, c) in grid}
    return min(rows), max(rows), min(cols), max(cols)


def render_grid(grid: Grid) -> str:
    """
    Convert grid dictionary to printable string representation.

    Args:
        grid: Grid to render

    Returns:
        String representation of the grid
    """
    if not grid:
        return ""

    min_row, max_row, min_col, max_col = get_grid_boundaries(grid)
    lines = []

    for row in range(min_row, max_row + 1):
        line = []
        for col in range(min_col, max_col + 1):
            line.append(grid.get((row, col), " "))
        lines.append(" ".join(line).rstrip())

    return "\n".join(lines)


def get_first_dict_item[Key, Value](dictionary: dict[Key, Value]) -> tuple[Key, Value]:
    """Get the first key-value pair from a dictionary."""
    first_key = next(iter(dictionary.keys()))
    return first_key, dictionary[first_key]


def find_best_crossing_position(
    grid: Grid,
    word: str,
    vertical_coords: set[tuple[int, int]],
    vertical_length: int,
    current_row_ptr: int,
) -> tuple[bool, int, int]:
    """
    Find optimal position to place a word crossing the vertical word.

    Args:
        grid: Current grid state
        word: Word to place
        vertical_coords: Set of vertical word coordinates
        vertical_length: Length of vertical word
        current_row_ptr: Current row pointer

    Returns:
        Tuple of (found_position, row, column)
    """
    max_left_shift = len(word) // 2

    for row in range(current_row_ptr, vertical_length):
        if row == 0:
            continue

        for col_offset, character in enumerate(word):
            if character == grid[(row, 0)]:
                start_col = -col_offset
                if abs(start_col) > max_left_shift:
                    continue

                if can_place_word(
                    grid, word, DIRECTION_ACROSS, row, start_col, vertical_coords
                ):
                    return True, row, start_col

    return False, 0, 0


def build_single_block(tokens: TokenList) -> tuple[Grid, TokenList]:
    """
    Build a single crossword block from tokens.

    Args:
        tokens: List of tokens to process

    Returns:
        Tuple of (grid_block, remaining_tokens)
    """
    grid: Grid = {}
    if not tokens:
        return grid, []

    vertical_word = tokens[0]
    place_word_in_grid(grid, vertical_word, DIRECTION_DOWN, 0, 0)

    if is_any_punctuation(vertical_word):
        return grid, tokens[1:]

    vertical_length = len(vertical_word)
    vertical_coords = {(r, 0) for r in range(vertical_length)}
    current_row_ptr = 0

    for i in range(1, len(tokens)):
        current_token = tokens[i]

        found_position, row, col = find_best_crossing_position(
            grid, current_token, vertical_coords, vertical_length, current_row_ptr
        )

        if not found_position:
            return grid, tokens[i:]

        place_word_in_grid(grid, current_token, DIRECTION_ACROSS, row, col)
        current_row_ptr = row + 1

    return grid, []


def calculate_column_offset(
    current_block: Grid,
    next_block: Grid,
    current_col_offset: int,
    block_index: int,
    total_blocks: int,
) -> int:
    """
    Calculate column offset for the next block.

    Args:
        current_block: Current block being processed
        next_block: Next block to be placed
        current_col_offset: Current column offset
        block_index: Index of current block
        total_blocks: Total number of blocks

    Returns:
        New column offset
    """
    if not current_block or block_index >= total_blocks - 1:
        return current_col_offset

    current_value = get_first_dict_item(current_block)[1]
    next_value = get_first_dict_item(next_block)[1]

    # Add extra space between word blocks
    if is_word(current_value) and is_word(next_value):
        return current_col_offset + 1

    return current_col_offset


def place_single_character_block(
    grid: Grid, block: Grid, blocks: list[Grid], block_index: int, col_offset: int
) -> None:
    """
    Handle placement of single-character blocks (punctuation).

    Args:
        grid: Main grid to modify
        block: Current single-character block
        blocks: List of all blocks
        block_index: Current block index
        col_offset: Current column offset
    """
    (row, col), character = get_first_dict_item(block)

    # Try to find a good row position near adjacent blocks
    for offset in (-1, 1):
        neighbor_index = block_index + offset
        if 0 <= neighbor_index < len(blocks):
            neighbor_block = blocks[neighbor_index]
            grouped_rows = [
                k
                for k, v in groupby(neighbor_block.keys(), lambda p: p[0])
                if len(list(v)) > 1
            ]
            if grouped_rows:
                target_row = min(grouped_rows)
                grid[(target_row, col + col_offset)] = character
                return

    # Default placement if no good position found
    grid[(row, col + col_offset)] = character


def merge_blocks(blocks: list[Grid]) -> Grid:
    """
    Merge individual blocks into a single grid with proper spacing.

    Args:
        blocks: List of blocks to merge

    Returns:
        Merged grid
    """
    grid: Grid = {}
    col_offset = 0

    for i, block in enumerate(blocks):
        if not block:
            continue

        block_columns = {c for (r, c) in block}
        min_col, max_col = min(block_columns), max(block_columns)

        if i > 0:
            col_offset -= min_col

        # Handle single-character blocks (punctuation) differently
        if len(block) == 1:
            place_single_character_block(grid, block, blocks, i, col_offset)
        else:
            for (row, col), character in block.items():
                grid[(row, col + col_offset)] = character

        # Calculate offset for next block
        if i < len(blocks) - 1:
            col_offset = calculate_column_offset(
                block, blocks[i + 1], col_offset, i, len(blocks)
            )

        col_offset += max_col + 1

    return grid


def build_grid(phrase: str) -> tuple[Grid, list[Grid]]:
    """
    Build crossword grid from input phrase.

    Args:
        phrase: Input phrase to process

    Returns:
        Tuple of (merged_grid, individual_blocks)
    """
    tokens = tokenize_with_end_punct(phrase)
    blocks: list[Grid] = []
    remaining_tokens = tokens

    while remaining_tokens:
        block, remaining_tokens = build_single_block(remaining_tokens)
        blocks.append(block)

    merged_grid = merge_blocks(blocks)
    return merged_grid, blocks
