"""
validator.py

InputValidator class to encapsulate user input and validate it for:
1) minimum length
2) basic safety checks (SQL/injection keywords + any punctuation)
"""

import string


class InputValidator:
    def __init__(self, text):
        # Store stripped text as the single encapsulated attribute
        self.text = str(text).strip()

    # -----------------------
    # Internal validation logic
    # -----------------------
    def is_long_enough(self, min_chars=20):
        """Return True if text length is >= min_chars, else False."""
        return len(self.text) >= min_chars

    def is_safe(self):
        """
        Return False if either condition is met:
        1) Contains dangerous SQL/injection keywords (case-insensitive)
        2) Contains ANY punctuation character from string.punctuation
        Otherwise return True.
        """
        raw_upper = self.text.upper()

        # Dangerous keywords / tokens
        dangerous_tokens = ["SELECT", "DELETE", "INSERT", "UPDATE", "DROP", "--", ";"]
        for token in dangerous_tokens:
            if token in raw_upper:
                return False

        # Any punctuation at all
        for ch in self.text:
            if ch in string.punctuation:
                return False

        return True

    # -----------------------
    # Public interface
    # -----------------------
    def validate_all(self):
        """
        Runs checks in order:
        - length first (fail fast)
        - safety second
        Returns (bool, message).
        """
        if not self.is_long_enough():
            return (False, "Input must be at least 20 characters long.")

        if not self.is_safe():
            return (False, "Input contains unsafe keywords or punctuation.")

        return (True, "Input validated successfully.")


# -----------------------
# Demonstration / tests
# -----------------------
if __name__ == "__main__":
    # Test 1: Fails due to a dangerous keyword (DROP)
    test1 = InputValidator("Please DROP the table in the database now")
    print("Test 1:", test1.validate_all())

    # Test 2: Fails due to being too short (< 20 chars)
    test2 = InputValidator("Too short input")
    print("Test 2:", test2.validate_all())

    # Test 3: Passes all checks (>=20 chars, no punctuation, no dangerous tokens)
    test3 = InputValidator("This input is long enough and safe")
    print("Test 3:", test3.validate_all())
