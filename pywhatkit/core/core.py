import os
import pathlib
import time
from os import PathLike
from platform import system
from urllib.parse import quote
from webbrowser import open

import requests
import pyperclip
from pyautogui import click, hotkey, locateOnScreen, moveTo, press, size, typewrite
from pyscreeze import Box, ImageNotFoundException, locate, screenshot

from pywhatkit.core.exceptions import InternetException

WIDTH, HEIGHT = size()


def check_number(number: str) -> bool:
    """Checks the Number to see if contains the Country Code"""

    return "+" in number or "_" in number


def close_tab(wait_time: int = 2) -> None:
    """Closes the Currently Opened Browser Tab"""

    time.sleep(wait_time)
    _system = system().lower()
    if _system in ("windows", "linux"):
        hotkey("ctrl", "w")
    elif _system == "darwin":
        hotkey("command", "w")
    else:
        raise Warning(f"{_system} not supported!")
    press("enter")  # Is this needed?


def _locate_on_screen(img_paths: list[PathLike]) -> Box | None:
    """Wraps a call to locateOnScreen to ensure no exception is raised (None is
    always returned if image not found)"""
    # try:
    #     return locateOnScreen(str(img_path))
    # except ImageNotFoundException:
    #     return None

    if len(img_paths) == 0:
        return None

    # Reimplement pyscreeze.locateOnScreen to allow searching for multiple
    # "needle" images in a single screenshot
    screenshot_img = screenshot(region=None)
    for img_path in img_paths:
        try:
            box = locate(str(img_path), screenshot_img)
            if box is not None:
                return box
        except ImageNotFoundException:
            pass
    return None


def find_textbox(
    max_retries: int = 1, sleep_secs_between_retries: float = 1.0,
) -> Box | None:
    """Returns a position inside the textbox, if visible on the screen, or None"""
    data_dir = pathlib.Path(__file__).resolve().parent / "data"
    num_retries = 0
    while True:
        location = _locate_on_screen([data_dir / "sticker_dark.png", data_dir / "sticker_light.png"])
        if location is not None:
            return location
        max_retries += 1
        if max_retries > 0 and num_retries >= max_retries:
            return None
        time.sleep(sleep_secs_between_retries)


def findtextbox(
    max_retries: int = 1, sleep_secs_between_retries: float = 1.0,
) -> None:
    """Try to click on text box"""
    location = find_textbox(max_retries, sleep_secs_between_retries)
    if location is not None:
        left = location.left + location.width + 50
        top = location.top + location.height // 2
        moveTo(left, top)
        click()


def find_link():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    location = locateOnScreen(f"{dir_path}\\data\\link.png")
    print(location)
    try:
        moveTo(location[0] + location[2]/2, location[1] + location[3]/2)
        click()
    except Exception:
        location = locateOnScreen(f"{dir_path}\\data\\link2.png")
        moveTo(location[0] + location[2]/2, location[1] + location[3]/2)
        print(location)
        click()


def find_document():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    location = locateOnScreen(f"{dir_path}\\data\\document.png")
    print(location)
    moveTo(location[0] + location[2]/2, location[1] + location[3]/2)
    click()


def find_photo_or_video():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    location = locateOnScreen(f"{dir_path}\\data\\photo_or_video.png")
    print(location)
    moveTo(location[0] + location[2]/2, location[1] + location[3]/2)
    click()


def check_connection() -> None:
    """Check the Internet connection of the Host Machine"""

    try:
        requests.get("https://google.com", timeout=5)
    except requests.RequestException:
        raise InternetException(
            "Error while connecting to the Internet. Make sure you are connected to the Internet!"
        )


def _web(receiver: str, message: str) -> None:
    """Opens WhatsApp Web based on the Receiver"""
    if check_number(number=receiver):
        open(
            "https://web.whatsapp.com/send?phone="
            + receiver
            + "&text="
            + quote(message)
        )
    else:
        open("https://web.whatsapp.com/accept?code=" + receiver)


def send_message(message: str, receiver: str, wait_time: int) -> None:
    """Parses and Sends the Message"""

    _web(receiver=receiver, message=message)
    time.sleep(7)  # Is this needed? Can it use wait_time?
    click(WIDTH / 2, HEIGHT / 2 + 15)  # Is this needed?
    if wait_time > 7:
        time.sleep(wait_time - 7)
    if not check_number(number=receiver):
        for char in message:
            if char == "\n":
                hotkey("shift", "enter")
            else:
                typewrite(char)
    findtextbox()
    press("enter")


def send_message_list(message: list[str], receiver: str) -> None:
    """Parse and send multiple messages to a number"""
    _web(receiver=receiver, message="")
    findtextbox(max_retries=-1)  # Wait until the textbox is selected
    for msg in message:
        pyperclip.copy(msg)
        paste_clipboard()  # TODO: Do we need to sleep in between?
        press("enter")


def copy_image(path: str) -> None:
    """Copy the Image to Clipboard based on the Platform"""

    _system = system().lower()
    if _system == "linux":
        if pathlib.Path(path).suffix in (".PNG", ".png"):
            os.system(f"copyq copy image/png - < {path}")
        elif pathlib.Path(path).suffix in (".jpg", ".JPG", ".jpeg", ".JPEG"):
            os.system(f"copyq copy image/jpeg - < {path}")
        else:
            raise Exception(
                f"File Format {pathlib.Path(path).suffix} is not Supported!"
            )
    elif _system == "windows":
        from io import BytesIO

        import win32clipboard  # pip install pywin32
        from PIL import Image

        image = Image.open(path)
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    elif _system == "darwin":
        if pathlib.Path(path).suffix in (".jpg", ".jpeg", ".JPG", ".JPEG"):
            os.system(
                f"osascript -e 'set the clipboard to (read (POSIX file \"{path}\") as JPEG picture)'"
            )
        else:
            raise Exception(
                f"File Format {pathlib.Path(path).suffix} is not Supported!"
            )
    else:
        raise Exception(f"Unsupported System: {_system}")


def send_image(path: str, caption: str, receiver: str, wait_time: int) -> None:
    """Sends the Image to a Contact or a Group based on the Receiver"""

    _web(message=caption, receiver=receiver)
    time.sleep(7)
    click(WIDTH / 2, HEIGHT / 2 + 15)
    time.sleep(wait_time - 7)
    copy_image(path=path)
    if not check_number(number=receiver):
        for char in caption:
            if char == "\n":
                hotkey("shift", "enter")
            else:
                typewrite(char)
    else:
        typewrite(" ")
    paste_clipboard()
    time.sleep(1)
    findtextbox()
    press("enter")


def paste_clipboard() -> None:
    """Pastes the clipboard contents into the active textbox"""
    if system().lower() == "darwin":
        hotkey("command", "v", interval=0.25)
    else:
        hotkey("ctrl", "v")
