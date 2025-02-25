#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Optional, List
import logging
from datetime import datetime

from src.processor.image_processor import ImageProcessor
from src.processor.char_processor import CharacterProcessor
from src.utils.file_handlers import FileHandler
from src.config.settings import SettingsManager
from src.utils.validators import ValidationError

import time
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ASCIIArtGenerator:
    """Main class for the ASCII Art Generator application."""

    def __init__(self):
        self.settings_manager = SettingsManager()
        self.file_handler = FileHandler(
            output_dir=self.settings_manager.get_output_settings().output_dir,
            temp_dir=self.settings_manager.get_output_settings().temp_dir
        )
        self.image_processor = ImageProcessor()
        self.char_processor = CharacterProcessor()

    def process_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        width: Optional[int] = None,
        remove_bg: bool = False,
        pattern_mode: bool = False,
        color_mode: str = 'none',
        chars: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Process an image and convert it to ASCII art.

        Args:
            image_path: Path to input image
            output_path: Path for output file (optional)
            width: Width of output ASCII art
            remove_bg: Whether to remove background
            pattern_mode: Use characters as repeating pattern instead of gradient'
            color_mode: Color mode for ASCII art
            chars: Custom characters for ASCII conversion
            **kwargs: Additional processing parameters
        """
        try:
            # Update settings if custom parameters provided
            ascii_settings = self.settings_manager.get_ascii_art_settings()
            if width:
                ascii_settings.width = width

            # Convert custom chars string to list if provided
            char_list = list(chars) if chars else None

            # Process image
            ascii_art = self.image_processor.image_to_ascii(
                image_path,
                width=ascii_settings.width,
                remove_bg=remove_bg,
                chars=char_list,
                pattern_mode=pattern_mode, 
                color_mode=color_mode
                
            )

            # Save output if path provided
            if output_path:
                metadata = self._create_metadata(
                        image_path=image_path,
                        ascii_settings=ascii_settings,
                        custom_chars=chars,
                        color_mode=color_mode,
                        pattern_mode=pattern_mode,
                        extra_params=kwargs
                    )
                self.file_handler.save_ascii_art(ascii_art, output_path, metadata)
            return ascii_art

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    def _create_metadata(self, image_path, ascii_settings, chars, extra_params):
        """Create metadata for ASCII art output."""
        return {
            'source_image': image_path,
            'timestamp': datetime.now().isoformat(),
            'settings': {
                'width': ascii_settings.width,
                'chars': chars,
                **extra_params
            },
            'version': self.settings_manager.settings.version
        }
    
    def process_gif(
        self,
        image_path: str,
        fps: int = 10,
        **kwargs
    ) -> None:
        """Process and display animated GIF."""
        try:
            # Get frame generator
            frames = self.image_processor.process_gif(
                image_path,
                **kwargs
            )

            # Display animation
            frame_delay = 1 / fps
            for frame in frames:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(frame)
                time.sleep(frame_delay)

        except Exception as e:
            logger.error(f"Error processing GIF: {e}")
            raise
        


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='ASCII Art Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s image.jpg
    %(prog)s image.png --width 150 --chars "MATRIX" --remove-bg
    """
    )

    parser.add_argument('input', help='Input image file')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--width', type=int, help='Width of ASCII art')
    parser.add_argument('--chars', help='Custom characters for ASCII conversion')
    parser.add_argument('--remove-bg', action='store_true', help='Remove background')
    parser.add_argument('--pattern-mode', action='store_true', 
                       help='Use characters as repeating pattern instead of gradient')
    parser.add_argument('--color', choices=['none', 'foreground', 'background', 'both'],
                       default='none', help='Color mode for ASCII art')
    parser.add_argument('--fps', type=int, default=10,
                       help='Frames per second for GIF animation')
    parser.add_argument('--format', choices=['txt', 'html', 'md'], 
                       default='txt', help='Output format')

    return parser.parse_args()

def main():
    """Main entry point for the ASCII Art Generator."""
    try:
        args = parse_arguments()
        generator = ASCIIArtGenerator()

        is_gif = args.input.lower().endswith('.gif')
        if is_gif:
                generator.process_gif(
                image_path=args.input,
                width=args.width,
                remove_bg=args.remove_bg,
                chars=list(args.chars) if args.chars else None,
                pattern_mode=args.pattern_mode,
                color_mode=args.color,
                fps=args.fps
            )
        else:
            # Process image
            ascii_art = generator.process_image(
                image_path=args.input,
                output_path=args.output,
                width=args.width,
                remove_bg=args.remove_bg,
                pattern_mode=args.pattern_mode,
                color_mode=args.color,
                chars=args.chars
            )
        
            # Print to console if no output file specified
            if not args.output:
                print(ascii_art)

        logger.info("Processing completed successfully")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()