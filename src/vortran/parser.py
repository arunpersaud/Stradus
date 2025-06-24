"""
parser.py

File to parse the output string from the laser.
"""

from types import NoneType


def parse_output(input: str | NoneType) -> list[str] | NoneType:
    """Parses response from microcontroller to seperate out the
    important data. Returns the data as a variable-length list.
    """

    if input != None:
        lines = input.splitlines()[1:]  # first element is always empty

        # TODO: return error if there is only one element in the list, which means no data

        result = []

        for datum in lines[:-1]:
            info = datum.split("=")[1].strip()
            result.append(info)

    else:
        result = None

    return result


def verify_result(input: str, command: str) -> bool:
    """Verifies if a response has data by looking for the command
    string inside.
    """

    index = input.find(command)

    result = True if (index != -1) else False

    return result
