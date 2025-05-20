from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="log_analyzer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tqdm>=4.0.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "log-analyzer=cli:main",
        ],
    },
    python_requires=">=3.8",
)
