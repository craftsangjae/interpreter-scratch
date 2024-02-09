import re


def check_if_text_is_float(element):
    return bool(re.match(r"^-?\d+(?:\.\d+)$", element))
