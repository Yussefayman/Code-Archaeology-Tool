"""AST analysis using tree-sitter for multi-language support."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, etc.)."""

    name: str
    type: str  # function, class, method, variable
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    complexity: int = 0
    is_public: bool = True


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: str
    language: str
    symbols: List[CodeSymbol]
    imports: List[str]
    total_lines: int
    code_lines: int


class ASTAnalyzer:
    """Analyzes code structure using AST parsing."""

    # Supported file extensions
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

    def __init__(self, repo_path: str) -> None:
        """Initialize analyzer with repository path.

        Args:
            repo_path: Path to the repository to analyze
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def analyze_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze a single file and extract symbols.

        Args:
            file_path: Path to the file to analyze

        Returns:
            FileAnalysis object or None if file cannot be analyzed
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return None

        extension = file_path_obj.suffix
        language = self.LANGUAGE_MAP.get(extension)

        if not language:
            return None

        try:
            with open(file_path_obj, "r", encoding="utf-8") as f:
                content = f.read()

            # For MVP, use simple pattern matching
            # In production, would use tree-sitter
            symbols = self._extract_symbols_simple(content, language, str(file_path_obj))
            imports = self._extract_imports_simple(content, language)

            lines = content.split("\n")
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

            return FileAnalysis(
                file_path=str(file_path_obj),
                language=language,
                symbols=symbols,
                imports=imports,
                total_lines=total_lines,
                code_lines=code_lines,
            )
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def _extract_symbols_simple(
        self, content: str, language: str, file_path: str
    ) -> List[CodeSymbol]:
        """Simple symbol extraction without tree-sitter (MVP version).

        Args:
            content: File content
            language: Programming language
            file_path: Path to the file

        Returns:
            List of CodeSymbol objects
        """
        symbols = []
        lines = content.split("\n")

        if language == "python":
            symbols.extend(self._extract_python_symbols(lines, file_path))
        elif language in ["javascript", "typescript"]:
            symbols.extend(self._extract_js_symbols(lines, file_path))

        return symbols

    def _extract_python_symbols(self, lines: List[str], file_path: str) -> List[CodeSymbol]:
        """Extract Python functions and classes.

        Args:
            lines: File content as list of lines
            file_path: Path to the file

        Returns:
            List of CodeSymbol objects
        """
        symbols = []
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Extract classes
            if stripped.startswith("class "):
                name = stripped.split("(")[0].replace("class ", "").replace(":", "").strip()
                is_public = not name.startswith("_")
                symbols.append(
                    CodeSymbol(
                        name=name,
                        type="class",
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        is_public=is_public,
                    )
                )

            # Extract functions/methods
            elif stripped.startswith("def "):
                name = stripped.split("(")[0].replace("def ", "").strip()
                is_public = not name.startswith("_")
                symbol_type = "function"

                # Check if it's a method (indented)
                if line.startswith("    ") or line.startswith("\t"):
                    symbol_type = "method"

                symbols.append(
                    CodeSymbol(
                        name=name,
                        type=symbol_type,
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        is_public=is_public,
                    )
                )

        return symbols

    def _extract_js_symbols(self, lines: List[str], file_path: str) -> List[CodeSymbol]:
        """Extract JavaScript/TypeScript functions and classes.

        Args:
            lines: File content as list of lines
            file_path: Path to the file

        Returns:
            List of CodeSymbol objects
        """
        symbols = []
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Extract classes
            if stripped.startswith("class "):
                name = stripped.split("{")[0].replace("class ", "").replace("extends", "").strip()
                symbols.append(
                    CodeSymbol(
                        name=name,
                        type="class",
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        is_public=True,
                    )
                )

            # Extract functions
            elif "function " in stripped:
                try:
                    name = stripped.split("function ")[1].split("(")[0].strip()
                    if name:
                        symbols.append(
                            CodeSymbol(
                                name=name,
                                type="function",
                                file_path=file_path,
                                line_start=i + 1,
                                line_end=i + 1,
                                is_public=True,
                            )
                        )
                except IndexError:
                    pass

            # Extract arrow functions assigned to const/let
            elif "const " in stripped or "let " in stripped:
                if "=>" in stripped:
                    try:
                        name = stripped.split("const ")[1].split("=")[0].strip() if "const " in stripped else stripped.split("let ")[1].split("=")[0].strip()
                        symbols.append(
                            CodeSymbol(
                                name=name,
                                type="function",
                                file_path=file_path,
                                line_start=i + 1,
                                line_end=i + 1,
                                is_public=True,
                            )
                        )
                    except IndexError:
                        pass

        return symbols

    def _extract_imports_simple(self, content: str, language: str) -> List[str]:
        """Extract import statements.

        Args:
            content: File content
            language: Programming language

        Returns:
            List of imported modules
        """
        imports = []
        lines = content.split("\n")

        if language == "python":
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("import "):
                    module = stripped.replace("import ", "").split(" as ")[0].split(",")[0].strip()
                    imports.append(module)
                elif stripped.startswith("from "):
                    try:
                        module = stripped.split("from ")[1].split(" import")[0].strip()
                        imports.append(module)
                    except IndexError:
                        pass

        elif language in ["javascript", "typescript"]:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("import "):
                    try:
                        # Extract module from 'from "module"'
                        if "from " in stripped:
                            module = stripped.split("from ")[1].strip().strip(";\"'")
                            imports.append(module)
                    except IndexError:
                        pass

        return imports

    def analyze_repository(self, include_patterns: Optional[List[str]] = None) -> Dict[str, FileAnalysis]:
        """Analyze all supported files in the repository.

        Args:
            include_patterns: List of glob patterns to include (e.g., ['*.py', '*.js'])

        Returns:
            Dictionary mapping file paths to FileAnalysis objects
        """
        results = {}

        # Find all supported files
        for ext in self.LANGUAGE_MAP.keys():
            pattern = f"**/*{ext}"
            for file_path in self.repo_path.rglob(pattern.replace("**/", "")):
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
                    ]
                ):
                    continue

                analysis = self.analyze_file(str(file_path))
                if analysis:
                    rel_path = str(file_path.relative_to(self.repo_path))
                    results[rel_path] = analysis

        return results

    def get_all_symbols(self) -> List[CodeSymbol]:
        """Get all symbols from the repository.

        Returns:
            List of all CodeSymbol objects
        """
        analyses = self.analyze_repository()
        symbols = []
        for analysis in analyses.values():
            symbols.extend(analysis.symbols)
        return symbols

    def find_entry_points(self) -> List[str]:
        """Find likely entry points in the codebase.

        Returns:
            List of file paths that are likely entry points
        """
        entry_points = []
        common_entry_files = [
            "main.py",
            "app.py",
            "index.py",
            "__main__.py",
            "run.py",
            "server.py",
            "index.js",
            "main.js",
            "app.js",
            "server.js",
            "index.ts",
            "main.ts",
        ]

        for file_name in common_entry_files:
            for file_path in self.repo_path.rglob(file_name):
                if not any(
                    part in file_path.parts
                    for part in ["node_modules", ".git", "test", "tests", "__pycache__"]
                ):
                    entry_points.append(str(file_path.relative_to(self.repo_path)))

        return entry_points
