"""
parser.py

File to parse the output string from the laser.
"""


def parse_output(input: str) -> list[str]:
    lines = input.splitlines()[1:]  # first element is always empty

    # TODO: return error if there is only one element in the list, which means no data

    result = []

    for datum in lines[:-1]:
        info = datum.split("=")[1].strip()
        result.append(info)

    return result
