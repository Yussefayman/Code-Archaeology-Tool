"""Tool for identifying core modules in the codebase."""

from typing import Dict, List, Any
from langchain.tools import BaseTool
from pydantic import Field

from onboarding_agent.analyzers import (
    ASTAnalyzer,
    DependencyAnalyzer,
    GitAnalyzer,
)


class CoreModulesTool(BaseTool):
    """Tool to identify the most important/core modules in the codebase."""

    name: str = "identify_core_modules"
    description: str = """
    Identifies the core modules that are most important to understand.

    Core modules are those that:
    - Many other modules depend on
    - Are frequently modified
    - Are central to the codebase architecture

    No input required. Returns a ranked list of core modules with explanations.
    """

    repo_path: str = Field(description="Path to the repository")
    ast_analyzer: Any = Field(default=None, exclude=True)
    dep_analyzer: Any = Field(default=None, exclude=True)
    git_analyzer: Any = Field(default=None, exclude=True)

    def __init__(self, repo_path: str, **kwargs: Any):
        """Initialize the core modules tool.

        Args:
            repo_path: Path to the repository
            **kwargs: Additional arguments
        """
        super().__init__(repo_path=repo_path, **kwargs)

        # Initialize analyzers
        self.ast_analyzer = ASTAnalyzer(repo_path)
        self.dep_analyzer = DependencyAnalyzer(repo_path)
        try:
            self.git_analyzer = GitAnalyzer(repo_path)
        except ValueError:
            self.git_analyzer = None  # Not a git repo

    def _run(self, query: str = "") -> str:
        """Identify core modules.

        Args:
            query: Optional query (not used, for compatibility)

        Returns:
            Formatted list of core modules
        """
        # Analyze repository
        file_analyses = self.ast_analyzer.analyze_repository()
        self.dep_analyzer.build_dependency_graph(file_analyses)

        # Get core modules by dependency count
        core_modules = self.dep_analyzer.identify_core_modules(15)

        # Get git hotspots if available
        hotspots = []
        if self.git_analyzer:
            try:
                hotspots = self.git_analyzer.get_hotspots(20)
            except Exception:
                pass

        # Create hotspot lookup
        hotspot_lookup = {h.file_path: h for h in hotspots}

        # Enrich core modules with git data and calculate overall importance
        enriched_modules = []
        for module in core_modules:
            importance_score = self.dep_analyzer.get_module_importance_score(module.path)
            churn_score = 0
            author_count = 0

            if module.path in hotspot_lookup:
                hotspot = hotspot_lookup[module.path]
                churn_score = hotspot.churn_score
                author_count = len(hotspot.authors)

            # Calculate overall core score
            # Weight: importance (40%), dependents (30%), churn (20%), authors (10%)
            core_score = (
                importance_score * 0.4
                + module.dependent_count * 3 * 0.3
                + min(churn_score * 2, 50) * 0.2
                + min(author_count * 5, 50) * 0.1
            )

            enriched_modules.append(
                {
                    "path": module.path,
                    "dependent_count": module.dependent_count,
                    "importance": importance_score,
                    "churn": churn_score,
                    "authors": author_count,
                    "core_score": core_score,
                }
            )

        # Sort by core score
        enriched_modules.sort(key=lambda x: x["core_score"], reverse=True)

        # Get additional insights
        entry_points = self.dep_analyzer.identify_entry_points()
        clusters = self.dep_analyzer.identify_clusters()

        # Format output
        result = "**Core Modules Analysis**\n\n"
        result += "These are the most important modules to understand:\n\n"

        for i, module in enumerate(enriched_modules[:10], 1):
            result += f"{i}. **{module['path']}**\n"
            result += f"   - Core Score: {module['core_score']:.1f}/100\n"
            result += f"   - Used by {module['dependent_count']} other modules\n"
            result += f"   - Importance: {module['importance']:.1f}/100\n"

            if module["churn"] > 0:
                result += f"   - Modified {module['churn']} times\n"
            if module["authors"] > 0:
                result += f"   - Worked on by {module['authors']} developers\n"

            # Add interpretation
            if module["core_score"] > 70:
                result += "   - 🌟 **Critical**: Essential for understanding the codebase\n"
            elif module["core_score"] > 50:
                result += "   - ⭐ **Important**: Key module with significant dependencies\n"

            result += "\n"

        # Add entry points section
        if entry_points:
            result += "\n**Entry Points** (good starting points):\n"
            for ep in entry_points[:5]:
                result += f"  - {ep.path}\n"

        # Add clusters section
        if clusters:
            result += "\n**Module Clusters** (related modules):\n"
            for cluster in clusters[:5]:
                result += f"  - **{cluster.name}**: {len(cluster.modules)} modules\n"

        # Add summary
        result += f"\n**Summary:**\n"
        result += f"- Total modules analyzed: {len(file_analyses)}\n"
        result += f"- Core modules identified: {len(enriched_modules)}\n"
        result += f"- Entry points found: {len(entry_points)}\n"
        result += f"- Module clusters: {len(clusters)}\n"

        return result

    async def _arun(self, query: str = "") -> str:
        """Async version of _run."""
        return self._run(query)
