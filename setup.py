"""
KursarScript setup.py - Legacy setup for compatibility
"""
from setuptools import setup, find_packages

setup(
    name="kursarscript",
    version="1.0.0",
    description="KursarScript (KSPL) - A virtual reality and digital-economy programming language",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="KursarScript Team",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "kursarscript=kursarscript.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Interpreters",
    ],
)
