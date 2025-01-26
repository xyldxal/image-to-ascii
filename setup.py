from setuptools import setup, find_packages

setup(
    name="ascii-art-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'Pillow>=9.5.0',
        'rembg>=2.0.50',
        'numpy>=1.24.3',
        'colorama>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'ascii-art=main:main',
        ],
    },
)