from typing import List, Union, Optional
from pathlib import Path
import os
import string
import imghdr
from PIL import Image

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_image_path(
    path: Union[str, Path],
    min_size: tuple = (10, 10),
    max_size: tuple = (10000, 10000),
    allowed_formats: Optional[set] = None
) -> None:
    """
    Validate image path and basic image properties.

    Args:
        path: Path to the image file
        min_size: Minimum allowed image dimensions (width, height)
        max_size: Maximum allowed image dimensions (width, height)
        allowed_formats: Set of allowed image formats (e.g., {'jpeg', 'png'})

    Raises:
        ValidationError: If any validation check fails
        FileNotFoundError: If the image file doesn't exist
    """
    # Convert string path to Path object
    path = Path(path) if isinstance(path, str) else path

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    # Check if it's a file
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    # Check file extension
    if path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}:
        raise ValidationError(f"Unsupported file extension: {path.suffix}")

    # Verify it's actually an image file
    if not imghdr.what(path):
        raise ValidationError(f"File is not a valid image: {path}")

    try:
        with Image.open(path) as img:
            # Check image format
            if allowed_formats and img.format.lower() not in allowed_formats:
                raise ValidationError(
                    f"Image format {img.format} not in allowed formats: {allowed_formats}"
                )

            # Check image size
            if (img.width < min_size[0] or img.height < min_size[1]):
                raise ValidationError(
                    f"Image is too small. Minimum size is {min_size}"
                )
            
            if (img.width > max_size[0] or img.height > max_size[1]):
                raise ValidationError(
                    f"Image is too large. Maximum size is {max_size}"
                )

            # Check if image can be read
            img.verify()

    except (IOError, SyntaxError) as e:
        raise ValidationError(f"Invalid or corrupted image file: {e}")

def validate_chars(
    chars: List[str],
    min_chars: int = 2,
    max_chars: int = 50,
    allow_spaces: bool = True,
    allow_special: bool = True,
    printable_only: bool = False
) -> None:
    """
    Validate character set for ASCII conversion.

    Args:
        chars: List of characters to validate
        min_chars: Minimum number of unique characters required
        max_chars: Maximum number of unique characters allowed
        allow_spaces: Whether to allow whitespace characters
        allow_special: Whether to allow special characters
        printable_only: Whether to restrict to printable characters only

    Raises:
        ValidationError: If character set validation fails
    """
    # Check character count
    if len(chars) < min_chars:
        raise ValidationError(
            f"At least {min_chars} different characters required. Got {len(chars)}"
        )
    
    if len(chars) > max_chars:
        raise ValidationError(
            f"Maximum {max_chars} characters allowed. Got {len(chars)}"
        )

    # Check for empty characters
    if '' in chars:
        raise ValidationError("Empty character found in character set")

    # Check for spaces if not allowed
    if not allow_spaces and any(c.isspace() for c in chars):
        raise ValidationError("Spaces are not allowed in character set")

    # Check for special characters if not allowed
    if not allow_special and any(not c.isalnum() for c in chars):
        raise ValidationError("Special characters are not allowed in character set")

    # Check for printable characters if required
    if printable_only and any(c not in string.printable for c in chars):
        raise ValidationError("Non-printable characters found in character set")

def validate_output_path(
    path: Union[str, Path],
    create_dirs: bool = True
) -> None:
    """
    Validate output file path for saving ASCII art.

    Args:
        path: Output file path
        create_dirs: Whether to create directories if they don't exist

    Raises:
        ValidationError: If path validation fails
    """
    path = Path(path) if isinstance(path, str) else path

    # Check if directory exists or create it
    if not path.parent.exists():
        if create_dirs:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Failed to create directory: {e}")
        else:
            raise ValidationError(f"Directory does not exist: {path.parent}")

    # Check if path is writable
    try:
        if path.exists():
            # Check if file can be written to
            if not os.access(path, os.W_OK):
                raise ValidationError(f"Output file is not writable: {path}")
        else:
            # Try to create and remove a temporary file
            try:
                path.touch()
                path.unlink()
            except Exception as e:
                raise ValidationError(f"Cannot write to output location: {e}")
    except Exception as e:
        raise ValidationError(f"Output path validation failed: {e}")

def validate_dimensions(
    width: int,
    height: Optional[int] = None,
    min_width: int = 10,
    max_width: int = 500,
    min_height: int = 10,
    max_height: int = 500
) -> None:
    """
    Validate dimensions for ASCII art output.

    Args:
        width: Width in characters
        height: Height in characters (optional)
        min_width: Minimum allowed width
        max_width: Maximum allowed width
        min_height: Minimum allowed height
        max_height: Maximum allowed height

    Raises:
        ValidationError: If dimensions are invalid
    """
    # Validate width
    if not isinstance(width, int):
        raise ValidationError("Width must be an integer")
    
    if width < min_width or width > max_width:
        raise ValidationError(
            f"Width must be between {min_width} and {max_width}"
        )

    # Validate height if provided
    if height is not None:
        if not isinstance(height, int):
            raise ValidationError("Height must be an integer")
        
        if height < min_height or height > max_height:
            raise ValidationError(
                f"Height must be between {min_height} and {max_height}"
            )

def validate_aspect_ratio(
    width: int,
    height: int,
    min_ratio: float = 0.25,
    max_ratio: float = 4.0
) -> None:
    """
    Validate aspect ratio of dimensions.

    Args:
        width: Width in pixels/characters
        height: Height in pixels/characters
        min_ratio: Minimum allowed aspect ratio
        max_ratio: Maximum allowed aspect ratio

    Raises:
        ValidationError: If aspect ratio is invalid
    """
    ratio = width / height
    if ratio < min_ratio or ratio > max_ratio:
        raise ValidationError(
            f"Aspect ratio {ratio:.2f} is outside allowed range "
            f"({min_ratio:.2f} to {max_ratio:.2f})"
        )

# Utility function to combine multiple validations
def validate_all(
    image_path: Union[str, Path],
    chars: List[str],
    output_path: Optional[Union[str, Path]] = None,
    width: int = 100,
    height: Optional[int] = None
) -> None:
    """
    Perform all relevant validations at once.

    Args:
        image_path: Path to input image
        chars: Character set for ASCII conversion
        output_path: Path for output file (optional)
        width: Output width in characters
        height: Output height in characters (optional)

    Raises:
        ValidationError: If any validation fails
    """
    # Validate image
    validate_image_path(image_path)

    # Validate character set
    validate_chars(chars)

    # Validate dimensions
    validate_dimensions(width, height)

    # Validate output path if provided
    if output_path:
        validate_output_path(output_path)

    # Validate aspect ratio if both dimensions are provided
    if height:
        validate_aspect_ratio(width, height)
