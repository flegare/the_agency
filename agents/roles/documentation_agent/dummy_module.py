"""A dummy Python module for testing the Documentation Agent."""

class MyClass:
    """A sample class.

    Attributes:
        value (int): The value of the class.
    """
    def __init__(self, value):
        """Initializes MyClass with a value.

        Args:
            value (int): The initial value.
        """
        self.value = value

    def get_value(self):
        """Returns the current value.

        Returns:
            int: The current value.
        """
        return self.value

def my_function(arg1, arg2):
    """A sample function.

    Args:
        arg1 (str): The first argument.
        arg2 (int): The second argument.

    Returns:
        str: A concatenated string.
    """
    return f"{arg1}-{arg2}"
