#!/usr/bin/env python3
"""
nbdl.py — NotebookLM downloader
Selects a notebook and downloads notes, sources, and artifacts.
"""
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from notebooklm import NotebookLMClient
from notebooklm.types import Notebook

# Monkey-patch: fixes sources_count always returning 0 (bug in notebooklm-py).
# Remove when upstream ships the fix.
_original_from_api_response = Notebook.from_api_response

def _patched_from_api_response(cls, data):
    nb = _original_from_api_response(data)
    if len(data) > 1 and isinstance(data[1], list):  # data[1] is the sources list
        nb.sources_count = len(data[1])
    return nb

Notebook.from_api_response = classmethod(_patched_from_api_response)

console = Console()


def slugify(text: str) -> str:
    """Converts a string into a safe directory name."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:80] or "notebook"


async def pick_notebook(notebooks: list[Notebook]) -> Notebook | None:
    """Displays the notebook list and asks which one to download (with autocomplete)."""
    if not notebooks:
        console.print("[red]No notebooks found.[/red]")
        return None

    table = Table(title="Your Notebooks", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold cyan")
    table.add_column("Sources", justify="right")
    table.add_column("Created", style="dim")

    for i, nb in enumerate(notebooks, 1):
        created = nb.created_at.strftime("%Y-%m-%d") if nb.created_at else "—"
        table.add_row(str(i), nb.title, str(nb.sources_count), created)

    console.print(table)

    titles = [nb.title for nb in notebooks]
    numbers = [str(i) for i in range(1, len(notebooks) + 1)]
    completer = WordCompleter(titles + numbers, ignore_case=True, sentence=True)

    # prompt_async() instead of prompt(): required to work inside an already-running event loop
    session: PromptSession = PromptSession(completer=completer)

    while True:
        try:
            raw = (
                await session.prompt_async(
                    "\nSelect notebook (number or name, Tab to complete): "
                )
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if not raw:
            continue

        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(notebooks):
                return notebooks[idx]
            console.print(f"[red]Number out of range (1–{len(notebooks)}).[/red]")
            continue

        lower = raw.lower()
        exact = [nb for nb in notebooks if nb.title.lower() == lower]
        if exact:
            return exact[0]
        partial = [nb for nb in notebooks if lower in nb.title.lower()]
        if len(partial) == 1:
            return partial[0]
        if len(partial) > 1:
            console.print(
                "[yellow]Multiple notebooks match:[/yellow] "
                + ", ".join(f'"{nb.title}"' for nb in partial)
            )
            continue
        console.print("[red]No notebook found with that name.[/red]")


async def download_notes(client: NotebookLMClient, nb: Notebook, out_dir: Path) -> None:
    """Downloads all text notes as Markdown files."""
    notes_dir = out_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    notes = await client.notes.list(nb.id)
    if not notes:
        console.print("  [dim]No notes found.[/dim]")
        return

    console.print(f"  Downloading [bold]{len(notes)}[/bold] notes...")
    for note in notes:
        filename = notes_dir / f"{slugify(note.title or note.id)}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {note.title or '(untitled)'}\n\n")
            if note.created_at:
                f.write(f"_Created: {note.created_at.isoformat()}_\n\n")
            f.write(note.content or "")
        console.print(f"    [green]✓[/green] {filename.name}")


async def download_sources(client: NotebookLMClient, nb: Notebook, out_dir: Path) -> None:
    """Downloads fulltext of all sources as JSON + Markdown."""
    sources_dir = out_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    sources = await client.sources.list(nb.id)
    ready = [s for s in sources if s.is_ready]
    if not ready:
        console.print("  [dim]No sources ready.[/dim]")
        return

    console.print(f"  Downloading fulltext of [bold]{len(ready)}[/bold] sources...")
    for source in ready:
        try:
            ft = await client.sources.get_fulltext(nb.id, source.id)
        except Exception as e:
            console.print(f"    [red]✗[/red] {source.title or source.id}: {e}")
            continue

        base = slugify(ft.title or source.id)

        json_path = sources_dir / f"{base}.json"
        data = {
            "id": source.id,
            "title": ft.title,
            "url": ft.url,
            "kind": str(ft.kind),
            "char_count": ft.char_count,
            "content": ft.content,
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        md_path = sources_dir / f"{base}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {ft.title}\n\n")
            if ft.url:
                f.write(f"**Source:** {ft.url}\n\n")
            f.write(ft.content or "")

        console.print(f"    [green]✓[/green] {base}.md / .json ({ft.char_count:,} chars)")


async def download_artifacts(client: NotebookLMClient, nb: Notebook, out_dir: Path) -> None:
    """Downloads available artifacts (audio, quiz, mind-map…)."""
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    artifacts = await client.artifacts.list(nb.id)
    completed = [a for a in artifacts if a.is_completed]
    if not completed:
        console.print("  [dim]No completed artifacts.[/dim]")
        return

    console.print(f"  Downloading [bold]{len(completed)}[/bold] artifacts...")
    for art in completed:
        base = slugify(art.title or art.id)
        try:
            if art.kind.name == "AUDIO":
                path = str(artifacts_dir / f"{base}.mp3")
                await client.artifacts.download_audio(nb.id, path, artifact_id=art.id)
                console.print(f"    [green]✓[/green] {base}.mp3")

            elif art.kind.name in ("QUIZ", "FLASHCARDS"):
                path = str(artifacts_dir / f"{base}.json")
                await client.artifacts.download_quiz(nb.id, path, artifact_id=art.id, output_format="json")
                console.print(f"    [green]✓[/green] {base}.json")

            elif art.kind.name == "MIND_MAP":
                path = str(artifacts_dir / f"{base}.json")
                await client.artifacts.download_mind_map(nb.id, path, artifact_id=art.id)
                console.print(f"    [green]✓[/green] {base}.json (mind map)")

            else:
                console.print(f"    [dim]skip[/dim] {art.title} ({art.kind.name})")

        except Exception as e:
            console.print(f"    [red]✗[/red] {art.title}: {e}")


async def main() -> None:
    console.print(Panel.fit("[bold cyan]NotebookLM Downloader[/bold cyan]", subtitle="nbdl.py"))

    async with await NotebookLMClient.from_storage() as client:
        console.print("Loading notebook list...", end=" ")
        notebooks = await client.notebooks.list()
        console.print(f"[green]{len(notebooks)} found[/green]\n")

        nb = await pick_notebook(notebooks)
        if nb is None:
            console.print("[yellow]Cancelled.[/yellow]")
            return

        console.print(f"\n[bold]Selected notebook:[/bold] [cyan]{nb.title}[/cyan] (id: {nb.id})\n")

        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("output") / f"{slugify(nb.title)}_{today}"
        out_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "id": nb.id,
            "title": nb.title,
            "sources_count": nb.sources_count,
            "created_at": nb.created_at.isoformat() if nb.created_at else None,
            "downloaded_at": datetime.now().isoformat(),
        }
        (out_dir / "notebook.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        console.print("[bold]→ Notes[/bold]")
        await download_notes(client, nb, out_dir)

        console.print("\n[bold]→ Sources[/bold]")
        await download_sources(client, nb, out_dir)

        console.print("\n[bold]→ Artifacts[/bold]")
        await download_artifacts(client, nb, out_dir)

        console.print(
            f"\n[bold green]Done![/bold green] Output saved to: [cyan]{out_dir}[/cyan]"
        )


if __name__ == "__main__":
    asyncio.run(main())
