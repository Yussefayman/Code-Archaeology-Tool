"""Tests for AST analyzer."""

from pathlib import Path

import pytest

from code_archaeology.analyzers import ASTAnalyzer


def test_ast_analyzer_init(sample_repo: Path) -> None:
    """Test AST analyzer initialization."""
    analyzer = ASTAnalyzer(str(sample_repo))
    assert analyzer.repo_path == sample_repo


def test_ast_analyzer_invalid_path() -> None:
    """Test AST analyzer with invalid path."""
    with pytest.raises(ValueError):
        ASTAnalyzer("/nonexistent/path")


def test_analyze_file(sample_repo: Path) -> None:
    """Test analyzing a single file."""
    analyzer = ASTAnalyzer(str(sample_repo))
    simple_file = sample_repo / "simple.py"

    analysis = analyzer.analyze_file(str(simple_file))

    assert analysis is not None
    assert analysis.file_path == str(simple_file)
    assert analysis.language == "python"
    assert len(analysis.symbols) > 0
    assert any(s.name == "hello" for s in analysis.symbols)
    assert any(s.name == "add" for s in analysis.symbols)


def test_analyze_repository(sample_repo: Path) -> None:
    """Test analyzing entire repository."""
    analyzer = ASTAnalyzer(str(sample_repo))
    analyses = analyzer.analyze_repository()

    assert len(analyses) > 0
    assert "simple.py" in analyses
    assert "complex.py" in analyses
    assert "main.py" in analyses


def test_find_entry_points(sample_repo: Path) -> None:
    """Test finding entry points."""
    analyzer = ASTAnalyzer(str(sample_repo))
    entry_points = analyzer.find_entry_points()

    assert len(entry_points) > 0
    assert any("main.py" in ep for ep in entry_points)


def test_get_all_symbols(sample_repo: Path) -> None:
    """Test getting all symbols."""
    analyzer = ASTAnalyzer(str(sample_repo))
    symbols = analyzer.get_all_symbols()

    assert len(symbols) > 0
    assert any(s.name == "hello" for s in symbols)
    assert any(s.name == "DataProcessor" for s in symbols)


def test_python_symbol_extraction(sample_repo: Path) -> None:
    """Test Python-specific symbol extraction."""
    analyzer = ASTAnalyzer(str(sample_repo))
    simple_file = sample_repo / "simple.py"

    analysis = analyzer.analyze_file(str(simple_file))

    # Check for functions
    functions = [s for s in analysis.symbols if s.type == "function"]
    assert len(functions) >= 2
    assert any(f.name == "hello" for f in functions)
    assert any(f.name == "add" for f in functions)

    # Check for classes
    complex_file = sample_repo / "complex.py"
    complex_analysis = analyzer.analyze_file(str(complex_file))
    classes = [s for s in complex_analysis.symbols if s.type == "class"]
    assert len(classes) >= 1
    assert any(c.name == "DataProcessor" for c in classes)
