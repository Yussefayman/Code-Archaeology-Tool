"""Tests for complexity analyzer."""

from pathlib import Path

import pytest

from code_archaeology.analyzers import ComplexityAnalyzer


def test_complexity_analyzer_init(sample_repo: Path) -> None:
    """Test complexity analyzer initialization."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    assert analyzer.repo_path == sample_repo


def test_analyze_file(sample_repo: Path) -> None:
    """Test analyzing a single file's complexity."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    simple_file = sample_repo / "simple.py"

    complexity = analyzer.analyze_file(str(simple_file))

    assert complexity is not None
    assert complexity.file_path == str(simple_file)
    assert complexity.average_complexity >= 0
    assert len(complexity.functions) > 0


def test_analyze_repository(sample_repo: Path) -> None:
    """Test analyzing repository complexity."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    results = analyzer.analyze_repository()

    assert len(results) > 0
    assert "simple.py" in results or any("simple.py" in path for path in results.keys())


def test_get_simple_files(sample_repo: Path) -> None:
    """Test getting simple files."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    simple_files = analyzer.get_simple_files(threshold=10)

    assert len(simple_files) > 0
    # All files should have low complexity
    for file in simple_files:
        assert file.average_complexity <= 10


def test_get_complex_files(sample_repo: Path) -> None:
    """Test getting complex files."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    # Use a low threshold to get some results
    complex_files = analyzer.get_complex_files(threshold=5)

    # Should return files sorted by complexity
    if len(complex_files) > 1:
        assert complex_files[0].average_complexity >= complex_files[-1].average_complexity


def test_generate_complexity_report(sample_repo: Path) -> None:
    """Test generating complexity report."""
    analyzer = ComplexityAnalyzer(str(sample_repo))
    report = analyzer.generate_complexity_report()

    assert "total_files" in report
    assert "average_complexity" in report
    assert "high_risk_files" in report
    assert "simple_files" in report
    assert "complex_files" in report
    assert report["total_files"] > 0


def test_classify_complexity(sample_repo: Path) -> None:
    """Test complexity classification."""
    analyzer = ComplexityAnalyzer(str(sample_repo))

    assert analyzer._classify_complexity(3) == "simple"
    assert analyzer._classify_complexity(7) == "moderate"
    assert analyzer._classify_complexity(15) == "complex"
    assert analyzer._classify_complexity(25) == "very_complex"


def test_determine_risk_level(sample_repo: Path) -> None:
    """Test risk level determination."""
    analyzer = ComplexityAnalyzer(str(sample_repo))

    # High risk: high complexity, low maintainability
    assert analyzer._determine_risk_level(25, 5) == "high"

    # Medium risk
    assert analyzer._determine_risk_level(12, 15) == "medium"

    # Low risk: low complexity, high maintainability
    assert analyzer._determine_risk_level(3, 25) == "low"
