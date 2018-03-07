from inspect import getsourcelines


def printsource(func):
    """Print out the source code of a function."""
    lines, _ = getsourcelines(func)
    for line in lines:
        print(line, end='')
