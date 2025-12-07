from setuptools import setup, find_packages

setup(
    name="pocket-bower",
    version="0.1.0",
    description="A modular RL environment and solver suite for the card game Euchre.",
    author="RogueTrainer",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "tqdm>=4.50.0",
        "jupyter>=1.0.0",
        "matplotlib>=3.3.0",
    ],
    python_requires=">=3.7",
)
