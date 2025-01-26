from typing import List, Optional, Set
import string
from ..utils.validators import validate_chars

class CharacterProcessor:
    """
    Class for handling ASCII character sets.
    
    Attributes:
        DEFAULT_CHARS (List[str]): Default ASCII character set
        MIN_CHARS (int): Minimum number of unique characters required
        MAX_CHARS (int): Maximum number of unique characters allowed

    """

    DEFAULT_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    MIN_CHARS = 2
    MAX_CHARS = 50

    def __init__(self, custom_chars: Optional[str] = None):
        self.DEFAULT_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
        self.MIN_CHARS = 2
        self.MAX_CHARS = 50
        self._chars: List[str] = []
        self.set_chars(custom_chars)

    def set_chars(self, chars: Optional[str]) -> None:
        """
        Set character set, preserving input sequence.

        Args:
            chars: String of characters to use (will be used in sequence)
        """
        if chars is None:
            self._chars = self.DEFAULT_CHARS
            return

        # Convert string to list of characters, preserving order
        char_list = list(chars)
        
        # Validate the character list
        validate_chars(char_list, self.MIN_CHARS, self.MAX_CHARS)
        
        # Set the characters
        self._chars = char_list

    def get_chars(self) -> List[str]:
        """Get current character set."""
        return self._chars.copy()

    def _process_custom_chars(self, input_string: str) -> List[str]:
        """
        Process input string into a list of unique characters.

        Args:
            input_string: Input string to process

        Returns:
            List of unique characters maintaining original order
        """
        # Check if it's a preset style name
        if input_string.upper() in self._preset_styles:
            return self._preset_styles[input_string.upper()]

        # Process as regular string
        seen: Set[str] = set()
        chars: List[str] = []
        
        for char in input_string:
            if char not in seen:
                seen.add(char)
                chars.append(char)
                
        return chars

    def _initialize_presets(self) -> dict:
        """Initialize preset character styles."""
        return {
            'BINARY': ['1', '0'],
            'MATRIX': ['M', 'A', 'T', 'R', 'I', 'X'],
            'BLOCKS': ['█', '▓', '▒', '░', ' '],
            'SIMPLE': ['#', ' '],
            # Fixed the escape sequence
            'DETAILED': list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "),
            'DOTS': ['●', '•', '°', '·', ' '],
            'CARDS': ['♠', '♣', '♥', '♦'],
            'WEATHER': ['☀', '⛅', '☁', '🌧', '⛈'],
        }

    def get_preset_names(self) -> List[str]:
        """Get list of available preset style names."""
        return list(self._preset_styles.keys())

    def apply_preset(self, preset_name: str) -> None:
        """
        Apply a preset character style.

        Args:
            preset_name: Name of the preset to apply

        Raises:
            ValueError: If preset name doesn't exist
        """
        preset_name = preset_name.upper()
        if preset_name not in self._preset_styles:
            raise ValueError(f"Unknown preset style: {preset_name}. "
                           f"Available presets: {', '.join(self.get_preset_names())}")
        
        self._chars = self._preset_styles[preset_name].copy()
        self._original_input = preset_name

    def create_custom_preset(self, name: str, chars: str) -> None:
        """
        Create a new preset style.

        Args:
            name: Name for the new preset
            chars: Characters for the preset

        Raises:
            ValueError: If name already exists or chars are invalid
        """
        name = name.upper()
        if name in self._preset_styles:
            raise ValueError(f"Preset '{name}' already exists")
        
        processed_chars = self._process_custom_chars(chars)
        validate_chars(processed_chars, self.MIN_CHARS, self.MAX_CHARS)
        self._preset_styles[name] = processed_chars

    def get_char_info(self) -> dict:
        """Get information about current character set."""
        return {
            'current_chars': self._chars,
            'char_count': len(self._chars),
            'original_input': self._original_input,
            'is_preset': self._original_input in self._preset_styles if self._original_input else False,
            'contains_spaces': ' ' in self._chars,
            'contains_special': any(not c.isalnum() for c in self._chars)
        }

    def validate_printability(self) -> bool:
        """
        Check if all characters are printable.

        Returns:
            bool: True if all characters are printable
        """
        return all(c in string.printable for c in self._chars)

    def reverse_chars(self) -> None:
        """Reverse the current character set order."""
        self._chars.reverse()

    def sort_chars(self, reverse: bool = False) -> None:
        """
        Sort the current character set.

        Args:
            reverse: Sort in reverse order if True
        """
        self._chars.sort(reverse=reverse)

    def remove_spaces(self) -> None:
        """Remove spaces from the character set."""
        self._chars = [c for c in self._chars if not c.isspace()]

    def add_chars(self, new_chars: str) -> None:
        """
        Add new characters to the existing set.

        Args:
            new_chars: New characters to add

        Raises:
            ValueError: If resulting set would exceed MAX_CHARS
        """
        processed = self._process_custom_chars(new_chars)
        combined = self._chars + [c for c in processed if c not in self._chars]
        
        if len(combined) > self.MAX_CHARS:
            raise ValueError(f"Adding these characters would exceed the maximum of {self.MAX_CHARS}")
            
        self._chars = combined
