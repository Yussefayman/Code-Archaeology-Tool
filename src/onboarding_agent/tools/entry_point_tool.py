"""Tool for suggesting entry points for specific tasks."""

from typing import Dict, List, Any
from langchain.tools import BaseTool
from pydantic import Field

from onboarding_agent.analyzers import (
    ASTAnalyzer,
    DependencyAnalyzer,
    ComplexityAnalyzer,
    GitAnalyzer,
)


class EntryPointTool(BaseTool):
    """Tool to suggest where to start for a specific development task."""

    name: str = "suggest_entry_points"
    description: str = """
    Suggests the best files and modules to start with for a specific development task.

    Input should be a task description (e.g., "add a new payment method", "fix authentication bug").

    Returns a list of suggested entry points with reasoning.
    """

    repo_path: str = Field(description="Path to the repository")
    ast_analyzer: Any = Field(default=None, exclude=True)
    dep_analyzer: Any = Field(default=None, exclude=True)
    complexity_analyzer: Any = Field(default=None, exclude=True)
    git_analyzer: Any = Field(default=None, exclude=True)

    def __init__(self, repo_path: str, **kwargs: Any):
        """Initialize the entry point tool.

        Args:
            repo_path: Path to the repository
            **kwargs: Additional arguments
        """
        super().__init__(repo_path=repo_path, **kwargs)

        # Initialize analyzers
        self.ast_analyzer = ASTAnalyzer(repo_path)
        self.dep_analyzer = DependencyAnalyzer(repo_path)
        self.complexity_analyzer = ComplexityAnalyzer(repo_path)
        try:
            self.git_analyzer = GitAnalyzer(repo_path)
        except ValueError:
            self.git_analyzer = None  # Not a git repo

    def _run(self, task_description: str) -> str:
        """Suggest entry points for a task.

        Args:
            task_description: Description of the task

        Returns:
            Formatted string with suggestions
        """
        # Analyze repository
        file_analyses = self.ast_analyzer.analyze_repository()

        # Build dependency graph
        self.dep_analyzer.build_dependency_graph(file_analyses)

        # Find entry points based on task keywords
        keywords = self._extract_keywords(task_description.lower())
        suggestions = []

        # 1. Look for files/symbols matching keywords
        for file_path, analysis in file_analyses.items():
            score = 0
            reasons = []

            # Check file name
            file_name_lower = file_path.lower()
            for keyword in keywords:
                if keyword in file_name_lower:
                    score += 10
                    reasons.append(f"File name contains '{keyword}'")

            # Check symbols (functions, classes)
            for symbol in analysis.symbols:
                symbol_name_lower = symbol.name.lower()
                for keyword in keywords:
                    if keyword in symbol_name_lower:
                        score += 5
                        reasons.append(f"Contains symbol '{symbol.name}'")

            if score > 0:
                # Get additional context
                module_info = self.dep_analyzer.modules.get(file_path)
                if module_info:
                    importance = self.dep_analyzer.get_module_importance_score(file_path)
                    score += importance * 0.1

                    reasons.append(
                        f"Importance score: {importance:.1f}, "
                        f"Dependencies: {module_info.dependency_count}, "
                        f"Dependents: {module_info.dependent_count}"
                    )

                suggestions.append(
                    {"file": file_path, "score": score, "reasons": reasons}
                )

        # Sort by score
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        # Format output
        if not suggestions:
            # Fallback: suggest entry points and core modules
            entry_points = self.dep_analyzer.identify_entry_points()
            core_modules = self.dep_analyzer.identify_core_modules(5)

            result = "No direct matches found. Here are some general suggestions:\n\n"
            result += "**Entry Points:**\n"
            for ep in entry_points[:5]:
                result += f"  - {ep.path}\n"

            result += "\n**Core Modules:**\n"
            for cm in core_modules:
                result += f"  - {cm.path} (used by {cm.dependent_count} modules)\n"

            return result

        # Return top 5 suggestions
        result = f"**Entry points for: '{task_description}'**\n\n"
        for i, suggestion in enumerate(suggestions[:5], 1):
            result += f"{i}. **{suggestion['file']}**\n"
            for reason in suggestion["reasons"][:3]:  # Top 3 reasons
                result += f"   - {reason}\n"
            result += "\n"

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from task description.

        Args:
            text: Task description text

        Returns:
            List of keywords
        """
        # Remove common words
        stop_words = {
            "a",
            "an",
            "the",
            "to",
            "for",
            "in",
            "on",
            "at",
            "add",
            "create",
            "update",
            "fix",
            "implement",
            "new",
            "and",
            "or",
            "is",
            "are",
            "was",
            "were",
        }

        words = text.split()
        keywords = [w.strip(",.!?") for w in words if w not in stop_words and len(w) > 2]

        return keywords

    async def _arun(self, task_description: str) -> str:
        """Async version of _run."""
        return self._run(task_description)
