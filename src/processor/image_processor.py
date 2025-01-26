from PIL import Image
from rembg import remove
import numpy as np
import io
from typing import Optional, Tuple, Union, List, Generator
from pathlib import Path
from ..utils.validators import validate_image_path
from .char_processor import CharacterProcessor

from colorama import init, Fore, Back, Style
import colorsys

import time
import os


init(convert=True)

class ImageProcessor:
    """
    Main class for processing images and converting them to ASCII art.
    
    Attributes:
        char_processor (CharacterProcessor): Handles ASCII character sets
        _width (int): Default width for ASCII art output
        _image_formats (set): Supported image formats
    """

    def __init__(self):
        self._width = 100
        self._default_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
        self._color_modes = {
            'none': self._no_color,
            'foreground': self._foreground_color,
            'background': self._background_color,
            'both': self._both_color
        }

    def image_to_ascii(
        self,
        image_path: str,
        width: Optional[int] = None,
        remove_bg: bool = False,
        pattern_mode: bool = False,
        color_mode: str = 'none', 
        chars: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        width = width or self._width
        chars = chars or self._default_chars

        # Load image
        image = Image.open(image_path)
        original_color = image.convert('RGB')

        if remove_bg:
            # Get both the image without background and the alpha mask
            no_bg_image, alpha_mask = self._remove_background(image)
            
            # Resize both
            no_bg_image = self._resize_image(no_bg_image, width)
            alpha_mask = self._resize_image(alpha_mask, width)
            
            # for color mode
            original_color = self._resize_image(original_color, width)

            # Convert image to grayscale
            grayscale_image = self._to_grayscale(no_bg_image)
            
            # Convert to ASCII using the alpha mask
            return self._convert_to_ascii_with_mask(
                grayscale_image, 
                alpha_mask, 
                chars, 
                pattern_mode,
                original_color,
                color_mode
            )
        else:
            # Regular processing without background removal
            image = self._resize_image(image, width)
            original_color = self._resize_image(original_color, width)
            grayscale_image = self._to_grayscale(image)
            return self._convert_to_ascii(
                grayscale_image, 
                chars, 
                pattern_mode,
                original_color,
                color_mode
            )

    def _remove_background(self, image: Image.Image) -> tuple[Image.Image, Image.Image]:
        """
        Remove background and return both the processed image and alpha mask.
        """
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Remove background
            output = remove(img_byte_arr)
            no_bg_image = Image.open(io.BytesIO(output))
            
            # Extract alpha channel as mask
            # If image is RGBA, use alpha channel; if RGB, create all-white mask
            if no_bg_image.mode == 'RGBA':
                alpha_mask = no_bg_image.split()[3]  # Get alpha channel
            else:
                alpha_mask = Image.new('L', no_bg_image.size, 255)
            
            return no_bg_image, alpha_mask
        except Exception as e:
            print(f"Warning: Background removal failed: {e}")
            return image, Image.new('L', image.size, 255)

    def _resize_image(self, image: Image.Image, width: int) -> Image.Image:
        """Resize image maintaining aspect ratio."""
        aspect_ratio = image.height / image.width
        height = int(aspect_ratio * width * 0.5)  # 0.5 to account for terminal character spacing
        return image.resize((width, height))

    def _to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale."""
        if image.mode == 'RGBA':
            # Convert RGBA to RGB before grayscale conversion
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            return background.convert('L')
        return image.convert('L')

    def _convert_to_ascii(
        self,
        image: Image.Image,
        chars: List[str],
        pattern_mode: bool,
        color_image: Image.Image,
        color_mode: str = 'none'
    ) -> str:
        """Convert grayscale image to ASCII art without background removal."""
        pixels = np.array(image)
        color_pixels = np.array(color_image)
        ascii_str = []
        
        for row_idx, row in enumerate(pixels):
            ascii_row = []
            for col_idx, pixel in enumerate(row):
                # Get character
                if pattern_mode:
                    char = chars[col_idx % len(chars)]
                else:
                    intensity_levels = 255 / (len(chars) - 1)
                    char_index = int(pixel / intensity_levels)
                    char = chars[char_index]

                # Get color
                rgb = color_pixels[row_idx][col_idx]
                colored_char = self._color_modes[color_mode](char, rgb)
                ascii_row.append(colored_char)

            ascii_str.append(''.join(ascii_row))
        
        return '\n'.join(ascii_str) + Style.RESET_ALL

    def _convert_to_ascii_with_mask(
        self,
        image: Image.Image,
        mask: Image.Image,
        chars: List[str],
        pattern_mode: bool,
        color_image: Image.Image,
        color_mode: str = 'none'
    ) -> str:
        """Convert grayscale image to ASCII art using alpha mask for background."""
        pixels = np.array(image)
        mask_pixels = np.array(mask)
        color_pixels = np.array(color_image)
        ascii_str = []

        for row_idx, row in enumerate(pixels):
            ascii_row = []
            for col_idx, pixel in enumerate(row):
                if mask_pixels[row_idx][col_idx] < 128:  # Background
                    ascii_row.append(' ')
                else:
                    # Get character based on mode
                    if pattern_mode:
                        char = chars[col_idx % len(chars)]
                    else:
                        intensity_levels = 255 / (len(chars) - 1)
                        char_index = int(pixel / intensity_levels)
                        char = chars[char_index]

                    # Apply color
                    rgb = color_pixels[row_idx][col_idx]
                    colored_char = self._color_modes[color_mode](char, rgb)
                    ascii_row.append(colored_char)

            ascii_str.append(''.join(ascii_row))

        return '\n'.join(ascii_str) + Style.RESET_ALL

    
    def _rgb_to_ansi(self, r: int, g: int, b: int) -> str:
        """Convert RGB to closest ANSI color code."""
        # Convert RGB to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Simple color matching
        if s < 0.2:
            if v < 0.5:
                return Fore.WHITE
            return Fore.BLACK
        
        h *= 360
        if h < 30:
            return Fore.RED
        elif h < 90:
            return Fore.YELLOW
        elif h < 150:
            return Fore.GREEN
        elif h < 210:
            return Fore.CYAN
        elif h < 270:
            return Fore.BLUE
        elif h < 330:
            return Fore.MAGENTA
        else:
            return Fore.RED

    def _no_color(self, char: str, rgb: tuple) -> str:
        """Return character without color."""
        return char

    def _foreground_color(self, char: str, rgb: tuple) -> str:
        """Apply foreground color to character."""
        return f"{self._rgb_to_ansi(*rgb)}{char}"

    def _background_color(self, char: str, rgb: tuple) -> str:
        """Apply background color to character."""
        return f"{self._rgb_to_ansi(*rgb).replace('Fore', 'Back')}{char}"

    def _both_color(self, char: str, rgb: tuple) -> str:
        """Apply both foreground and background color."""
        fg = self._rgb_to_ansi(*rgb)
        bg = fg.replace('Fore', 'Back')
        return f"{fg}{bg}{char}"



    def set_custom_chars(self, chars: str) -> None:
        """
        Update the ASCII character set.

        Args:
            chars: New character set to use
        """
        self.char_processor.set_chars(chars)

    def get_image_info(self, image_path: Union[str, Path]) -> dict:
        """
        Get information about an image.

        Args:
            image_path: Path to the image

        Returns:
            dict: Image information including size, format, and mode
        """
        image = self._load_image(image_path)
        return {
            'size': image.size,
            'format': image.format,
            'mode': image.mode,
            'aspect_ratio': image.size[0] / image.size[1]
        }

    def preview(
        self,
        image_path: Union[str, Path],
        max_size: Tuple[int, int] = (800, 600)
    ) -> None:
        """
        Display a preview of the image (useful for debugging).

        Args:
            image_path: Path to the image
            max_size: Maximum display size
        """
        image = self._load_image(image_path)
        image.thumbnail(max_size)
        image.show()

    @property
    def supported_formats(self) -> set:
        """Get supported image formats."""
        return self._image_formats.copy()