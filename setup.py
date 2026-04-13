"""
Setup script for Clipify - AI-Powered Viral Clip Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="clipify",
    version="1.0.0",
    author="Clipify Team",
    author_email="",
    description="AI-Powered Viral Clip Generator from Videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/princekjha-dev/Clipify",
    project_urls={
        "Issues": "https://github.com/princekjha-dev/Clipify/issues",
        "Discussions": "https://github.com/princekjha-dev/Clipify/discussions",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "clipify=clipify:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
