"""Main CLI entry point for Code Archaeology Tool."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from code_archaeology.agents import CodeArchaeologyAgent
from code_archaeology.orchestrator import get_llm, load_config
from code_archaeology.utils import clone_repository, is_github_url, get_repo_info

console = Console()


def resolve_repository(repo_input: str) -> Tuple[str, bool]:
    """Resolve repository input to a local path.

    Args:
        repo_input: Either a local path or GitHub URL

    Returns:
        Tuple of (resolved_path, is_temporary)
            - resolved_path: Local path to the repository
            - is_temporary: Whether to clean up the path later

    Raises:
        ValueError: If repository cannot be resolved
    """
    # Check if it's a GitHub URL
    if is_github_url(repo_input):
        console.print(f"[yellow]Detected GitHub URL, cloning repository...[/yellow]")

        # Get GitHub token from environment if available
        token = os.getenv("GITHUB_TOKEN")

        try:
            repo_info = get_repo_info(repo_input)
            console.print(
                f"[cyan]Cloning {repo_info['owner']}/{repo_info['name']}...[/cyan]"
            )

            clone_path, is_temp = clone_repository(repo_input, token=token)

            console.print(f"[green]✓ Repository cloned to {clone_path}[/green]\n")
            return clone_path, is_temp

        except Exception as e:
            console.print(f"[red]Error cloning repository: {e}[/red]")
            sys.exit(1)
    else:
        # Local path
        repo_path_obj = Path(repo_input)
        if not repo_path_obj.exists():
            console.print(
                f"[red]Error: Repository path does not exist: {repo_input}[/red]"
            )
            sys.exit(1)

        return str(repo_path_obj), False


@click.group()
def cli() -> None:
    """Code Archaeology Tool - Your AI mentor for navigating codebases."""
    pass


@cli.command()
@click.option(
    "--repo-path",
    "-r",
    type=str,
    help="Path to repository or GitHub URL (e.g., https://github.com/user/repo)",
)
@click.option(
    "--llm-provider",
    "-p",
    type=click.Choice(["groq", "openai", "anthropic"], case_sensitive=False),
    help="LLM provider to use",
)
@click.option(
    "--model",
    "-m",
    help="Model name (e.g., llama-3.3-70b-versatile, gpt-4-turbo-preview)",
)
def chat(
    repo_path: Optional[str],
    llm_provider: Optional[str],
    model: Optional[str],
) -> None:
    """Start an interactive chat session with the Code Archaeology Tool."""
    # Load configuration
    config = load_config()

    # Override with CLI arguments
    if repo_path:
        config["repo_path"] = repo_path
    if llm_provider:
        config["llm_provider"] = llm_provider
    if model:
        config["llm_model"] = model

    # Resolve repository (local path or GitHub URL)
    resolved_repo_path, is_temporary = resolve_repository(config["repo_path"])

    try:
        # Display welcome message
        console.print()
        console.print(
            Panel.fit(
                "[bold blue]Code Archaeology Tool - The Mentor[/bold blue]\n\n"
                "I'll help you navigate this codebase!\n\n"
                f"Repository: [cyan]{resolved_repo_path}[/cyan]\n"
                f"LLM: [cyan]{config['llm_provider']} ({config['llm_model']})[/cyan]",
                border_style="blue",
            )
        )
        console.print()

        # Initialize LLM
        try:
            console.print("[yellow]Initializing LLM...[/yellow]")
            llm = get_llm(config)
        except Exception as e:
            console.print(f"[red]Error initializing LLM: {e}[/red]")
            console.print(
                "\n[yellow]Tip: Make sure you have set up your API key in .env file[/yellow]"
            )
            sys.exit(1)

        # Initialize agent
        console.print("[yellow]Initializing Code Archaeology Tool...[/yellow]")
        agent = CodeArchaeologyAgent(repo_path=resolved_repo_path, llm=llm)

        console.print("[green]✓ Ready to chat![/green]\n")

        # Show helpful commands
        console.print("[dim]Try asking:[/dim]")
        console.print("[dim]  - Where should I start to add a new feature?[/dim]")
        console.print("[dim]  - Show me the core modules[/dim]")
        console.print("[dim]  - Create a learning path for authentication[/dim]")
        console.print("[dim]  - What's the complexity map?[/dim]")
        console.print("[dim]\nType 'quit' or 'exit' to end the session[/dim]\n")

        # Chat loop
        chat_history = []

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "bye"]:
                    console.print("\n[yellow]Goodbye! Happy coding! 👋[/yellow]\n")
                    break

                # Send to agent
                console.print("\n[bold blue]Code Archaeology Tool[/bold blue] (thinking...)")

                response = agent.chat(user_input, chat_history)

                # Display response
                console.print()
                if response["success"]:
                    md = Markdown(response["output"])
                    console.print(md)

                    # Add to chat history
                    chat_history.append((user_input, response["output"]))

                    # Limit history to last 5 exchanges
                    if len(chat_history) > 5:
                        chat_history = chat_history[-5:]
                else:
                    console.print(f"[red]Error: {response['error']}[/red]")

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Goodbye! 👋[/yellow]\n")
                break
            except Exception as e:
                console.print(f"\n[red]Unexpected error: {e}[/red]")

    finally:
        # Clean up temporary directory if needed
        if is_temporary and resolved_repo_path:
            console.print(f"[dim]Cleaning up temporary files...[/dim]")
            try:
                # Remove the parent temp directory
                temp_dir = str(Path(resolved_repo_path).parent)
                shutil.rmtree(temp_dir)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not clean up temp files: {e}[/yellow]")


@cli.command()
@click.option(
    "--repo-path",
    "-r",
    type=str,
    help="Path to repository or GitHub URL (e.g., https://github.com/user/repo)",
)
def analyze(repo_path: Optional[str]) -> None:
    """Perform a quick analysis of the codebase."""
    # Load configuration
    config = load_config()

    # Override with CLI argument
    if repo_path:
        config["repo_path"] = repo_path

    # Resolve repository (local path or GitHub URL)
    resolved_repo_path, is_temporary = resolve_repository(config["repo_path"])

    try:
        console.print(
            Panel.fit(
                "[bold blue]Quick Codebase Analysis[/bold blue]\n\n"
                f"Repository: [cyan]{resolved_repo_path}[/cyan]",
                border_style="blue",
            )
        )
        console.print()

        # Initialize LLM (needed for agent, but not used in quick analysis)
        try:
            llm = get_llm(config)
        except Exception as e:
            console.print(f"[red]Error initializing LLM: {e}[/red]")
            console.print(
                "\n[yellow]Tip: Make sure you have set up your API key in .env file[/yellow]"
            )
            sys.exit(1)

        # Initialize agent
        console.print("[yellow]Analyzing repository...[/yellow]\n")
        agent = CodeArchaeologyAgent(repo_path=resolved_repo_path, llm=llm)

        # Perform quick analysis
        results = agent.quick_analysis()

        # Display results
        console.print()
        md_core = Markdown(results["core_modules"])
        console.print(md_core)

        console.print("\n" + "=" * 80 + "\n")

        md_complexity = Markdown(results["complexity_map"])
        console.print(md_complexity)

        console.print()

    finally:
        # Clean up temporary directory if needed
        if is_temporary and resolved_repo_path:
            console.print(f"[dim]Cleaning up temporary files...[/dim]")
            try:
                # Remove the parent temp directory
                temp_dir = str(Path(resolved_repo_path).parent)
                shutil.rmtree(temp_dir)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not clean up temp files: {e}[/yellow]")


@cli.command()
def version() -> None:
    """Show version information."""
    from code_archaeology import __version__

    console.print(f"Code Archaeology Tool version: [cyan]{__version__}[/cyan]")


@cli.command()
def config() -> None:
    """Show current configuration."""
    cfg = load_config()

    console.print(
        Panel.fit(
            f"[bold blue]Current Configuration[/bold blue]\n\n"
            f"LLM Provider: [cyan]{cfg['llm_provider']}[/cyan]\n"
            f"LLM Model: [cyan]{cfg['llm_model']}[/cyan]\n"
            f"Temperature: [cyan]{cfg['temperature']}[/cyan]\n"
            f"Max Tokens: [cyan]{cfg['max_tokens']}[/cyan]\n"
            f"Max Iterations: [cyan]{cfg['max_iterations']}[/cyan]\n"
            f"Repository Path: [cyan]{cfg['repo_path']}[/cyan]\n"
            f"Log Level: [cyan]{cfg['log_level']}[/cyan]",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    cli()
