"""Tool for creating complexity visualization and maps."""

from typing import Any
from langchain.tools import BaseTool
from pydantic import Field

from onboarding_agent.analyzers import ComplexityAnalyzer


class ComplexityMapTool(BaseTool):
    """Tool to create a complexity map of the codebase."""

    name: str = "create_complexity_map"
    description: str = """
    Creates a visual complexity map showing which parts of the codebase are simple vs complex.

    No input required. Returns a complexity analysis with:
    - Simple files (good for beginners)
    - Complex files (require more experience)
    - Risk assessment

    Helps new developers know which areas are approachable.
    """

    repo_path: str = Field(description="Path to the repository")
    complexity_analyzer: Any = Field(default=None, exclude=True)

    def __init__(self, repo_path: str, **kwargs: Any):
        """Initialize the complexity map tool.

        Args:
            repo_path: Path to the repository
            **kwargs: Additional arguments
        """
        super().__init__(repo_path=repo_path, **kwargs)
        self.complexity_analyzer = ComplexityAnalyzer(repo_path)

    def _run(self, query: str = "") -> str:
        """Create a complexity map.

        Args:
            query: Optional query (not used, for compatibility)

        Returns:
            Formatted complexity map
        """
        # Generate comprehensive complexity report
        report = self.complexity_analyzer.generate_complexity_report()

        # Get detailed file complexities
        simple_files = self.complexity_analyzer.get_simple_files(threshold=5)
        complex_files = self.complexity_analyzer.get_complex_files(threshold=10)

        # Format output
        result = "**Codebase Complexity Map**\n\n"

        # Overview
        result += "**Overview:**\n"
        result += f"- Total Python files analyzed: {report['total_files']}\n"
        result += f"- Average complexity: {report['average_complexity']:.2f}\n"
        result += f"- High-risk files: {len(report['high_risk_files'])}\n\n"

        # Simple files (good starting points)
        result += "**🟢 Simple Files** (Great for beginners):\n\n"
        if simple_files:
            for i, file in enumerate(simple_files[:8], 1):
                result += f"{i}. **{file.file_path}**\n"
                result += f"   - Complexity: {file.average_complexity:.1f}\n"
                result += f"   - Maintainability: {file.maintainability_index:.1f}/100\n"
                result += f"   - Risk: {file.risk_level}\n"
                result += "   - 💡 Good for learning the codebase\n\n"
        else:
            result += "No simple files found.\n\n"

        # Moderate complexity files
        result += "\n**🟡 Moderate Complexity Files:**\n\n"
        all_files = self.complexity_analyzer.analyze_repository()
        moderate_files = [
            fc
            for fc in all_files.values()
            if 5 < fc.average_complexity <= 10
        ]
        moderate_files.sort(key=lambda x: x.average_complexity)

        if moderate_files:
            for i, file in enumerate(moderate_files[:5], 1):
                result += f"{i}. {file.file_path} (complexity: {file.average_complexity:.1f})\n"
        else:
            result += "No moderate complexity files found.\n"

        # Complex files
        result += "\n\n**🔴 Complex Files** (Requires experience):\n\n"
        if complex_files:
            for i, file in enumerate(complex_files[:8], 1):
                result += f"{i}. **{file.file_path}**\n"
                result += f"   - Complexity: {file.average_complexity:.1f}\n"
                result += f"   - Max complexity: {file.max_complexity}\n"
                result += f"   - Maintainability: {file.maintainability_index:.1f}/100\n"
                result += f"   - Risk: {file.risk_level}\n"
                result += "   - ⚠️  Study simpler files first\n\n"
        else:
            result += "No highly complex files found.\n\n"

        # High-risk files
        if report["high_risk_files"]:
            result += "\n**⚠️  High-Risk Files** (Technical debt areas):\n\n"
            for i, file_path in enumerate(report["high_risk_files"][:5], 1):
                result += f"{i}. {file_path}\n"

        # Recommendations
        result += "\n\n**Recommendations for New Developers:**\n\n"
        result += "1. **Start with Simple Files**: Begin with the green (simple) files listed above\n"
        result += "2. **Progress Gradually**: Move to moderate complexity files as you understand the patterns\n"
        result += "3. **Avoid High-Risk Areas**: Stay away from red (complex) files until you're comfortable\n"
        result += "4. **Ask for Help**: Complex files often require team knowledge - don't hesitate to ask\n"

        # Complexity legend
        result += "\n\n**Complexity Scale:**\n"
        result += "- 🟢 Simple (1-5): Easy to understand, good for beginners\n"
        result += "- 🟡 Moderate (6-10): Requires some experience\n"
        result += "- 🟠 Complex (11-20): Advanced understanding needed\n"
        result += "- 🔴 Very Complex (20+): Expert-level, potential technical debt\n"

        return result

    async def _arun(self, query: str = "") -> str:
        """Async version of _run."""
        return self._run(query)
