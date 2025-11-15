"""Dependency and module relationship analysis."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set
import networkx as nx


@dataclass
class ModuleInfo:
    """Information about a module/file."""

    path: str
    imports: List[str]
    exported_symbols: List[str]
    is_entry_point: bool = False
    dependency_count: int = 0
    dependent_count: int = 0


@dataclass
class DependencyCluster:
    """A cluster of related modules."""

    name: str
    modules: List[str]
    internal_dependencies: int
    external_dependencies: List[str]


class DependencyAnalyzer:
    """Analyzes module dependencies and relationships."""

    def __init__(self, repo_path: str) -> None:
        """Initialize dependency analyzer.

        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        self.dependency_graph = nx.DiGraph()
        self.modules: Dict[str, ModuleInfo] = {}

    def build_dependency_graph(self, file_analyses: Dict[str, any]) -> None:
        """Build dependency graph from file analyses.

        Args:
            file_analyses: Dictionary of file paths to analysis results
        """
        # First pass: Create nodes
        for file_path, analysis in file_analyses.items():
            self.modules[file_path] = ModuleInfo(
                path=file_path,
                imports=analysis.imports if hasattr(analysis, "imports") else [],
                exported_symbols=[s.name for s in analysis.symbols]
                if hasattr(analysis, "symbols")
                else [],
            )
            self.dependency_graph.add_node(file_path)

        # Second pass: Create edges
        for file_path, module_info in self.modules.items():
            for import_path in module_info.imports:
                # Try to resolve import to actual file
                resolved = self._resolve_import(import_path, file_analyses.keys())
                if resolved and resolved in self.modules:
                    self.dependency_graph.add_edge(file_path, resolved)

        # Calculate dependency counts
        for file_path in self.modules.keys():
            self.modules[file_path].dependency_count = self.dependency_graph.out_degree(
                file_path
            )
            self.modules[file_path].dependent_count = self.dependency_graph.in_degree(
                file_path
            )

    def _resolve_import(self, import_path: str, available_files: Set[str]) -> str:
        """Resolve an import statement to an actual file path.

        Args:
            import_path: Import string (e.g., 'src.utils.helpers')
            available_files: Set of available file paths

        Returns:
            Resolved file path or empty string
        """
        # Convert import to potential file paths
        potential_paths = []

        # Python style: src.utils.helpers -> src/utils/helpers.py
        python_path = import_path.replace(".", "/") + ".py"
        potential_paths.append(python_path)

        # JavaScript style: ./utils/helpers -> utils/helpers.js
        if import_path.startswith("./") or import_path.startswith("../"):
            js_path = import_path.lstrip("./") + ".js"
            ts_path = import_path.lstrip("./") + ".ts"
            potential_paths.extend([js_path, ts_path])

        # Check if any potential path exists
        for path in potential_paths:
            if path in available_files:
                return path

        return ""

    def identify_core_modules(self, top_n: int = 10) -> List[ModuleInfo]:
        """Identify core modules based on dependency metrics.

        Core modules are those that many other modules depend on.

        Args:
            top_n: Number of top modules to return

        Returns:
            List of core ModuleInfo objects
        """
        # Sort by dependent_count (how many modules depend on this one)
        core_modules = sorted(
            self.modules.values(), key=lambda m: m.dependent_count, reverse=True
        )
        return core_modules[:top_n]

    def identify_leaf_modules(self) -> List[ModuleInfo]:
        """Identify leaf modules (no other modules depend on them).

        Returns:
            List of leaf ModuleInfo objects
        """
        return [m for m in self.modules.values() if m.dependent_count == 0]

    def identify_entry_points(self) -> List[ModuleInfo]:
        """Identify potential entry points (modules with few dependencies).

        Returns:
            List of potential entry point ModuleInfo objects
        """
        # Entry points typically have few dependencies but may have dependents
        entry_points = [
            m
            for m in self.modules.values()
            if m.dependency_count <= 3 and m.dependent_count >= 0
        ]

        # Also look for common entry point file names
        common_names = ["main", "app", "index", "server", "run", "cli"]
        for module in self.modules.values():
            file_name = Path(module.path).stem
            if file_name in common_names:
                module.is_entry_point = True
                if module not in entry_points:
                    entry_points.append(module)

        return entry_points

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the codebase.

        Returns:
            List of cycles, where each cycle is a list of file paths
        """
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except Exception:
            return []

    def identify_clusters(self) -> List[DependencyCluster]:
        """Identify clusters of related modules.

        Returns:
            List of DependencyCluster objects
        """
        if len(self.dependency_graph.nodes) == 0:
            return []

        # Convert to undirected for community detection
        undirected = self.dependency_graph.to_undirected()

        # Use simple approach: group by directory
        clusters: Dict[str, List[str]] = {}

        for file_path in self.modules.keys():
            # Get directory name
            directory = str(Path(file_path).parent)
            if directory == ".":
                directory = "root"

            if directory not in clusters:
                clusters[directory] = []
            clusters[directory].append(file_path)

        # Build cluster objects
        cluster_objects = []
        for dir_name, module_paths in clusters.items():
            if len(module_paths) < 2:  # Skip single-file clusters
                continue

            # Count internal dependencies
            internal_deps = 0
            external_deps: Set[str] = set()

            for module_path in module_paths:
                for neighbor in self.dependency_graph.neighbors(module_path):
                    if neighbor in module_paths:
                        internal_deps += 1
                    else:
                        external_deps.add(neighbor)

            cluster_objects.append(
                DependencyCluster(
                    name=dir_name,
                    modules=module_paths,
                    internal_dependencies=internal_deps,
                    external_dependencies=list(external_deps),
                )
            )

        return cluster_objects

    def get_dependency_depth(self, file_path: str) -> int:
        """Calculate dependency depth for a file.

        Args:
            file_path: Path to the file

        Returns:
            Maximum depth of dependency chain
        """
        if file_path not in self.dependency_graph:
            return 0

        try:
            # Find longest path from this node
            depths = []
            for node in self.dependency_graph.nodes():
                if nx.has_path(self.dependency_graph, file_path, node):
                    path = nx.shortest_path(self.dependency_graph, file_path, node)
                    depths.append(len(path) - 1)

            return max(depths) if depths else 0
        except Exception:
            return 0

    def get_module_importance_score(self, file_path: str) -> float:
        """Calculate importance score for a module.

        Score is based on:
        - Number of dependents (modules that import this one)
        - Centrality in the dependency graph

        Args:
            file_path: Path to the file

        Returns:
            Importance score (0-100)
        """
        if file_path not in self.dependency_graph:
            return 0.0

        # Get betweenness centrality (how often this node is on shortest paths)
        try:
            centrality = nx.betweenness_centrality(self.dependency_graph)
            centrality_score = centrality.get(file_path, 0) * 50

            # Get dependent count score
            dependent_score = min(self.modules[file_path].dependent_count * 5, 50)

            return min(centrality_score + dependent_score, 100)
        except Exception:
            return float(self.modules[file_path].dependent_count * 10)

    def generate_dependency_report(self) -> Dict[str, any]:
        """Generate a comprehensive dependency report.

        Returns:
            Dictionary with dependency statistics
        """
        core_modules = self.identify_core_modules(10)
        entry_points = self.identify_entry_points()
        leaf_modules = self.identify_leaf_modules()
        circular_deps = self.detect_circular_dependencies()
        clusters = self.identify_clusters()

        return {
            "total_modules": len(self.modules),
            "core_modules": [m.path for m in core_modules],
            "entry_points": [m.path for m in entry_points],
            "leaf_modules_count": len(leaf_modules),
            "circular_dependencies": len(circular_deps),
            "circular_dependency_chains": circular_deps[:5],  # First 5
            "clusters": [
                {"name": c.name, "module_count": len(c.modules)} for c in clusters
            ],
        }
