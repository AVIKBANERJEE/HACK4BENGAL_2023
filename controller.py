import re
from enum import Enum

import pyautogui


class InvalidCommandError(Exception):
    pass


pyautogui.FAILSAFE = False
window_size: tuple = pyautogui.size()

SCROLL_AMOUNT = 200
CURSOR_MOVE_AMOUNT = 10
TYPING_DELAY = 0.1

keyboard_keys = {
    "control": "ctrl",
    "windows": "win",
    "escape": "esc",
    "delete": "del",
    "slash": "/",
    "backslash": "\\",
    "at": "@",
    "hash": "#",
    "dollar": "$",
    "percent": "%",
    "caret": "^",
    "ampersand": "&",
    "asterisk": "*",
    "open bracket": "(",
    "close bracket": ")",
    "open square bracket": "[",
    "close square bracket": "]",
    "open curly bracket": "{",
    "close curly bracket": "}",
    "lesser than": "<",
    "greater than": ">",
    "comma": ",",
    "dot": ".",
    "semicolon": ";",
    "colon": ":",
    "single quote": "'",
    "double quote": '"',
    "backtick": "`",
    "hyphen": "-",
    "underscore": "_",
    "equals": "=",
    "plus": "+",
    "minus": "-",
    "question mark": "?",
    "exclamation mark": "!",
    "pipe": "|",
    "tilde": "~",
    "period": ".",
    "full stop": ".",
}


corners = {
    "top left": (0, 0),
    "top right": (window_size[0], 0),
    "bottom left": (0, window_size[1]),
    "bottom right": (window_size[0], window_size[1]),
}

edges = {
    "top": (pyautogui.position()[0], 0),
    "bottom": (pyautogui.position()[0], window_size[1]),
    "left": (0, pyautogui.position()[1]),
    "right": (window_size[0], pyautogui.position()[1]),
}

num_pattern = re.compile(r"\d+")


def handle_move_mouse_by_percentage(command: str) -> None:
    position = list(int(i) for i in pyautogui.position())
    search_obj = num_pattern.search(command)
    if search_obj is None:
        raise InvalidCommandError()

    number = int(search_obj.group())

    if "left" in command:
        dx = round((number / 100) * (0 - position[0]))
        position[0] += dx

    elif "right" in command:
        dx = round((number / 100) * (window_size[0] - position[0]))
        position[0] += dx

    elif "up" in command or "top" in command:
        dy = round((number / 100) * (0 - position[1]))
        position[1] += dy

    elif "down" in command or "bottom" in command:
        dy = round((number / 100) * (window_size[1] - position[1]))
        position[1] += dy

    pyautogui.moveTo(position[0], position[1], duration=0.25)


def handle_move_mouse_by(command: str) -> None:
    if "percent" in command or "%" in command:
        return handle_move_mouse_by_percentage(command)

    position = list(int(i) for i in pyautogui.position())
    search_obj = num_pattern.search(command)
    if search_obj is None:
        raise InvalidCommandError()

    number = int(search_obj.group())

    if "left" in command:
        position[0] -= number

    elif "right" in command:
        position[0] += number

    elif "up" in command or "top" in command:
        position[1] -= number

    elif "down" in command or "bottom" in command:
        position[1] += number

    pyautogui.moveTo(position[0], position[1], duration=0.25)


def handle_move_mouse_to(command: str) -> None:
    position = None
    curr_x, curr_y = pyautogui.position()

    position = None

    if "center" in command:
        position = (window_size[0] // 2, window_size[1] // 2)
    elif "top edge" in command:
        position = edges["top"]
    elif "bottom edge" in command:
        position = edges["bottom"]
    elif "left edge" in command:
        position = edges["left"]
    elif "right edge" in command:
        position = edges["right"]
    elif "top left corner" in command:
        position = corners["top left"]
    elif "top right corner" in command:
        position = corners["top right"]
    elif "bottom left corner" in command:
        position = corners["bottom left"]
    elif "bottom right corner" in command:
        position = corners["bottom right"]

    if position is None:
        if "left" in command:
            position = (curr_x - CURSOR_MOVE_AMOUNT, curr_y)
        if "right" in command:
            position = (curr_x + CURSOR_MOVE_AMOUNT, curr_y)
        if "up" in command:
            position = (curr_x, curr_y - CURSOR_MOVE_AMOUNT)
        if "down" in command:
            position = (curr_x, curr_y + CURSOR_MOVE_AMOUNT)

    if position is None:
        position = re.findall(r"\d+", command)
        position = tuple(map(int, position))

    if (
        position[0] > window_size[0]
        or len(position) > 2
        and position[1] > window_size[1]
    ):
        print("Please mention a valid position.")
        return

    position = tuple(map(int, position))
    pyautogui.moveTo(*position, duration=0.25)


def handle_mouse_movement(command: str) -> None:
    if "by" in command:
        handle_move_mouse_by(command)

    if "to" in command:
        handle_move_mouse_to(command)


def handle_mouse_click(command: str) -> None:
    button = "left"
    if "right" in command:
        button = "right"
    elif "middle" in command:
        button = "middle"

    click = 1
    if "double" in command:
        click = 2

    pyautogui.click(button=button, clicks=click)


def handle_scroll(command: str) -> None:
    scroll_amt = SCROLL_AMOUNT

    if "by" in command:
        search_obj = num_pattern.search(command)
        if search_obj is None:
            raise InvalidCommandError()

        scroll_amt = int(search_obj.group(0))

    if "down" in command:
        scroll_amt = -scroll_amt
    pyautogui.scroll(scroll_amt)


def handle_mouse_drag(command: str) -> None:
    ...


def handle_typing(command: str) -> None:
    text = re.sub(r"^(type|write)\s+", "", command)
    pyautogui.typewrite(text, interval=TYPING_DELAY)


def handle_key_press(command: str) -> None:
    if "hotkey" in command:
        keys = []
        probable_keys = command.split(" ")[2:]

        for key in probable_keys:
            keys.append(keyboard_keys.get(key, key))

        pyautogui.hotkey(*keys)
        return

    keys = command.split(" ")[1:]
    for key in keys:
        pyautogui.press(keyboard_keys.get(key, key))


def parse(command: str) -> None:
    sub_commands = re.split(r"and|then", command)
    parent_command = None

    for command in sub_commands:
        if "move" in command and "cursor" in command:
            parent_command = handle_mouse_movement
            handle_mouse_movement(command)

        elif "click" in command:
            parent_command = handle_mouse_click
            handle_mouse_click(command)

        elif command.startswith("drag"):
            parent_command = handle_mouse_drag
            handle_mouse_drag(command)

        elif command.startswith("scroll"):
            parent_command = handle_scroll
            handle_scroll(command)

        elif command.startswith(("type", "write")):
            parent_command = handle_typing
            handle_typing(command)

        elif command.startswith("press"):
            parent_command = handle_key_press
            handle_key_press(command)

        elif parent_command:
            parent_command(command)
