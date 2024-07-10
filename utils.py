# utils.py
import random
import string


def generate_code():
    """Generate a random string of 6 uppercase and lowercase letters"""
    letters = string.ascii_letters
    random_code = "".join(random.choice(letters) for _ in range(6))
    return random_code
