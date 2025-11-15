"""Main CLI entry point for OnboardingAgent."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from onboarding_agent.agents import OnboardingAgent
from onboarding_agent.orchestrator import get_llm, load_config

console = Console()


@click.group()
def cli() -> None:
    """OnboardingAgent - Your AI mentor for navigating codebases."""
    pass


@cli.command()
@click.option(
    "--repo-path",
    "-r",
    type=click.Path(exists=True),
    help="Path to the repository to analyze",
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
    help="Model name (e.g., llama-3.1-70b-versatile, gpt-4-turbo-preview)",
)
def chat(
    repo_path: Optional[str],
    llm_provider: Optional[str],
    model: Optional[str],
) -> None:
    """Start an interactive chat session with the OnboardingAgent."""
    # Load configuration
    config = load_config()

    # Override with CLI arguments
    if repo_path:
        config["repo_path"] = repo_path
    if llm_provider:
        config["llm_provider"] = llm_provider
    if model:
        config["llm_model"] = model

    # Validate repository path
    repo_path_obj = Path(config["repo_path"])
    if not repo_path_obj.exists():
        console.print(
            f"[red]Error: Repository path does not exist: {config['repo_path']}[/red]"
        )
        sys.exit(1)

    # Display welcome message
    console.print()
    console.print(
        Panel.fit(
            "[bold blue]OnboardingAgent - The Mentor[/bold blue]\n\n"
            "I'll help you navigate this codebase!\n\n"
            f"Repository: [cyan]{repo_path_obj.absolute()}[/cyan]\n"
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
    console.print("[yellow]Initializing OnboardingAgent...[/yellow]")
    agent = OnboardingAgent(repo_path=str(repo_path_obj), llm=llm)

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
            console.print("\n[bold blue]OnboardingAgent[/bold blue] (thinking...)")

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


@cli.command()
@click.option(
    "--repo-path",
    "-r",
    type=click.Path(exists=True),
    help="Path to the repository to analyze",
)
def analyze(repo_path: Optional[str]) -> None:
    """Perform a quick analysis of the codebase."""
    # Load configuration
    config = load_config()

    # Override with CLI argument
    if repo_path:
        config["repo_path"] = repo_path

    # Validate repository path
    repo_path_obj = Path(config["repo_path"])
    if not repo_path_obj.exists():
        console.print(
            f"[red]Error: Repository path does not exist: {config['repo_path']}[/red]"
        )
        sys.exit(1)

    console.print(
        Panel.fit(
            "[bold blue]Quick Codebase Analysis[/bold blue]\n\n"
            f"Repository: [cyan]{repo_path_obj.absolute()}[/cyan]",
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
    agent = OnboardingAgent(repo_path=str(repo_path_obj), llm=llm)

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


@cli.command()
def version() -> None:
    """Show version information."""
    from onboarding_agent import __version__

    console.print(f"OnboardingAgent version: [cyan]{__version__}[/cyan]")


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
