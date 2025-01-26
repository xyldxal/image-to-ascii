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
                rgb = tuple(map(int, color_pixels[row_idx][col_idx]))
                colored_char = self._color_modes[color_mode](char, rgb)
                ascii_row.append(colored_char)

            ascii_str.append(''.join(ascii_row))
        
        return '\n'.join(ascii_str) + "\033[0m" 

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
                    rgb = tuple(map(int, color_pixels[row_idx][col_idx]))
                    colored_char = self._color_modes[color_mode](char, rgb)
                    ascii_row.append(colored_char)


            ascii_str.append(''.join(ascii_row))

        return '\n'.join(ascii_str) + "\033[0m"

    
    def _rgb_to_256(self, r: int, g: int, b: int) -> int:
        """
        Convert RGB values to 256-color code.
        Returns color index (0-255).
        """
        # Convert to 0-5 range for each component
        r = int((r * 5) / 255)
        g = int((g * 5) / 255)
        b = int((b * 5) / 255)
        
        # Calculate 256-color code
        return 16 + (36 * r) + (6 * g) + b

    def _get_color_escape(self, r: int, g: int, b: int, background: bool = False) -> str:
        """
        Get ANSI escape sequence for 256-color.
        """
        color_code = self._rgb_to_256(r, g, b)
        return f"\033[{48 if background else 38};5;{color_code}m"

    def _no_color(self, char: str, rgb: Tuple[int, int, int]) -> str:
        """Return character without color."""
        return char

    def _foreground_color(self, char: str, rgb: Tuple[int, int, int]) -> str:
        """Apply 256-color foreground."""
        return f"{self._get_color_escape(*rgb)}{char}"

    def _background_color(self, char: str, rgb: Tuple[int, int, int]) -> str:
        """Apply 256-color background."""
        return f"{self._get_color_escape(*rgb, background=True)}{char}"

    def _both_color(self, char: str, rgb: Tuple[int, int, int]) -> str:
        """Apply both 256-color foreground and background."""
        # Adjust background color to be slightly different for visibility
        bg_rgb = tuple(max(0, min(255, v + 20)) for v in rgb)
        return f"{self._get_color_escape(*rgb)}{self._get_color_escape(*bg_rgb, background=True)}{char}"

    
    def process_gif(
        self,
        image_path: str,
        width: Optional[int] = None,
        remove_bg: bool = False,
        chars: Optional[List[str]] = None,
        pattern_mode: bool = False,
        color_mode: str = 'none',
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Process GIF and yield ASCII frames.
        """
        with Image.open(image_path) as gif:
            # Check if image is animated
            is_animated = getattr(gif, "is_animated", False)
            frames = getattr(gif, "n_frames", 1)
            
            if not is_animated:
                # If it's not a GIF, process as single image
                yield self.image_to_ascii(
                    image_path,
                    width=width,
                    remove_bg=remove_bg,
                    chars=chars,
                    pattern_mode=pattern_mode,
                    color_mode=color_mode
                )
                return
            try:
                for frame in range(frames):
                    gif.seek(frame)
                    # Convert frame to RGB
                    rgb_frame = gif.convert('RGB')
                    
                    # Save frame temporarily
                    temp_path = f"temp_frame_{frame}.png"
                    rgb_frame.save(temp_path)
                    
                    # Process frame
                    ascii_frame = self.image_to_ascii(
                        temp_path,
                        width=width,
                        remove_bg=remove_bg,
                        chars=chars,
                        pattern_mode=pattern_mode,
                        color_mode=color_mode
                    )
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    yield ascii_frame

            except Exception as e:
                print(f"Error processing GIF frame: {e}")
                raise

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
