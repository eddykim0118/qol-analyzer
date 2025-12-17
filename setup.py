"""
Setup configuration for qol-analyzer package.

Quality of Life analyzer for U.S. states using Census ACS, BLS CPI, and Tax Foundation data.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qol-analyzer",
    version="1.0.0",
    author="Jun Kim, Eddy Kim",
    author_email="",
    description="Measure Quality of Life across U.S. states using salary, housing, and cost of living data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/qol-analyzer",  # Update with actual repo URL
    packages=find_packages(exclude=["tests", "tests.*", "scripts", "docs", "data", ".venv", "venv"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qol-pipeline=scripts.run_pipeline:main",
            "qol-validate=scripts.validate_output:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
