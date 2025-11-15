"""Code complexity analysis using radon and custom metrics."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit


@dataclass
class ComplexityMetrics:
    """Complexity metrics for a code entity."""

    name: str
    file_path: str
    line_start: int
    cyclomatic_complexity: int
    maintainability_index: float
    halstead_difficulty: float
    classification: str  # simple, moderate, complex, very_complex


@dataclass
class FileComplexity:
    """Aggregated complexity metrics for a file."""

    file_path: str
    average_complexity: float
    max_complexity: int
    maintainability_index: float
    functions: List[ComplexityMetrics]
    risk_level: str  # low, medium, high


class ComplexityAnalyzer:
    """Analyzes code complexity using multiple metrics."""

    # Complexity thresholds
    SIMPLE = 5
    MODERATE = 10
    COMPLEX = 20

    def __init__(self, repo_path: str) -> None:
        """Initialize complexity analyzer.

        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def analyze_file(self, file_path: str) -> Optional[FileComplexity]:
        """Analyze complexity of a single file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            FileComplexity object or None if file cannot be analyzed
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return None

        # Currently only supports Python
        if not file_path.endswith(".py"):
            return None

        try:
            with open(file_path_obj, "r", encoding="utf-8") as f:
                content = f.read()

            # Calculate cyclomatic complexity for functions
            cc_results = cc_visit(content)
            functions = []

            for result in cc_results:
                classification = self._classify_complexity(result.complexity)
                functions.append(
                    ComplexityMetrics(
                        name=result.name,
                        file_path=str(file_path_obj),
                        line_start=result.lineno,
                        cyclomatic_complexity=result.complexity,
                        maintainability_index=0.0,  # Will calculate per-file
                        halstead_difficulty=0.0,  # Will calculate per-file
                        classification=classification,
                    )
                )

            # Calculate maintainability index
            mi_score = mi_visit(content, multi=True)
            mi_value = mi_score if isinstance(mi_score, (int, float)) else 0.0

            # Calculate Halstead metrics
            h_metrics = h_visit(content)
            h_difficulty = h_metrics.total.difficulty if h_metrics.total else 0.0

            # Calculate aggregate metrics
            complexities = [f.cyclomatic_complexity for f in functions]
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0
            max_complexity = max(complexities) if complexities else 0

            # Determine risk level
            risk_level = self._determine_risk_level(avg_complexity, mi_value)

            return FileComplexity(
                file_path=str(file_path_obj),
                average_complexity=avg_complexity,
                max_complexity=max_complexity,
                maintainability_index=mi_value,
                functions=functions,
                risk_level=risk_level,
            )

        except Exception as e:
            print(f"Error analyzing complexity for {file_path}: {e}")
            return None

    def _classify_complexity(self, complexity: int) -> str:
        """Classify complexity score into categories.

        Args:
            complexity: Cyclomatic complexity score

        Returns:
            Classification string
        """
        if complexity <= self.SIMPLE:
            return "simple"
        elif complexity <= self.MODERATE:
            return "moderate"
        elif complexity <= self.COMPLEX:
            return "complex"
        else:
            return "very_complex"

    def _determine_risk_level(self, avg_complexity: float, mi_index: float) -> str:
        """Determine overall risk level for a file.

        Args:
            avg_complexity: Average cyclomatic complexity
            mi_index: Maintainability index (0-100, higher is better)

        Returns:
            Risk level string
        """
        # Maintainability Index thresholds:
        # 0-9: Difficult to maintain
        # 10-19: Moderately maintainable
        # 20+: Highly maintainable

        if avg_complexity > self.COMPLEX or mi_index < 10:
            return "high"
        elif avg_complexity > self.MODERATE or mi_index < 20:
            return "medium"
        else:
            return "low"

    def analyze_repository(self) -> Dict[str, FileComplexity]:
        """Analyze complexity of all Python files in repository.

        Returns:
            Dictionary mapping file paths to FileComplexity objects
        """
        results = {}

        for file_path in self.repo_path.rglob("*.py"):
            # Skip common directories to ignore
            if any(
                part in file_path.parts
                for part in [
                    "node_modules",
                    ".git",
                    "__pycache__",
                    "venv",
                    "env",
                    ".venv",
                    "dist",
                    "build",
                    "tests",
                    "test",
                ]
            ):
                continue

            complexity = self.analyze_file(str(file_path))
            if complexity:
                rel_path = str(file_path.relative_to(self.repo_path))
                results[rel_path] = complexity

        return results

    def get_complex_files(self, threshold: int = 10) -> List[FileComplexity]:
        """Get files with high complexity.

        Args:
            threshold: Minimum average complexity threshold

        Returns:
            List of FileComplexity objects sorted by complexity
        """
        all_files = self.analyze_repository()
        complex_files = [
            fc for fc in all_files.values() if fc.average_complexity >= threshold
        ]
        complex_files.sort(key=lambda x: x.average_complexity, reverse=True)
        return complex_files

    def get_simple_files(self, threshold: int = 5) -> List[FileComplexity]:
        """Get files with low complexity (good starting points).

        Args:
            threshold: Maximum average complexity threshold

        Returns:
            List of FileComplexity objects sorted by complexity
        """
        all_files = self.analyze_repository()
        simple_files = [
            fc for fc in all_files.values() if fc.average_complexity <= threshold
        ]
        simple_files.sort(key=lambda x: x.average_complexity)
        return simple_files

    def generate_complexity_report(self) -> Dict[str, any]:
        """Generate a comprehensive complexity report.

        Returns:
            Dictionary with complexity statistics
        """
        all_files = self.analyze_repository()

        if not all_files:
            return {
                "total_files": 0,
                "average_complexity": 0,
                "high_risk_files": [],
                "simple_files": [],
                "complex_files": [],
            }

        all_complexities = [fc.average_complexity for fc in all_files.values()]
        avg_complexity = sum(all_complexities) / len(all_complexities)

        high_risk = [fc for fc in all_files.values() if fc.risk_level == "high"]
        simple = self.get_simple_files(threshold=5)
        complex_files = self.get_complex_files(threshold=15)

        return {
            "total_files": len(all_files),
            "average_complexity": avg_complexity,
            "high_risk_files": [fc.file_path for fc in high_risk],
            "simple_files": [fc.file_path for fc in simple[:10]],
            "complex_files": [fc.file_path for fc in complex_files[:10]],
        }
