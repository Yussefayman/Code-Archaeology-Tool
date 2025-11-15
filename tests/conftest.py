"""Pytest configuration and fixtures."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def sample_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a sample repository for testing.

    Args:
        tmp_path: Pytest temporary path

    Yields:
        Path to the sample repository
    """
    repo_path = tmp_path / "sample_repo"
    repo_path.mkdir()

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=repo_path, check=False, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=False,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=False,
        capture_output=True,
    )

    # Set default branch
    subprocess.run(
        ["git", "config", "init.defaultBranch", "main"],
        cwd=repo_path,
        check=False,
        capture_output=True,
    )

    # Create sample Python files
    # Simple file
    simple_file = repo_path / "simple.py"
    simple_file.write_text(
        '''"""Simple module."""


def hello(name: str) -> str:
    """Say hello.

    Args:
        name: Name to greet

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
    )

    # Complex file
    complex_file = repo_path / "complex.py"
    complex_file.write_text(
        '''"""Complex module with higher complexity."""


class DataProcessor:
    """Process data with various methods."""

    def __init__(self, data):
        self.data = data

    def process(self, mode="default"):
        """Process data based on mode."""
        if mode == "default":
            result = self._default_process()
        elif mode == "advanced":
            result = self._advanced_process()
        elif mode == "expert":
            result = self._expert_process()
        else:
            result = None

        if result is not None:
            if isinstance(result, list):
                if len(result) > 0:
                    return result
                else:
                    return []
            elif isinstance(result, dict):
                if result:
                    return result
                else:
                    return {}
            else:
                return result
        return None

    def _default_process(self):
        return [x * 2 for x in self.data]

    def _advanced_process(self):
        return {i: x for i, x in enumerate(self.data)}

    def _expert_process(self):
        return sum(self.data)
'''
    )

    # Main entry point
    main_file = repo_path / "main.py"
    main_file.write_text(
        '''"""Main entry point."""

from simple import hello
from complex import DataProcessor


def main():
    """Main function."""
    print(hello("World"))

    processor = DataProcessor([1, 2, 3, 4, 5])
    result = processor.process("default")
    print(result)


if __name__ == "__main__":
    main()
'''
    )

    # Create a utils directory
    utils_dir = repo_path / "utils"
    utils_dir.mkdir()

    utils_file = utils_dir / "helpers.py"
    utils_file.write_text(
        '''"""Helper utilities."""


def format_output(data):
    """Format data for output."""
    return str(data)


def validate_input(data):
    """Validate input data."""
    return data is not None
'''
    )

    # Commit the files
    subprocess.run(["git", "add", "."], cwd=repo_path, check=False, capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )

    # Make some changes for history (only if first commit succeeded)
    if result.returncode == 0:
        simple_file.write_text(
            simple_file.read_text() + "\n\ndef goodbye(name: str) -> str:\n    return f'Goodbye, {name}!'\n"
        )
        subprocess.run(["git", "add", "."], cwd=repo_path, check=False, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add goodbye function"],
            cwd=repo_path,
            check=False,
            capture_output=True,
        )

    yield repo_path

    # Cleanup is automatic with tmp_path


@pytest.fixture
def sample_non_git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a sample non-git repository for testing.

    Args:
        tmp_path: Pytest temporary path

    Yields:
        Path to the sample repository
    """
    repo_path = tmp_path / "non_git_repo"
    repo_path.mkdir()

    # Create sample Python file
    sample_file = repo_path / "sample.py"
    sample_file.write_text(
        '''"""Sample module."""


def sample_function():
    """Sample function."""
    return "Hello"
'''
    )

    yield repo_path
