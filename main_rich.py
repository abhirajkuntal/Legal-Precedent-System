import time

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn
)
from rich.text import Text
from rich.align import Align

from src.ingestion.loader import load_all_cases
from src.graph.citation_graph import CitationGraph
from src.graph.citation_resolver import CitationResolver
from src.retrieval.chunk_search import ChunkSearchEngine
from src.llm.llm_query_parser import LLMQueryParser


# =========================================
# RICH CONSOLE
# =========================================
console = Console()


# =========================================
# SPINNER HELPER
# =========================================
def run_with_spinner(text, func, *args, **kwargs):

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=console
    ) as progress:

        progress.add_task(
            description=text,
            total=None
        )

        result = func(*args, **kwargs)

    return result


# =========================================
# LOAD CASES
# =========================================
cases = run_with_spinner(
    "Loading legal cases...",
    load_all_cases,
    "data/raw"
)

console.print(
    f"\n[bold green]✓ Loaded {len(cases)} cases[/bold green]"
)


# =========================================
# BUILD CITATION GRAPH
# =========================================
resolver = CitationResolver(cases)

citation_graph = CitationGraph(
    resolver=resolver
)


def build_graph():

    for case in cases:
        citation_graph.add_case(case)


run_with_spinner(
    "Building citation graph...",
    build_graph
)


# =========================================
# INIT SEARCH ENGINE
# =========================================
search_engine = ChunkSearchEngine(
    cases,
    citation_graph=citation_graph
)

query_parser = LLMQueryParser()


# =========================================
# HEADER
# =========================================
title = Text(
    "LEGAL PRECEDENT SEARCH ENGINE",
    style="bold white on blue"
)

console.print("\n")
console.print(
    Align.center(title)
)

console.print(
    Align.center(
        "[italic cyan]AI-Powered Legal Research Assistant[/italic cyan]"
    )
)

console.print("\n")


# =========================================
# MAIN LOOP
# =========================================
while True:

    console.print(
        Rule(
            "[bold blue]NEW LEGAL SEARCH[/bold blue]"
        )
    )

    query = console.input(
        "\n[bold yellow]Enter Query[/bold yellow] "
        "(or type 'exit'): "
    )

    if query.lower() == "exit":
        break

    court_input = console.input(
        "[cyan]Court Filter (optional): [/cyan]"
    ).strip()

    jurisdiction_input = console.input(
        "[cyan]Jurisdiction Filter (optional): [/cyan]"
    ).strip()

    judge_input = console.input(
        "[cyan]Judge Filter (optional): [/cyan]"
    ).strip()

    category_input = console.input(
        "[cyan]Category Filter (optional): [/cyan]"
    ).strip()

    # =========================================
    # QUERY PARSING
    # =========================================
    parsed = run_with_spinner(
        "Parsing legal query...",
        query_parser.parse_query,
        query
    )

    court = (
        court_input
        if court_input
        else parsed.get("court")
    )

    jurisdiction = (
        jurisdiction_input
        if jurisdiction_input
        else parsed.get("jurisdiction")
    )

    judge = (
        judge_input
        if judge_input
        else parsed.get("judge")
    )

    category = (
        category_input
        if category_input
        else parsed.get("category")
    )

    # =========================================
    # INPUT SUMMARY
    # =========================================
    summary_table = Table(
        show_header=False,
        expand=True
    )

    summary_table.add_column(
        "Field",
        style="bold cyan"
    )

    summary_table.add_column(
        "Value",
        style="white"
    )

    summary_table.add_row(
        "Query",
        parsed.get("semantic_query", query)
    )

    summary_table.add_row(
        "Court",
        str(court or "None")
    )

    summary_table.add_row(
        "Jurisdiction",
        str(jurisdiction or "None")
    )

    summary_table.add_row(
        "Judge",
        str(judge or "None")
    )

    summary_table.add_row(
        "Category",
        str(category or "None")
    )

    console.print(
        Panel(
            summary_table,
            title="[bold green]INPUT SUMMARY[/bold green]",
            border_style="green"
        )
    )

    # =========================================
    # SEARCH
    # =========================================
    search_output = run_with_spinner(
        "Searching precedents and ranking cases...",
        search_engine.search,
        query=parsed["semantic_query"],
        court=court,
        jurisdiction=jurisdiction,
        judge=judge,
        category=category
    )

    results = search_output["results"]

    # =========================================
    # NO RESULTS FOUND
    # =========================================
    if not results:

        console.print(
            Panel(
                "[bold red]No sufficiently relevant legal precedents found.[/bold red]\n\n"
                "[yellow]Suggestions:[/yellow]\n"
                "• Broaden the legal query\n"
                "• Remove restrictive filters\n"
                "• Try different legal terminology\n"
                "• Check spelling of courts/judges/categories",
                title="[bold red]NO RESULTS FOUND[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
        )

        continue

    # =========================================
    # RESULTS HEADER
    # =========================================
    console.print(
        Rule(
            "[bold magenta]TOP LEGAL PRECEDENTS[/bold magenta]"
        )
    )

    # =========================================
    # STREAM RESULTS
    # =========================================
    for i, result in enumerate(results, start=1):

        chunk = result["chunk"]

        score = result["score"]

        # -------------------------------------
        # SCORE COLORING
        # -------------------------------------
        if score >= 8:
            score_style = "bold green"

        elif score >= 5:
            score_style = "bold yellow"

        else:
            score_style = "bold red"

        # -------------------------------------
        # CASE TABLE
        # -------------------------------------
        table = Table(
            show_header=False,
            expand=True
        )

        table.add_column(
            "Field",
            style="bold cyan",
            width=18
        )

        table.add_column(
            "Value",
            style="white"
        )

        table.add_row(
            "Case Title",
            str(chunk.case_title)
        )

        table.add_row(
            "Case ID",
            str(chunk.case_id)
        )

        table.add_row(
            "Court",
            str(chunk.court)
        )

        table.add_row(
            "Jurisdiction",
            str(chunk.jurisdiction)
        )

        table.add_row(
            "Judges",
            str(chunk.judges)
        )

        table.add_row(
            "Category",
            str(chunk.legal_category)
        )

        table.add_row(
            "Score",
            f"[{score_style}]{score:.4f}[/{score_style}]"
        )

        # -------------------------------------
        # DETAILS
        # -------------------------------------
        details = f"""

[bold yellow]SUMMARY[/bold yellow]
{result.get("summary", "")}

[bold yellow]LEGAL ISSUE[/bold yellow]
{result.get("legal_issue", "")}

[bold yellow]REASONING[/bold yellow]
{result.get("reasoning", "")}

[bold yellow]HOLDING[/bold yellow]
{result.get("holding", "")}

[bold yellow]PROCEDURAL POSTURE[/bold yellow]
{result.get("procedural_posture", "")}
"""

        console.print(
            Panel(
                table,
                title=f"[bold blue]CASE {i}[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
        )

        console.print(
            Panel(
                details,
                border_style="magenta",
                padding=(1, 2)
            )
        )

        time.sleep(0.25)

console.print(
    "\n[bold red]Exiting Legal Precedent Search Engine[/bold red]"
)
