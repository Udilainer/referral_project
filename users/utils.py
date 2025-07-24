import random
import string
from django.core.cache import cache


def generate_auth_code():
    """
    Generate a random 4-digit string code for phone authentication.

    Returns:
        str: A 4-digit string (e.g., "1234", "0891")
    """
    return ''.join(random.choices(string.digits, k=4))


def generate_invite_code():
    """
    Generate a random 6-character alphanumeric string for invite codes.
    Uses uppercase letters and digits only.

    Returns:
        str: A 6-character string (e.g., "A1B2C3", "XYZ789")
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=6))


def cache_auth_code(phone_number, code):
    """
    Store the authentication code in Redis cache with a 5-minute expiration.

    Args:
        phone_number (str): The user's phone number
        code (str): The 4-digit authentication code

    Returns:
        bool: True if successfully cached
    """
    cache_key = f"auth_code:{phone_number}"
    return cache.set(cache_key, code, timeout=300)


def verify_auth_code(phone_number, code):
    """
    Check if the provided code matches the cached code for the phone number.

    Args:
        phone_number (str): The user's phone number
        code (str): The code to verify

    Returns:
        bool: True if the code matches, False otherwise
    """
    cache_key = f"auth_code:{phone_number}"
    cached_code = cache.get(cache_key)

    if cached_code is None:
        return False

    is_valid = str(cached_code) == str(code)

    if is_valid:
        cache.delete(cache_key)

    return is_valid
