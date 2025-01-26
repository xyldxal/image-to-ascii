"""
ASCII Art Generator
------------------

A tool for converting images to ASCII art with various customization options.
"""

__version__ = "1.0.0"
__author__ = "Marxel Abogado"
__email__ = "xyldxal@gmail.com"

from .processor.image_processor import ImageProcessor
from .processor.char_processor import CharacterProcessor
from .config.settings import SettingsManager

__all__ = ['ImageProcessor', 'CharacterProcessor', 'SettingsManager']