from typing import Union, Optional, List, BinaryIO
from pathlib import Path
import os
import shutil
import json
import pickle
from datetime import datetime
from PIL import Image
import io
import logging
from ..utils.validators import validate_output_path, validate_image_path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileHandler:
    """
    Handles file operations for the ASCII art generator.
    
    Attributes:
        output_dir (Path): Directory for output files
        temp_dir (Path): Directory for temporary files
        supported_formats (set): Supported image formats
    """

    def __init__(self, output_dir: Union[str, Path] = "output", temp_dir: Union[str, Path] = "temp"):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        
        # Create necessary directories
        self._initialize_directories()

    def _initialize_directories(self) -> None:
        """Create output and temp directories if they don't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def save_ascii_art(
        self,
        ascii_art: str,
        filename: Union[str, Path],
        metadata: Optional[dict] = None
    ) -> Path:
        """
        Save ASCII art to a file with optional metadata.

        Args:
            ascii_art: The ASCII art string
            filename: Output filename
            metadata: Optional metadata dictionary

        Returns:
            Path to the saved file
        """
        output_path = self.output_dir / filename
        validate_output_path(output_path)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(ascii_art)

            # Save metadata if provided
            if metadata:
                meta_path = output_path.with_suffix('.meta.json')
                self.save_metadata(metadata, meta_path)

            logger.info(f"ASCII art saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error saving ASCII art: {e}")
            raise

    def load_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        Load and validate an image file.

        Args:
            image_path: Path to the image file

        Returns:
            PIL Image object
        """
        image_path = Path(image_path)
        validate_image_path(image_path)

        try:
            image = Image.open(image_path)
            return image
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise

    def save_image(
        self,
        image: Image.Image,
        filename: Union[str, Path],
        format: Optional[str] = None
    ) -> Path:
        """
        Save a PIL Image object to file.

        Args:
            image: PIL Image object
            filename: Output filename
            format: Image format (e.g., 'PNG', 'JPEG')

        Returns:
            Path to the saved file
        """
        output_path = self.output_dir / filename
        format = format or output_path.suffix[1:].upper()

        try:
            image.save(output_path, format=format)
            logger.info(f"Image saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            raise

    def save_metadata(self, metadata: dict, filepath: Union[str, Path]) -> None:
        """Save metadata to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4)
            logger.info(f"Metadata saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise

    def create_backup(self, filepath: Union[str, Path]) -> Path:
        """
        Create a backup of a file.

        Args:
            filepath: Path to the file to backup

        Returns:
            Path to the backup file
        """
        filepath = Path(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = filepath.with_name(f"{filepath.stem}_backup_{timestamp}{filepath.suffix}")

        try:
            shutil.copy2(filepath, backup_path)
            logger.info(f"Backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """
        Clean up temporary files older than specified age.

        Args:
            max_age_hours: Maximum age of files in hours
        """
        current_time = datetime.now().timestamp()
        
        try:
            for file_path in self.temp_dir.glob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_hours * 3600:
                        file_path.unlink()
                        logger.info(f"Deleted old temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def save_project(
        self,
        project_data: dict,
        filename: Union[str, Path]
    ) -> Path:
        """
        Save project data including ASCII art and settings.

        Args:
            project_data: Dictionary containing project data
            filename: Output filename

        Returns:
            Path to the saved project file
        """
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(project_data, f)
            logger.info(f"Project saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            raise

    def load_project(self, filepath: Union[str, Path]) -> dict:
        """
        Load a saved project.

        Args:
            filepath: Path to the project file

        Returns:
            Project data dictionary
        """
        try:
            with open(filepath, 'rb') as f:
                project_data = pickle.load(f)
            logger.info(f"Project loaded from {filepath}")
            return project_data
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            raise

    def export_ascii_art(
        self,
        ascii_art: str,
        filename: Union[str, Path],
        format: str = 'txt'
    ) -> Path:
        """
        Export ASCII art in various formats.

        Args:
            ascii_art: The ASCII art string
            filename: Output filename
            format: Output format ('txt', 'html', 'md')

        Returns:
            Path to the exported file
        """
        output_path = self.output_dir / f"{Path(filename).stem}.{format}"
        
        try:
            if format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
            elif format == 'html':
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><title>ASCII Art</title></head>
                <body><pre>{ascii_art}</pre></body>
                </html>
                """
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            elif format == 'md':
                md_content = f"```\n{ascii_art}\n```"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"ASCII art exported to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error exporting ASCII art: {e}")
            raise

    def get_file_info(self, filepath: Union[str, Path]) -> dict:
        """
        Get information about a file.

        Args:
            filepath: Path to the file

        Returns:
            Dictionary containing file information
        """
        filepath = Path(filepath)
        
        try:
            stats = filepath.stat()
            return {
                'name': filepath.name,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime),
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'extension': filepath.suffix,
                'path': str(filepath.absolute())
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            raise