import shutil
import sys
from typing import Any, Iterable

import tqdm


def load_print(
    text: str,
    symbol: str = "*",
    indent: int = 0,
    echo: bool = True,
    end: str = "\r",
) -> None:
    """
    Print a loading message with a symbol.

    Parameters
    ----------
    text : str
        Text to display
    symbol : str, default "*"
        Symbol to display before the text
    indent : int, default 0
        Number of spaces to indent the message
    echo : bool, default True
        Whether to actually print the message
    end : str, default "\r"
        Character to print at the end of the message
    """
    symbol = f"\033[1m[{symbol}]\033[0m"
    if echo:
        print(
            f"\r{' ' * indent}{symbol} {text}".ljust(
                shutil.get_terminal_size().columns
            ),
            end=end,
        )


def done_print(
    text: str,
    symbol: str = "+",
    indent: int = 0,
    echo: bool = True,
    overwrite_n_extra_lines: int = 0,
) -> None:
    """
    Print a completion message with a green symbol.

    Parameters
    ----------
    text : str
        Text to display
    symbol : str, default "+"
        Symbol to display before the text
    indent : int, default 0
        Number of spaces to indent the message
    echo : bool, default True
        Whether to actually print the message
    overwrite_n_extra_lines : int, default 0
        Number of extra lines to overwrite
    """
    symbol = f"\033[1m\033[92m[{symbol}]\033[0m"
    if echo:
        if overwrite_n_extra_lines:
            cursor_up(overwrite_n_extra_lines + 1)
            for _ in range(overwrite_n_extra_lines):
                print(" ".ljust(shutil.get_terminal_size().columns))
            cursor_up(overwrite_n_extra_lines + 1)
        print(
            f"\r{' ' * indent}{symbol} {text}".ljust(
                shutil.get_terminal_size().columns
            )
        )


def warn_print(
    text: str, symbol: str = "!", indent: int = 0, echo: bool = True
) -> None:
    """
    Print a warning message with a red symbol.

    Parameters
    ----------
    text : str
        Text to display
    symbol : str, default "!"
        Symbol to display before the text
    indent : int, default 0
        Number of spaces to indent the message
    echo : bool, default True
        Whether to actually print the message
    """
    symbol = f"\033[1m\033[91m[{symbol}]\033[0m"
    if echo:
        print(
            f"\r{' ' * indent}{symbol} {text}".ljust(
                shutil.get_terminal_size().columns
            )
        )


def load_progress(
    iter_: Iterable[Any],
    text: str,
    symbol: str = "*",
    indent: int = 0,
    echo: bool = True,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Any]:
    """
    Create a progress bar for an iterable.

    Parameters
    ----------
    iter_ : Iterable[Any]
        Iterable to iterate over
    text : str
        Text to display with the progress bar
    symbol : str, default "*"
        Symbol to display before the text
    indent : int, default 0
        Number of spaces to indent the message
    echo : bool, default True
        Whether to actually show the progress bar
    *args : Any
        Additional arguments to pass to tqdm
    **kwargs : Any
        Additional keyword arguments to pass to tqdm

    Returns
    -------
    Iterable[Any]
        Iterable wrapped in tqdm if echo is True, otherwise the original iterable
    """
    if echo:
        return tqdm.tqdm(
            iter_,
            f"{' ' * indent}[{symbol}] {text}",
            *args,
            leave=False,
            position=0,
            file=sys.stdout,
            **kwargs,
        )
    else:
        return iter_


def format_number(n: float) -> str:
    """
    Format a number with spaces as thousand separators.

    Parameters
    ----------
    n : float
        Number to format

    Returns
    -------
    str
        Formatted number string
    """
    return "{:,}".format(n).replace(",", " ")


def cursor_up(n: int) -> None:
    """
    Move the cursor up n lines in the terminal.

    Parameters
    ----------
    n : int
        Number of lines to move up
    """
    print(f"\x1b[{n}A")
