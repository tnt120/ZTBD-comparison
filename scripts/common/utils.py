from datetime import timedelta
import random
import json


def get_colored(text="", color=None, bgcolor=None, style=None, restore=None):
    """
    Returns text with specified color, background color, and style using raw ANSI escape codes.

    Parameters:
    - text (str): The text to be styled
    - color (str): Foreground color (e.g., 'RED', 'GREEN', 'BLUE') (default: None)
    - bgcolor (str): Background color (e.g., 'YELLOW', 'BLACK') (default: None)
    - style (str): Text style (e.g., 'BRIGHT', 'DIM', 'RESET') (default: None)
    """
    color_codes = {
        "BLACK": 30,
        "RED": 31,
        "GREEN": 32,
        "YELLOW": 33,
        "BLUE": 34,
        "MAGENTA": 35,
        "CYAN": 36,
        "WHITE": 37,
    }
    bgcolor_codes = {
        "BLACK": 40,
        "RED": 41,
        "GREEN": 42,
        "YELLOW": 43,
        "BLUE": 44,
        "MAGENTA": 45,
        "CYAN": 46,
        "WHITE": 47,
    }
    style_codes = {"BRIGHT": 1, "DIM": 2, "RESET": 0}

    color_code = f"\033[{color_codes.get(color.upper(), 39)}m" if color else ""
    bgcolor_code = f"\033[{bgcolor_codes.get(bgcolor.upper(), 49)}m" if bgcolor else ""
    style_code = f"\033[{style_codes.get(style.upper(), 0)}m" if style else ""

    RESET = "\033[0m"

    post_code = RESET

    if restore:
        post_code = get_colored(**restore, restore=False)
    elif restore is False:
        post_code = ""

    return f"{color_code}{bgcolor_code}{style_code}{text}{post_code}"


def print_colored(
    text, color=None, bgcolor=None, style=None, restore=None, newline=True
):
    """
    Print text with specified color, background color, and style using raw ANSI escape codes.

    Parameters:
    - text (str): The text to be printed
    - color (str): Foreground color (e.g., 'RED', 'GREEN', 'BLUE') (default: None)
    - bgcolor (str): Background color (e.g., 'YELLOW', 'BLACK') (default: None)
    - style (str): Text style (e.g., 'BRIGHT', 'DIM', 'RESET') (default: None)
    """

    print(
        get_colored(text, color, bgcolor, style, restore),
        end="\n" if newline is True else "",
    )


def random_datetime(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def import_n_records(input_file, records_count):

    try:
        with open(input_file, "r") as file:
            data = json.load(file)

            if len(data) == 0:
                print_colored("Input dataset is empty", "RED")
                return False

            if len(data) < records_count:
                print_colored(
                    f'Requested {get_colored(records_count, "WHITE", restore={"color": "YELLOW"})} records, but input file has only {get_colored(len(data), "WHITE", restore={"color": "YELLOW"})}. Returning all available.',
                    "YELLOW",
                )

            return data[:records_count]
    except:
        print_colored(
            f'Failed loading {get_colored(input_file,"WHITE", restore={"color": "RED"})} file.',
            "RED",
        )
        return False
