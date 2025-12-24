"""CLI interface for tf-diff."""

import sys
import click
from pathlib import Path
from rich.console import Console

from .parser import parse_plan
from .output import print_diff

console = Console()


@click.command()
@click.argument('file', type=click.Path(exists=True), required=False)
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['unified', 'summary']),
              default='unified',
              help='Output format (default: unified)')
@click.version_option()
def main(file: str, output_format: str):
    """Git diff style output for Terraform plan.

    Reads Terraform plan JSON from file or stdin.

    Examples:

        terraform plan -json | tf-diff
        terraform show -json tfplan | tf-diff
        tf-diff plan.json
    """
    # Read input
    if file:
        json_input = Path(file).read_text()
    elif not sys.stdin.isatty():
        json_input = sys.stdin.read()
    else:
        console.print("[red]Error:[/] No input. Pipe terraform plan -json or provide a file.")
        console.print("\nUsage: terraform plan -json | tf-diff")
        raise click.Abort()

    # Parse
    changes = parse_plan(json_input)

    if not changes:
        console.print("[dim]No changes detected.[/dim]")
        return

    # Output
    if output_format == 'summary':
        from .parser import get_summary
        summary = get_summary(changes)
        console.print(f"[green]{summary['add']} to add[/], "
                      f"[yellow]{summary['change']} to change[/], "
                      f"[red]{summary['destroy']} to destroy[/]")
    else:
        print_diff(changes, console)


if __name__ == '__main__':
    main()
