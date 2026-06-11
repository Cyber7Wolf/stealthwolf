#!/usr/bin/env python3
"""
StealthWolf Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stealthwolf",
    version="1.0.0",
    author="CyberWolf Security",
    description="Advanced data smuggling and steganography framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/stealthwolf",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "PyPDF2>=3.0.0",
        "reportlab>=4.0.0",
        "watchdog>=3.0.0",
        "scipy>=1.9.0",
        "scikit-learn>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "stealthwolf=stealthwolf:main",
        ],
    },
)
