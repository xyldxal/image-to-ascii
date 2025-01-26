from typing import Dict, Any, Optional, Union
from pathlib import Path
import json
import os
from dataclasses import dataclass, asdict, field
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ASCIIArtSettings:
    """
    Data class for ASCII art conversion settings.
    """
    width: int = 100
    height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    remove_background: bool = False
    invert: bool = False
    brightness: float = 1.0
    contrast: float = 1.0

@dataclass
class CharacterSettings:
    """
    Data class for character set settings.
    """
    default_chars: str = "@#S%?*+;:,."
    custom_chars: Optional[str] = None
    min_chars: int = 2
    max_chars: int = 50
    allow_spaces: bool = True
    allow_special: bool = True
    use_color: bool = False

@dataclass
class OutputSettings:
    """
    Data class for output settings.
    """
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    backup_dir: Path = Path("backups")
    format: str = "txt"
    create_backup: bool = True
    include_metadata: bool = True
    save_original: bool = True

@dataclass
class ApplicationSettings:
    """
    Main settings class that contains all configuration options.
    """
    ascii_art: ASCIIArtSettings = field(default_factory=ASCIIArtSettings)
    character: CharacterSettings = field(default_factory=CharacterSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    
    # Additional settings
    supported_image_formats: set = field(default_factory=lambda: {'.jpg', '.jpeg', '.png', '.bmp', '.gif'})
    max_image_size: tuple = (5000, 5000)
    min_image_size: tuple = (10, 10)
    debug_mode: bool = False
    version: str = "1.0.0"

class SettingsManager:
    """
    Manages application settings including loading, saving, and validation.
    """

    def __init__(self, config_path: Union[str, Path] = "config.json"):
        """
        Initialize settings manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.settings = ApplicationSettings()
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from configuration file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                self._update_settings(data)
                logger.info("Settings loaded successfully")
            else:
                self._save_settings()  # Create default settings file
                logger.info("Created default settings file")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.info("Using default settings")

    def _save_settings(self) -> None:
        """Save current settings to configuration file."""
        try:
            # Convert settings to dictionary
            settings_dict = self._settings_to_dict()
            
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save settings
            with open(self.config_path, 'w') as f:
                json.dump(settings_dict, f, indent=4, default=str)
            
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def _settings_to_dict(self) -> dict:
        """Convert settings to dictionary format."""
        return {
            'ascii_art': asdict(self.settings.ascii_art),
            'character': asdict(self.settings.character),
            'output': {
                **asdict(self.settings.output),
                'output_dir': str(self.settings.output.output_dir),
                'temp_dir': str(self.settings.output.temp_dir),
                'backup_dir': str(self.settings.output.backup_dir)
            },
            'supported_image_formats': list(self.settings.supported_image_formats),
            'max_image_size': self.settings.max_image_size,
            'min_image_size': self.settings.min_image_size,
            'debug_mode': self.settings.debug_mode,
            'version': self.settings.version,
            'last_modified': datetime.now().isoformat()
        }

    def _update_settings(self, data: Dict[str, Any]) -> None:
        """
        Update settings from dictionary data.

        Args:
            data: Dictionary containing settings data
        """
        try:
            # Update ASCII art settings
            if 'ascii_art' in data:
                self.settings.ascii_art = ASCIIArtSettings(**data['ascii_art'])

            # Update character settings
            if 'character' in data:
                self.settings.character = CharacterSettings(**data['character'])

            # Update output settings
            if 'output' in data:
                output_data = data['output'].copy()
                output_data['output_dir'] = Path(output_data['output_dir'])
                output_data['temp_dir'] = Path(output_data['temp_dir'])
                output_data['backup_dir'] = Path(output_data['backup_dir'])
                self.settings.output = OutputSettings(**output_data)

            # Update other settings
            if 'supported_image_formats' in data:
                self.settings.supported_image_formats = set(data['supported_image_formats'])
            if 'max_image_size' in data:
                self.settings.max_image_size = tuple(data['max_image_size'])
            if 'min_image_size' in data:
                self.settings.min_image_size = tuple(data['min_image_size'])
            if 'debug_mode' in data:
                self.settings.debug_mode = data['debug_mode']
            if 'version' in data:
                self.settings.version = data['version']

        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            raise

    def get_ascii_art_settings(self) -> ASCIIArtSettings:
        """Get ASCII art conversion settings."""
        return self.settings.ascii_art

    def get_character_settings(self) -> CharacterSettings:
        """Get character set settings."""
        return self.settings.character

    def get_output_settings(self) -> OutputSettings:
        """Get output settings."""
        return self.settings.output

    def update_ascii_art_settings(self, **kwargs) -> None:
        """Update ASCII art settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings.ascii_art, key):
                setattr(self.settings.ascii_art, key, value)
        self._save_settings()

    def update_character_settings(self, **kwargs) -> None:
        """Update character settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings.character, key):
                setattr(self.settings.character, key, value)
        self._save_settings()

    def update_output_settings(self, **kwargs) -> None:
        """Update output settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings.output, key):
                setattr(self.settings.output, key, value)
        self._save_settings()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = ApplicationSettings()
        self._save_settings()

    def create_backup(self) -> Path:
        """
        Create a backup of current settings.

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_path.with_name(f"config_backup_{timestamp}.json")
        
        try:
            with open(backup_path, 'w') as f:
                json.dump(self._settings_to_dict(), f, indent=4, default=str)
            logger.info(f"Settings backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating settings backup: {e}")
            raise