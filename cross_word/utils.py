import re

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

def is_word(token: str) -> bool:
    """Check if a token is a word (contains letters or numbers)."""
    return WORD_PATTERN.match(token)


def is_end_punctuation(token: str) -> bool:
    """Check if token ends with sentence-ending punctuation."""
    return token[-1] in END_PUNCTUATION


def is_any_punctuation(token: str) -> bool:
    """Check if token is any punctuation (end or split)."""
    return is_end_punctuation(token) or token[0] in SPLIT_PUNCTUATION


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
