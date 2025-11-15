"""Git repository analysis for understanding code evolution."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


@dataclass
class FileHistory:
    """Git history information for a file."""

    file_path: str
    commit_count: int
    authors: List[str]
    last_modified: datetime
    creation_date: datetime
    churn_score: int  # Number of times modified


@dataclass
class ContributorStats:
    """Statistics about a contributor."""

    name: str
    email: str
    commit_count: int
    files_touched: int
    lines_added: int
    lines_deleted: int


class GitAnalyzer:
    """Analyzes git history for insights."""

    def __init__(self, repo_path: str) -> None:
        """Initialize git analyzer.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Check if it's a git repository
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output.

        Args:
            args: List of git command arguments

        Returns:
            Command output as string
        """
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path)] + args,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return ""

    def get_file_history(self, file_path: str) -> Optional[FileHistory]:
        """Get git history for a specific file.

        Args:
            file_path: Relative path to the file

        Returns:
            FileHistory object or None if file has no history
        """
        # Get commit count
        commit_count_output = self._run_git_command(
            ["rev-list", "--count", "HEAD", "--", file_path]
        )
        if not commit_count_output:
            return None

        commit_count = int(commit_count_output)

        # Get authors
        authors_output = self._run_git_command(
            ["log", "--format=%an", "--", file_path]
        )
        authors = list(set(authors_output.split("\n"))) if authors_output else []

        # Get last modified date
        last_modified_output = self._run_git_command(
            ["log", "-1", "--format=%ct", "--", file_path]
        )
        last_modified = (
            datetime.fromtimestamp(int(last_modified_output))
            if last_modified_output
            else datetime.now()
        )

        # Get creation date (first commit)
        creation_output = self._run_git_command(
            ["log", "--diff-filter=A", "--format=%ct", "--", file_path]
        )
        creation_lines = creation_output.split("\n") if creation_output else []
        creation_date = (
            datetime.fromtimestamp(int(creation_lines[-1]))
            if creation_lines
            else last_modified
        )

        return FileHistory(
            file_path=file_path,
            commit_count=commit_count,
            authors=authors,
            last_modified=last_modified,
            creation_date=creation_date,
            churn_score=commit_count,
        )

    def get_hotspots(self, limit: int = 10) -> List[FileHistory]:
        """Identify files with high churn (frequently modified).

        Args:
            limit: Maximum number of hotspots to return

        Returns:
            List of FileHistory objects sorted by churn score
        """
        # Get all files tracked by git
        files_output = self._run_git_command(["ls-files"])
        if not files_output:
            return []

        files = files_output.split("\n")
        file_histories = []

        for file_path in files:
            history = self.get_file_history(file_path)
            if history:
                file_histories.append(history)

        # Sort by churn score
        file_histories.sort(key=lambda x: x.churn_score, reverse=True)
        return file_histories[:limit]

    def get_contributor_stats(self) -> List[ContributorStats]:
        """Get statistics about all contributors.

        Returns:
            List of ContributorStats objects
        """
        # Get all authors
        authors_output = self._run_git_command(["shortlog", "-sne", "HEAD"])
        if not authors_output:
            return []

        contributors = []
        for line in authors_output.split("\n"):
            if not line.strip():
                continue

            # Parse line: "    5  John Doe <john@example.com>"
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue

            commit_count = int(parts[0])
            author_info = parts[1]

            # Extract name and email
            if "<" in author_info and ">" in author_info:
                name = author_info.split("<")[0].strip()
                email = author_info.split("<")[1].split(">")[0].strip()
            else:
                name = author_info
                email = ""

            # Get files touched by this author
            files_output = self._run_git_command(
                ["log", f"--author={email}", "--name-only", "--format="]
            )
            files_touched = len(set(files_output.split("\n"))) if files_output else 0

            # Get line statistics
            stats_output = self._run_git_command(
                ["log", f"--author={email}", "--numstat", "--format="]
            )
            lines_added = 0
            lines_deleted = 0

            if stats_output:
                for stat_line in stats_output.split("\n"):
                    if not stat_line.strip():
                        continue
                    parts = stat_line.split("\t")
                    if len(parts) >= 2:
                        try:
                            lines_added += int(parts[0]) if parts[0] != "-" else 0
                            lines_deleted += int(parts[1]) if parts[1] != "-" else 0
                        except ValueError:
                            pass

            contributors.append(
                ContributorStats(
                    name=name,
                    email=email,
                    commit_count=commit_count,
                    files_touched=files_touched,
                    lines_added=lines_added,
                    lines_deleted=lines_deleted,
                )
            )

        return contributors

    def get_recent_activity(self, days: int = 30) -> Dict[str, int]:
        """Get files modified in the last N days.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping file paths to number of commits
        """
        output = self._run_git_command(
            ["log", f"--since={days}.days.ago", "--name-only", "--format="]
        )

        if not output:
            return {}

        files = output.split("\n")
        file_counts: Dict[str, int] = {}

        for file_path in files:
            if file_path.strip():
                file_counts[file_path] = file_counts.get(file_path, 0) + 1

        return file_counts

    def is_actively_maintained(self) -> bool:
        """Check if repository is actively maintained.

        Returns:
            True if there are commits in the last 90 days
        """
        recent_commits = self._run_git_command(
            ["rev-list", "--count", "HEAD", "--since=90.days.ago"]
        )
        return int(recent_commits) > 0 if recent_commits else False

    def get_total_commits(self) -> int:
        """Get total number of commits.

        Returns:
            Total commit count
        """
        output = self._run_git_command(["rev-list", "--count", "HEAD"])
        return int(output) if output else 0

    def get_branch_count(self) -> int:
        """Get number of branches.

        Returns:
            Number of branches
        """
        output = self._run_git_command(["branch", "-a"])
        return len(output.split("\n")) if output else 0
