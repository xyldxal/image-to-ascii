import pytest
from pathlib import Path
import shutil
import tempfile
from PIL import Image
import numpy as np

from src.processor.image_processor import ImageProcessor
from src.processor.char_processor import CharacterProcessor
from src.utils.file_handlers import FileHandler
from src.utils.validators import ValidationError
from src.config.settings import SettingsManager

# Fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_image(temp_dir):
    """Create a sample image for testing."""
    image_path = temp_dir / "test_image.png"
    # Create a simple gradient image
    array = np.linspace(0, 255, 100*100).reshape(100, 100).astype(np.uint8)
    image = Image.fromarray(array)
    image.save(image_path)
    return image_path

@pytest.fixture
def image_processor():
    """Create an ImageProcessor instance."""
    return ImageProcessor()

@pytest.fixture
def char_processor():
    """Create a CharacterProcessor instance."""
    return CharacterProcessor()

@pytest.fixture
def file_handler(temp_dir):
    """Create a FileHandler instance with temporary directory."""
    return FileHandler(output_dir=temp_dir, temp_dir=temp_dir)

@pytest.fixture
def settings_manager(temp_dir):
    """Create a SettingsManager instance with temporary config file."""
    return SettingsManager(config_path=temp_dir / "config.json")

# Image Processor Tests
class TestImageProcessor:
    def test_init(self, image_processor):
        """Test ImageProcessor initialization."""
        assert image_processor is not None
        assert hasattr(image_processor, '_width')

    def test_image_to_ascii(self, image_processor, sample_image):
        """Test basic image to ASCII conversion."""
        ascii_art = image_processor.image_to_ascii(sample_image)
        assert isinstance(ascii_art, str)
        assert len(ascii_art) > 0
        assert '\n' in ascii_art

    def test_invalid_image_path(self, image_processor):
        """Test handling of invalid image path."""
        with pytest.raises(FileNotFoundError):
            image_processor.image_to_ascii("nonexistent.jpg")

    def test_custom_width(self, image_processor, sample_image):
        """Test ASCII conversion with custom width."""
        width = 50
        ascii_art = image_processor.image_to_ascii(sample_image, width=width)
        first_line = ascii_art.split('\n')[0]
        assert len(first_line) == width

    @pytest.mark.parametrize("width", [10, 50, 100])
    def test_multiple_widths(self, image_processor, sample_image, width):
        """Test ASCII conversion with various widths."""
        ascii_art = image_processor.image_to_ascii(sample_image, width=width)
        first_line = ascii_art.split('\n')[0]
        assert len(first_line) == width

# Character Processor Tests
class TestCharacterProcessor:
    def test_init(self, char_processor):
        """Test CharacterProcessor initialization."""
        assert char_processor is not None
        assert len(char_processor.get_chars()) > 0

    def test_custom_chars(self):
        """Test setting custom characters."""
        processor = CharacterProcessor("MATRIX")
        chars = processor.get_chars()
        assert all(c in "MATRIX" for c in chars)
        assert len(chars) == len(set(chars))  # No duplicates

    def test_invalid_chars(self):
        """Test handling of invalid character sets."""
        with pytest.raises(ValidationError):  # Changed from ValueError to ValidationError
            CharacterProcessor("")  # Empty string

    def test_char_order(self):
        """Test character order preservation."""
        test_chars = "ABCDEF"
        processor = CharacterProcessor(test_chars)
        assert "".join(processor.get_chars()) == test_chars

# File Handler Tests
class TestFileHandler:
    def test_init(self, file_handler, temp_dir):
        """Test FileHandler initialization."""
        assert file_handler.output_dir == temp_dir
        assert file_handler.temp_dir == temp_dir

    def test_save_ascii_art(self, file_handler, temp_dir):
        """Test saving ASCII art to file."""
        ascii_art = "Test ASCII Art"
        output_path = temp_dir / "output.txt"
        file_handler.save_ascii_art(ascii_art, output_path)
        assert output_path.exists()
        with open(output_path) as f:
            assert f.read() == ascii_art

    def test_save_with_metadata(self, file_handler, temp_dir):
        """Test saving ASCII art with metadata."""
        ascii_art = "Test ASCII Art"
        metadata = {"test": "metadata"}
        output_path = temp_dir / "output.txt"
        file_handler.save_ascii_art(ascii_art, output_path, metadata)
        assert output_path.with_suffix('.meta.json').exists()

# Settings Manager Tests
class TestSettingsManager:
    def test_init(self, settings_manager):
        """Test SettingsManager initialization."""
        assert settings_manager is not None
        assert hasattr(settings_manager, 'settings')

    def test_default_settings(self, settings_manager):
        """Test default settings values."""
        ascii_settings = settings_manager.get_ascii_art_settings()
        assert ascii_settings.width == 100
        assert ascii_settings.maintain_aspect_ratio is True

    def test_update_settings(self, settings_manager):
        """Test updating settings."""
        settings_manager.update_ascii_art_settings(width=150)
        ascii_settings = settings_manager.get_ascii_art_settings()
        assert ascii_settings.width == 150

    def test_save_load_settings(self, settings_manager, temp_dir):
        """Test saving and loading settings."""
        settings_manager.update_ascii_art_settings(width=200)
        settings_manager._save_settings()
        
        # Create new settings manager instance
        new_settings = SettingsManager(config_path=temp_dir / "config.json")
        assert new_settings.get_ascii_art_settings().width == 200

# Integration Tests
class TestIntegration:
    def test_full_conversion_process(self, image_processor, file_handler, sample_image, temp_dir):
        """Test complete image to ASCII conversion and saving process."""
        # Convert image to ASCII
        ascii_art = image_processor.image_to_ascii(sample_image)
        
        # Save ASCII art
        output_path = temp_dir / "output.txt"
        file_handler.save_ascii_art(ascii_art, output_path)
        
        # Verify output
        assert output_path.exists()
        with open(output_path) as f:
            saved_art = f.read()
        assert saved_art == ascii_art

    def test_batch_processing(self, image_processor, file_handler, temp_dir):
        """Test batch processing of multiple images."""
        # Create multiple test images
        image_paths = []
        for i in range(3):
            path = temp_dir / f"test_image_{i}.png"
            array = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
            Image.fromarray(array).save(path)
            image_paths.append(path)

        # Process each image
        output_paths = []
        for path in image_paths:
            ascii_art = image_processor.image_to_ascii(path)
            output_path = temp_dir / f"{path.stem}_ascii.txt"
            file_handler.save_ascii_art(ascii_art, output_path)
            output_paths.append(output_path)

        # Verify outputs
        assert all(path.exists() for path in output_paths)