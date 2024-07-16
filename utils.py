# utils.py
import random
import string


def generate_code(length):
    """Generate a random string of 6 uppercase and lowercase letters"""
    letters = string.ascii_letters
    random_code = "".join(random.choice(letters) for _ in range(length))
    return random_code
