"""Tool for generating progressive learning paths through the codebase."""

from typing import Dict, List, Any
from langchain.tools import BaseTool
from pydantic import Field

from code_archaeology.analyzers import (
    ASTAnalyzer,
    DependencyAnalyzer,
    ComplexityAnalyzer,
)


class LearningPathTool(BaseTool):
    """Tool to generate a progressive learning path for understanding a codebase area."""

    name: str = "generate_learning_path"
    description: str = """
    Generates a progressive learning path (simple to complex) for understanding a specific
    area of the codebase.

    Input should be an area or module name (e.g., "authentication", "payment processing").

    Returns an ordered list of files/modules to study, from simplest to most complex.
    """

    repo_path: str = Field(description="Path to the repository")
    ast_analyzer: Any = Field(default=None, exclude=True)
    dep_analyzer: Any = Field(default=None, exclude=True)
    complexity_analyzer: Any = Field(default=None, exclude=True)

    def __init__(self, repo_path: str, **kwargs: Any):
        """Initialize the learning path tool.

        Args:
            repo_path: Path to the repository
            **kwargs: Additional arguments
        """
        super().__init__(repo_path=repo_path, **kwargs)

        # Initialize analyzers
        self.ast_analyzer = ASTAnalyzer(repo_path)
        self.dep_analyzer = DependencyAnalyzer(repo_path)
        self.complexity_analyzer = ComplexityAnalyzer(repo_path)

    def _run(self, area: str) -> str:
        """Generate a learning path for a specific area.

        Args:
            area: Area or module to learn about

        Returns:
            Formatted learning path
        """
        # Analyze repository
        file_analyses = self.ast_analyzer.analyze_repository()
        self.dep_analyzer.build_dependency_graph(file_analyses)
        complexity_results = self.complexity_analyzer.analyze_repository()

        # Find relevant files
        relevant_files = self._find_relevant_files(area.lower(), file_analyses)

        if not relevant_files:
            return f"No files found related to '{area}'. Try a broader search term."

        # Enrich with complexity and dependency info
        enriched_files = []
        for file_path in relevant_files:
            complexity_info = complexity_results.get(file_path)
            dep_info = self.dep_analyzer.modules.get(file_path)

            avg_complexity = (
                complexity_info.average_complexity if complexity_info else 0
            )
            dependency_count = dep_info.dependency_count if dep_info else 0
            dependency_depth = self.dep_analyzer.get_dependency_depth(file_path)

            # Calculate learning order score (lower = should learn first)
            # Factors: complexity, dependencies, depth
            learning_score = (
                avg_complexity * 2 + dependency_count * 3 + dependency_depth * 5
            )

            enriched_files.append(
                {
                    "path": file_path,
                    "complexity": avg_complexity,
                    "dependencies": dependency_count,
                    "depth": dependency_depth,
                    "score": learning_score,
                    "risk_level": complexity_info.risk_level if complexity_info else "unknown",
                }
            )

        # Sort by learning score (ascending)
        enriched_files.sort(key=lambda x: x["score"])

        # Generate learning path
        result = f"**Learning Path for: '{area}'**\n\n"
        result += "Study these files in order (simple → complex):\n\n"

        for i, file_info in enumerate(enriched_files, 1):
            difficulty = self._get_difficulty_label(file_info["complexity"])

            result += f"{i}. **{file_info['path']}**\n"
            result += f"   - Difficulty: {difficulty}\n"
            result += f"   - Complexity: {file_info['complexity']:.1f}\n"
            result += f"   - Dependencies: {file_info['dependencies']}\n"
            result += f"   - Dependency Depth: {file_info['depth']}\n"

            # Add learning tip
            if i == 1:
                result += "   - 💡 **Start here!** This is the simplest file in this area.\n"
            elif file_info["complexity"] > 15:
                result += "   - ⚠️  This file is complex. Make sure you understand the simpler files first.\n"

            result += "\n"

        # Add summary
        result += "\n**Learning Tips:**\n"
        result += "- Start with the files at the top of the list\n"
        result += "- Understand each file's purpose before moving to the next\n"
        result += "- Pay attention to how files depend on each other\n"
        result += f"- Total files to review: {len(enriched_files)}\n"

        return result

    def _find_relevant_files(
        self, area: str, file_analyses: Dict[str, Any]
    ) -> List[str]:
        """Find files relevant to a specific area.

        Args:
            area: Area or module name
            file_analyses: Dictionary of file analyses

        Returns:
            List of relevant file paths
        """
        relevant = []
        keywords = area.split()

        for file_path in file_analyses.keys():
            file_path_lower = file_path.lower()

            # Check if any keyword is in the file path
            if any(keyword in file_path_lower for keyword in keywords):
                relevant.append(file_path)

        return relevant

    def _get_difficulty_label(self, complexity: float) -> str:
        """Get difficulty label based on complexity score.

        Args:
            complexity: Complexity score

        Returns:
            Difficulty label
        """
        if complexity <= 5:
            return "Beginner 🟢"
        elif complexity <= 10:
            return "Intermediate 🟡"
        elif complexity <= 20:
            return "Advanced 🟠"
        else:
            return "Expert 🔴"

    async def _arun(self, area: str) -> str:
        """Async version of _run."""
        return self._run(area)
