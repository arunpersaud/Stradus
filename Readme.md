# Stradus SDK for Vortran lasers

## Installation

If you don't have python already on your system you can install it using [uv](https://docs.astral.sh/uv/#installation).

## Use

- System will use the first laser found. If your intent is to use more than 1 laser, please edit the section containing:
    for x in range (len(lasers)) where x is the laser you want to control.
- Note you will need access to the commands list to drive vortran lasers. The example command in this file is LE=1 which refers to "Laser Enable ON". To test, send "LE=0" and laser should turn off.
- Additional commands can be used as needed, simply following the function call "send_my_command"
- Note the option for writeOnly. If using as true, the system will issue the command and not check for a reply.
  if false, the system will poll the laser output stream until an acknowledgement is received.

## Development

If you want to contribute, please install and use `pre-commit`.

You can do this by doing

    uv pip install pre-commit

and then running the following command inside the git repo

    pre-commit install

