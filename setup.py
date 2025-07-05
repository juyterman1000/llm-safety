from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="llm-guard",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Lightweight, fast, and accurate safety toolkit for LLM applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-guard",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/llm-guard/issues",
        "Documentation": "https://llm-guard.readthedocs.io",
        "Source Code": "https://github.com/yourusername/llm-guard",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "isort>=5.0",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.0",
        ],
        "ml": [
            "onnxruntime>=1.12",
            "transformers>=4.0",
            "torch>=1.9",
        ]
    },
    entry_points={
        "console_scripts": [
            "llm-guard=llm_guard.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "llm_guard": ["data/*.json", "data/models/*.onnx"],
    },
    keywords=[
        "llm", "safety", "ai", "security", "prompt-injection", 
        "pii", "toxicity", "content-moderation", "nlp"
    ],
)
