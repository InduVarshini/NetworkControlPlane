"""Setup script for NetworkControlPlane."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="network-control-plane",
    version="0.1.0",
    description="Centralized Network Configuration, Automation, and Observability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NetworkControlPlane Contributors",
    packages=find_packages(),
    install_requires=[
        "jinja2>=3.1.0",
        "pyyaml>=6.0",
        "mininet>=2.3.0",
        "paramiko>=3.0.0",
        "flask>=2.3.0",
        "click>=8.1.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ncp=network_control_plane.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

