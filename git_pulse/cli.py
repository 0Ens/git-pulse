import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

from git_pulse.config import ConfigManager
from git_pulse.scanner import find_git_repos
from git_pulse.analyzer import analyze_repo

app = typer.Typer(
    name="git-pulse",
    help="The heartbeat of your local development environment.",
    no_args_is_help=True,
)
ignore_app = typer.Typer(help="Manage ignored folders.")
app.add_typer(ignore_app, name="ignore")

config = ConfigManager()
console = Console()


@app.command()
def scan(
    directory: Path = typer.Argument(
        ...,
        help="Directory to scan for git repositories.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
):
    """Scan a directory and report the git activity inside it."""
    ignored = config.get_ignored_folders()

    console.print(f"\n[bold cyan]Git Pulse[/bold cyan] — scanning [bold]{directory}[/bold]")
    console.print(f"[dim]Ignoring: {', '.join(ignored) if ignored else 'nothing'}[/dim]\n")

    with console.status("[bold green]Repos aranıyor...[/bold green]"):
        repos = find_git_repos(directory, ignored)

    if not repos:
        console.print("[yellow]Hiç git reposu bulunamadı.[/yellow]")
        raise typer.Exit()

    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("Repo", style="bold white", no_wrap=True)
    table.add_column("Branch", style="cyan")
    table.add_column("Son Commit", style="dim")
    table.add_column("Mesaj", max_width=40)
    table.add_column("Yazar", style="magenta")
    table.add_column("Ne zaman", style="dim")
    table.add_column("Durum", justify="center")

    with console.status("[bold green]Repolar analiz ediliyor...[/bold green]"):
        for repo_path in repos:
            status = analyze_repo(repo_path)

            relative = repo_path.relative_to(directory) if repo_path != directory else Path(".")
            dirty_label = f"[red]dirty ({status.uncommitted_count})[/red]" if status.is_dirty else "[green]clean[/green]"

            table.add_row(
                str(relative),
                status.branch,
                status.last_commit_hash,
                status.last_commit_message,
                status.last_commit_author,
                status.last_commit_date,
                dirty_label,
            )

    console.print(table)
    console.print(f"\n[bold]{len(repos)}[/bold] repo bulundu.\n")


@ignore_app.command("list")
def ignore_list():
    """List all ignored folders."""
    folders = config.get_ignored_folders()
    if not folders:
        console.print("[yellow]Hiç ignore klasörü yok.[/yellow]")
        return
    for folder in folders:
        console.print(f"  [dim]-[/dim] {folder}")


@ignore_app.command("add")
def ignore_add(folder: str = typer.Argument(..., help="Folder name to ignore.")):
    """Add a folder to the ignore list."""
    if config.add_ignored_folder(folder):
        console.print(f"[green]'{folder}' ignore listesine eklendi.[/green]")
    else:
        console.print(f"[yellow]'{folder}' zaten listede.[/yellow]", highlight=False)
        raise typer.Exit(1)


@ignore_app.command("remove")
def ignore_remove(folder: str = typer.Argument(..., help="Folder name to stop ignoring.")):
    """Remove a folder from the ignore list."""
    if config.remove_ignored_folder(folder):
        console.print(f"[green]'{folder}' ignore listesinden çıkarıldı.[/green]")
    else:
        console.print(f"[yellow]'{folder}' listede değil.[/yellow]", highlight=False)
        raise typer.Exit(1)


def main():
    app()
