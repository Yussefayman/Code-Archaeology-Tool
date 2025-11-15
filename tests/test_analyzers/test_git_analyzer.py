"""Tests for git analyzer."""

from pathlib import Path

import pytest

from code_archaeology.analyzers import GitAnalyzer


def test_git_analyzer_init(sample_repo: Path) -> None:
    """Test git analyzer initialization."""
    analyzer = GitAnalyzer(str(sample_repo))
    assert analyzer.repo_path == sample_repo


def test_git_analyzer_invalid_path() -> None:
    """Test git analyzer with invalid path."""
    with pytest.raises(ValueError):
        GitAnalyzer("/nonexistent/path")


def test_git_analyzer_non_git_repo(sample_non_git_repo: Path) -> None:
    """Test git analyzer with non-git repository."""
    with pytest.raises(ValueError, match="Not a git repository"):
        GitAnalyzer(str(sample_non_git_repo))


def test_get_file_history(sample_repo: Path) -> None:
    """Test getting file history."""
    analyzer = GitAnalyzer(str(sample_repo))
    history = analyzer.get_file_history("simple.py")

    assert history is not None
    assert history.file_path == "simple.py"
    assert history.commit_count >= 2  # We made 2 commits
    assert len(history.authors) > 0


def test_get_total_commits(sample_repo: Path) -> None:
    """Test getting total commits."""
    analyzer = GitAnalyzer(str(sample_repo))
    total = analyzer.get_total_commits()

    assert total >= 2  # We made 2 commits in the fixture


def test_is_actively_maintained(sample_repo: Path) -> None:
    """Test checking if repository is actively maintained."""
    analyzer = GitAnalyzer(str(sample_repo))
    # Since we just created the repo, it should be active
    assert analyzer.is_actively_maintained() is True


def test_get_hotspots(sample_repo: Path) -> None:
    """Test identifying file hotspots."""
    analyzer = GitAnalyzer(str(sample_repo))
    hotspots = analyzer.get_hotspots(limit=5)

    assert len(hotspots) > 0
    # simple.py should be in hotspots since we modified it twice
    assert any(h.file_path == "simple.py" for h in hotspots)


def test_get_contributor_stats(sample_repo: Path) -> None:
    """Test getting contributor statistics."""
    analyzer = GitAnalyzer(str(sample_repo))
    stats = analyzer.get_contributor_stats()

    assert len(stats) > 0
    # Should have our test user
    assert any(s.name == "Test User" for s in stats)
    assert any(s.email == "test@example.com" for s in stats)
