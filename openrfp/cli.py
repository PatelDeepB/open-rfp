"""Command Line Interface for OpenRFP."""

from pathlib import Path
from typing import Optional
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from openrfp import __version__
from openrfp.config import settings
from openrfp.core.drafter import ProposalDrafter
from openrfp.core.exporter import ProposalExporter
from openrfp.core.parser import RfpParser
from openrfp.core.retriever import KnowledgeRetriever
from openrfp.models import ConfidenceLevel, KnowledgeItem, RequirementCategory
from openrfp.storage import StorageService

app = typer.Typer(
    name="open-rfp",
    help="Autonomous AI RFP and Proposal Response Agent",
    add_completion=False,
)
kb_app = typer.Typer(name="kb", help="Manage enterprise knowledge base")
app.add_typer(kb_app)

console = Console()
storage = StorageService()
parser = RfpParser()
exporter = ProposalExporter()


@app.command()
def version() -> None:
    """Print the OpenRFP version."""
    console.print(f"[bold cyan]OpenRFP[/bold cyan] version [green]{__version__}[/green]")


@app.command()
def shred(
    file_path: Path = typer.Argument(..., help="Path to RFP document (txt or md)"),
    buyer: str = typer.Option("Client", help="Name of prospective buyer"),
) -> None:
    """Shred an RFP solicitation into a structured compliance matrix."""
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File '{file_path}' does not exist.")
        raise typer.Exit(code=1)

    with console.status("[bold green]Parsing solicitation and requirements..."):
        rfp = parser.parse_file(file_path, buyer_name=buyer)
        storage.save_rfp(rfp)

    console.print(Panel(f"[bold green]Parsed RFP:[/bold green] {rfp.title} ({len(rfp.requirements)} requirements)"))
    table = Table(title="Compliance Matrix")
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Section", style="magenta", width=22)
    table.add_column("Requirement", style="white")
    table.add_column("Priority", style="yellow", width=12)
    table.add_column("Category", style="blue", width=22)

    for req in rfp.requirements:
        table.add_row(req.id, req.section_title, req.requirement_text, req.priority.value, req.category.value)
    console.print(table)


@app.command()
def draft(
    file_path: Path = typer.Argument(..., help="Path to RFP document"),
    buyer: str = typer.Option("Client", help="Name of prospective buyer"),
    output_dir: Optional[Path] = typer.Option(None, help="Directory to save export deliverables"),
) -> None:
    """End-to-end: shred solicitation, match truth, synthesize answers and score."""
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File '{file_path}' does not exist.")
        raise typer.Exit(code=1)

    items = storage.get_all_knowledge_items()
    retriever = KnowledgeRetriever(items=items)
    drafter = ProposalDrafter(retriever=retriever)

    with console.status("[bold green]Synthesizing proposal response..."):
        rfp = parser.parse_file(file_path, buyer_name=buyer)
        storage.save_rfp(rfp)
        proposal = drafter.draft_proposal(rfp)
        storage.save_proposal(proposal)

    gap = proposal.gap_report
    console.print(Panel(
        f"[bold]Proposal Summary for {rfp.buyer_name}[/bold]\n"
        f"Win Readiness Score: [bold green]{proposal.win_probability_score}%[/bold green]\n"
        f"Verified: [green]{gap.green_count}[/green] | Review: [yellow]{gap.amber_count}[/yellow] | Gaps: [red]{gap.red_count}[/red]\n"
        f"Coverage: [cyan]{gap.completeness_percentage}%[/cyan]"
    ))

    if output_dir:
        files = exporter.save_all(proposal, rfp, output_dir)
        console.print(f"[green]Saved deliverables to:[/green] {output_dir}")
        for fmt, path in files.items():
            console.print(f"  - {fmt}: {path.name}")


@kb_app.command("list")
def list_knowledge() -> None:
    """List all verified enterprise truth records."""
    items = storage.get_all_knowledge_items()
    if not items:
        console.print("[yellow]Knowledge base is currently empty. Run 'open-rfp kb seed' to populate samples.[/yellow]")
        return

    table = Table(title="Enterprise Truth Repository")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Title", style="white", width=30)
    table.add_column("Category", style="blue", width=24)
    table.add_column("Verified By", style="green", width=16)

    for item in items:
        table.add_row(item.id, item.title, item.category.value, item.verified_by or "Verified")
    console.print(table)


@kb_app.command("seed")
def seed_knowledge() -> None:
    """Seed sample enterprise truth records."""
    from openrfp.core.seed import get_sample_enterprise_knowledge
    sample_items = get_sample_enterprise_knowledge()
    for item in sample_items:
        storage.save_knowledge_item(item)
    console.print(f"[green]Successfully seeded {len(sample_items)} enterprise truth records.[/green]")


@app.command()
def serve(
    host: str = typer.Option(settings.host, help="Host address to bind to"),
    port: int = typer.Option(settings.port, help="Port to listen on"),
) -> None:
    """Start the OpenRFP server with interactive Web UI and REST API."""
    console.print(f"[bold green]Starting OpenRFP Server[/bold green] on http://{host}:{port}")
    uvicorn.run("openrfp.api.server:app", host=host, port=port, reload=False)


def main() -> None:
    """Entry point for CLI script."""
    app()


if __name__ == "__main__":
    main()
