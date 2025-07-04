#!/usr/bin/env python3
"""
Setup script for TTS Tester GUI
A comprehensive GUI application for testing Coqui TTS models with speaker tagging and timing.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "TTS Tester GUI - A comprehensive GUI for testing Coqui TTS models"

setup(
    name="tts-tester-gui",
    version="1.0.0",
    description="A comprehensive GUI application for testing Coqui TTS models with speaker tagging and timing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="TTS Tester Team",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "TTS>=0.22.0",
        "torch>=2.0.0",
        "pygame>=2.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "audio": [
            "soundfile>=0.12.0",
            "librosa>=0.10.0",
            "pydub>=0.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tts-tester=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    keywords="tts text-to-speech coqui gui testing audio synthesis",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
) 