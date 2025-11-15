"""GitHub repository cloning utilities."""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse


def is_github_url(path: str) -> bool:
    """Check if a string is a GitHub URL.

    Args:
        path: Path or URL to check

    Returns:
        True if it's a GitHub URL, False otherwise

    Examples:
        >>> is_github_url("https://github.com/user/repo")
        True
        >>> is_github_url("git@github.com:user/repo.git")
        True
        >>> is_github_url("/local/path/to/repo")
        False
    """
    github_patterns = [
        r"^https?://github\.com/[\w-]+/[\w.-]+",
        r"^git@github\.com:[\w-]+/[\w.-]+\.git$",
        r"^github\.com/[\w-]+/[\w.-]+",
    ]

    return any(re.match(pattern, path) for pattern in github_patterns)


def normalize_github_url(url: str) -> str:
    """Normalize GitHub URL to HTTPS format.

    Args:
        url: GitHub URL in any format

    Returns:
        Normalized HTTPS URL

    Examples:
        >>> normalize_github_url("git@github.com:user/repo.git")
        'https://github.com/user/repo'
        >>> normalize_github_url("github.com/user/repo")
        'https://github.com/user/repo'
    """
    # Remove .git suffix
    url = url.rstrip("/").replace(".git", "")

    # Convert SSH to HTTPS
    if url.startswith("git@github.com:"):
        url = url.replace("git@github.com:", "https://github.com/")

    # Add https:// if missing
    if not url.startswith("http"):
        url = "https://" + url

    return url


def extract_repo_name(url: str) -> str:
    """Extract repository name from GitHub URL.

    Args:
        url: GitHub URL

    Returns:
        Repository name (e.g., "repo" from "user/repo")

    Examples:
        >>> extract_repo_name("https://github.com/user/my-repo")
        'my-repo'
    """
    normalized = normalize_github_url(url)
    parsed = urlparse(normalized)
    parts = parsed.path.strip("/").split("/")

    if len(parts) >= 2:
        return parts[1]

    return "repository"


def clone_repository(
    github_url: str,
    destination: Optional[str] = None,
    depth: int = 1,
    token: Optional[str] = None,
) -> Tuple[str, bool]:
    """Clone a GitHub repository.

    Args:
        github_url: GitHub repository URL
        destination: Optional destination path (creates temp dir if None)
        depth: Git clone depth (1 for shallow clone, None for full)
        token: Optional GitHub personal access token for private repos

    Returns:
        Tuple of (cloned_path, is_temporary)
            - cloned_path: Path to the cloned repository
            - is_temporary: Whether the path is temporary and should be cleaned up

    Raises:
        ValueError: If URL is invalid
        subprocess.CalledProcessError: If git clone fails

    Examples:
        >>> path, is_temp = clone_repository("https://github.com/user/repo")
        >>> # Use the repository
        >>> if is_temp:
        ...     shutil.rmtree(path)  # Clean up
    """
    if not is_github_url(github_url):
        raise ValueError(f"Invalid GitHub URL: {github_url}")

    # Normalize URL
    clone_url = normalize_github_url(github_url)

    # Add token if provided
    if token:
        # Insert token into URL: https://TOKEN@github.com/user/repo
        clone_url = clone_url.replace("https://", f"https://{token}@")

    # Determine destination
    is_temporary = destination is None
    if is_temporary:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="code-archaeology-")
        repo_name = extract_repo_name(github_url)
        clone_path = os.path.join(temp_dir, repo_name)
    else:
        clone_path = destination

    # Build git clone command
    cmd = ["git", "clone"]

    if depth:
        cmd.extend(["--depth", str(depth)])

    cmd.extend([clone_url, clone_path])

    # Clone the repository
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return clone_path, is_temporary
    except subprocess.CalledProcessError as e:
        # Clean up temp dir if clone failed
        if is_temporary and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        # Provide helpful error message
        error_msg = e.stderr or e.stdout or str(e)

        if "Authentication failed" in error_msg or "403" in error_msg:
            raise ValueError(
                f"Authentication failed. For private repos, provide a GitHub token:\n"
                f"  export GITHUB_TOKEN=your_token_here\n"
                f"Error: {error_msg}"
            ) from e
        elif "not found" in error_msg.lower():
            raise ValueError(
                f"Repository not found: {github_url}\n"
                f"Make sure the URL is correct and the repo is accessible.\n"
                f"Error: {error_msg}"
            ) from e
        else:
            raise ValueError(f"Failed to clone repository: {error_msg}") from e


def get_repo_info(github_url: str) -> dict:
    """Get basic information about a GitHub repository from URL.

    Args:
        github_url: GitHub repository URL

    Returns:
        Dictionary with repo info (owner, name, url)

    Examples:
        >>> info = get_repo_info("https://github.com/user/repo")
        >>> info['owner']
        'user'
        >>> info['name']
        'repo'
    """
    normalized = normalize_github_url(github_url)
    parsed = urlparse(normalized)
    parts = parsed.path.strip("/").split("/")

    if len(parts) >= 2:
        return {
            "owner": parts[0],
            "name": parts[1],
            "url": normalized,
            "ssh_url": f"git@github.com:{parts[0]}/{parts[1]}.git",
            "https_url": normalized,
        }

    return {
        "owner": "unknown",
        "name": extract_repo_name(github_url),
        "url": normalized,
    }
