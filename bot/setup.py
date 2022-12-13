from setuptools import setup, find_packages
from pathlib import Path
import os

if __name__ == "__main__":
    import os

    def _read_reqs(relpath):
        fullpath = os.path.join(os.path.dirname(__file__), relpath)
        with open(fullpath) as f:
            return [
                s.strip()
                for s in f.readlines()
                if (s.strip() and not s.startswith("#"))
            ]

    REQUIREMENTS = _read_reqs("requirements.txt")

    setup(
        name="open-chat-gpt",
        packages=find_packages(),
        version="0.0.1",
        license="Apache 2.0",
        description="A Discord Bot for collecting and ranking prompts to train an Open ChatGPT",
        keywords=["machine learning", "natural language processing", "discord"],
        install_requires=REQUIREMENTS,
        classifiers=[
            "Development Status :: Alpha",
            "Intended Audience :: Developers",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "License :: OSI Approved :: Apache License",
            "Programming Language :: Python :: 3.6",
        ],
    )
