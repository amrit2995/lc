import re

class Validator:
    """
    Utility class to validate command-line arguments that are strings or booleans.
    """

    # Class-level regex pattern
    allowed_string_pattern = re.compile(r'^[\w\-./:@<>]+$')  # Can be customized as needed

    @staticmethod
    def validate_args(args):
        """
        Validates that all string and boolean parameters in args are safe and correctly typed.
        Raises ValueError if a validation check fails.
        """
        for key, value in vars(args).items():
            # Validate string parameters
            if isinstance(value, str):
                if value == "":
                    continue  # Allow empty strings
                if value.lower() in {'true', 'false'}:
                    continue  # Acceptable boolean string
                if not Validator.allowed_string_pattern.match(value):
                    raise ValueError(f"Invalid characters in string parameter: {key}={value}")

            # Validate boolean parameters (actual bools or string equivalents)
            elif isinstance(value, bool):
                continue  # OK
            elif isinstance(value, str) and value.lower() in {'true', 'false'}:
                continue  # Acceptable string form