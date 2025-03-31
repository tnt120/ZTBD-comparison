def print_colored(text, color=None, bgcolor=None, style=None):
    """
    Print text with specified color, background color, and style using raw ANSI escape codes.

    Parameters:
    - text (str): The text to be printed
    - color (str): Foreground color (e.g., 'RED', 'GREEN', 'BLUE') (default: None)
    - bgcolor (str): Background color (e.g., 'YELLOW', 'BLACK') (default: None)
    - style (str): Text style (e.g., 'BRIGHT', 'DIM', 'RESET') (default: None)
    """
    color_codes = {
        'BLACK': 30, 'RED': 31, 'GREEN': 32, 'YELLOW': 33, 'BLUE': 34, 'MAGENTA': 35, 'CYAN': 36, 'WHITE': 37
    }
    bgcolor_codes = {
        'BLACK': 40, 'RED': 41, 'GREEN': 42, 'YELLOW': 43, 'BLUE': 44, 'MAGENTA': 45, 'CYAN': 46, 'WHITE': 47
    }
    style_codes = {
        'BRIGHT': 1, 'DIM': 2, 'RESET': 0
    }

    color_code = f'\033[{color_codes.get(color.upper(), 39)}m' if color else ''
    bgcolor_code = f'\033[{bgcolor_codes.get(bgcolor.upper(), 49)}m' if bgcolor else ''
    style_code = f'\033[{style_codes.get(style.upper(), 0)}m' if style else ''

    RESET = '\033[0m'

    print(f"{color_code}{bgcolor_code}{style_code}{text}{RESET}")