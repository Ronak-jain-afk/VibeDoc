"""CLI entry point."""

import pathlib

import typer
from rich.console import Console

from vibedoc.config import VibeDocConfig
from vibedoc.llm import create_client
from vibedoc.log import get_logger

app = typer.Typer(invoke_without_command=True)
console = Console()
logger = get_logger(__name__)


SYSTEM_PROMPT = (
    "You are a senior software engineer analyzing source code. "
    "Be precise, technical, and concise. Explain what the code does "
    "and why, referencing specific lines when helpful."
)


def _test_connection(base_url: str) -> bool:
    """Test if LM Studio is reachable."""
    try:
        import httpx

        response = httpx.get(f"{base_url}/models", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


@app.callback()
def main():
    """VibeDoc - AI-powered repository documentation generator."""
    pass


@app.command()
def analyze(
    file: str = typer.Argument(..., help="Path to source file to analyze"),
    model: str = typer.Option("lmstudio", help="LLM provider: lmstudio, openai, claude"),
    base_url: str | None = typer.Option(None, help="API base URL override"),
    api_key: str | None = typer.Option(None, help="API key override"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Analyze a source file and explain its contents."""
    config = VibeDocConfig()
    if base_url:
        config.lmstudio_base_url = base_url
    if api_key:
        config.lmstudio_api_key = api_key

    if verbose:
        console.print(f"[dim]Model: {config.lmstudio_model}[/dim]")

    candidates = [config.lmstudio_base_url]
    if "127.0.0.1" in config.lmstudio_base_url or "localhost" in config.lmstudio_base_url:
        candidates.append(config.lmstudio_base_url.replace("127.0.0.1", "172.22.144.1").replace("localhost", "172.22.144.1"))

    working_url = None
    for url in candidates:
        if _test_connection(url):
            working_url = url
            break

    if not working_url:
        console.print("[yellow]Warning: Cannot connect to LM Studio.[/yellow]")
        console.print(f"[dim]Checked: {', '.join(candidates)}[/dim]")
        console.print("[dim]Make sure LM Studio is running with 'Enable API' checked.[/dim]")
        console.print("[dim]Ensure Windows Firewall allows connections on port 1234.[/dim]")
        raise typer.Exit(1)

    if working_url != config.lmstudio_base_url:
        config.lmstudio_base_url = working_url
        console.print(f"[green]Connected to LM Studio at: {working_url}[/green]")

    try:
        client = create_client(model, config)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    file_path = pathlib.Path(file)
    if not file_path.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(1)

    source_code = file_path.read_text(encoding="utf-8")

    user_prompt = f"""Analyze this source code file:

```python
{source_code}
```

Provide a comprehensive explanation covering:
1. What the file does overall
2. Each function/class with its purpose
3. Dependencies and how they're used
4. Any notable patterns or potential issues

Keep the explanation technical and precise."""

    console.print("\n[bold cyan]Analyzing...[/bold cyan]\n")

    try:
        for token in client.stream(SYSTEM_PROMPT, user_prompt):
            print(token, end="", flush=True)
        print()
    except Exception as e:
        console.print(f"\n[red]Error during analysis: {e}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


if __name__ == "__main__":
    app()