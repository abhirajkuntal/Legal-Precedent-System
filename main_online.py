import time

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.align import Align

from src.services.legal_search_service import LegalSearchService


console = Console()


def run_with_spinner(text, func, *args, **kwargs):
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=text, total=None)
        return func(*args, **kwargs)


# =========================================
# INIT SERVICE (ONLINE ONLY)
# =========================================
service = run_with_spinner(
    "Initializing Legal Search Service",
    LegalSearchService
)


# =========================================
# HEADER
# =========================================
title = Text(
    "LEGAL PRECEDENT SEARCH ENGINE",
    style="bold white on blue"
)

console.print("\n")
console.print(Align.center(title))
console.print(Align.center("[italic cyan]AI-Powered Legal Research Assistant[/italic cyan]"))
console.print("\n")


# =========================================
# MAIN LOOP
# =========================================
while True:

    console.print(Rule("[bold blue]NEW LEGAL SEARCH[/bold blue]"))

    query = console.input("\n[bold yellow]Enter Query (or exit): [/bold yellow]")

    if query.lower() == "exit":
        break

    court_input = console.input("[cyan]Court Filter: [/cyan]").strip()
    jurisdiction_input = console.input("[cyan]Jurisdiction Filter: [/cyan]").strip()
    judge_input = console.input("[cyan]Judge Filter: [/cyan]").strip()
    category_input = console.input("[cyan]Category Filter: [/cyan]").strip()

    parsed = service.query_parser.parse_query(query)

    court = court_input or parsed.get("court")
    jurisdiction = jurisdiction_input or parsed.get("jurisdiction")
    judge = judge_input or parsed.get("judge")
    category = category_input or parsed.get("category")

    # =========================================
    # SEARCH
    # =========================================
    search_output = run_with_spinner(
        "Searching precedents and ranking cases...",
        service.search,
        query,
        court,
        jurisdiction,
        judge,
        category
    )

    results = search_output["results"]

    # =========================================
    # NO RESULTS
    # =========================================
    if not results:
        console.print(
            Panel(
                "[bold red]No results found[/bold red]",
                border_style="red"
            )
        )
        continue

    console.print(Rule("[bold magenta]TOP LEGAL PRECEDENTS[/bold magenta]"))

    # =========================================
    # RESULTS
    # =========================================
    for i, result in enumerate(results, start=1):

        chunk = result["chunk"]
        score = result["score"]

        if score >= 8:
            style = "bold green"
        elif score >= 5:
            style = "bold yellow"
        else:
            style = "bold red"

        table = Table(show_header=False, expand=True)
        table.add_column("Field", style="bold cyan", width=18)
        table.add_column("Value", style="white")

        table.add_row("Case Title", str(chunk.case_title))
        table.add_row("Case ID", str(chunk.case_id))
        table.add_row("Court", str(chunk.court))
        table.add_row("Jurisdiction", str(chunk.jurisdiction))
        table.add_row("Judges", str(chunk.judges))
        table.add_row("Category", str(chunk.legal_category))
        table.add_row("Score", f"[{style}]{score:.4f}[/{style}]")

        details = f"""
[bold yellow]SUMMARY[/bold yellow]
{result.get("summary","")}

[bold yellow]LEGAL ISSUE[/bold yellow]
{result.get("legal_issue","")}

[bold yellow]REASONING[/bold yellow]
{result.get("reasoning","")}

[bold yellow]HOLDING[/bold yellow]
{result.get("holding","")}

[bold yellow]PROCEDURAL POSTURE[/bold yellow]
{result.get("procedural_posture","")}
"""

        console.print(Panel(table, title=f"CASE {i}", border_style="blue"))
        console.print(Panel(details, border_style="magenta"))

        time.sleep(0.25)


console.print("\n[bold red]Exiting System[/bold red]")
