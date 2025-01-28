# Image to ASCII Generator

## Features

- Convert images to ASCII art
- Supported file types: .png, .jpg, .jpeg, .bmp, .gif
- Optional background removal and color support
- Animation support for .gif files
- Custom characters and pattern mode
- Export output formats: .txt, .html, .md, .gif

## Instructions

```bash
# Clone repository
git clone https://github.com/xyldxal/image-to-ascii.git

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic usage

```bash
python main.py path/to/img.jpg
```

#### With options

``` bash
# Custom width
python main.py path/to/img.jpg --width 150

# Custom characters
python main.py path/to/img.jpg --chars "MARX"

# Remove background
python main.py path/to/img.jpg --remove-bg

# Color modes: foreground, background, both
python main.py path/to/img.jpg --color both

# Save to file
python main.py path/to/img.jpg --output art.txt

```

| Option | Description |
| ----------- | ----------- |
| ```--h, --help``` | Show help message and exit |
| ```--width``` | Width of ASCII art |
| ```--chars``` | Custom characters for ASCII conversion |
| ```--remove-bg``` | Remove background |
| ```--output``` | Output file path |
| ```--color {none,foreground,background,both}``` | Color mode for ASCII art |
| ```--fps``` | Frames per second for GIF animation |
| ```--format``` | Output format |





