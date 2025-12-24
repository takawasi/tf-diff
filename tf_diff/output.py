"""Rich formatted output for Terraform changes."""

from typing import List
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from .parser import ResourceChange, get_summary


def print_diff(changes: List[ResourceChange], console: Console):
    """Print changes in git diff style."""
    if not changes:
        console.print("[dim]No changes detected.[/dim]")
        return

    # Summary
    summary = get_summary(changes)
    summary_text = Text()
    summary_text.append("Plan: ")
    summary_text.append(f"{summary['add']} to add", style="bold green")
    summary_text.append(", ")
    summary_text.append(f"{summary['change']} to change", style="bold yellow")
    summary_text.append(", ")
    summary_text.append(f"{summary['destroy']} to destroy", style="bold red")
    console.print(summary_text)
    console.print()

    # Group by action for cleaner output
    for change in changes:
        _print_resource_change(change, console)
        console.print()


def _print_resource_change(change: ResourceChange, console: Console):
    """Print a single resource change."""
    # Header with action indicator
    action_styles = {
        'create': ('green', '+'),
        'delete': ('red', '-'),
        'update': ('yellow', '~'),
        'replace': ('magenta', '±'),
    }
    style, symbol = action_styles.get(change.action, ('white', '?'))

    header = Text()
    header.append(f"━━━ {change.address} ", style=f"bold {style}")
    header.append(f"({change.action}) ", style=style)
    header.append("━━━", style=f"bold {style}")
    console.print(header)

    if change.action == 'create':
        _print_additions(change.after, console)
    elif change.action == 'delete':
        _print_deletions(change.before, console)
    elif change.action in ('update', 'replace'):
        _print_modifications(change, console)


def _print_additions(after: dict, console: Console):
    """Print all attributes as additions."""
    for key, value in sorted(after.items()):
        if value is None:
            continue
        line = Text()
        line.append("+ ", style="green")
        line.append(f"{key:20} = ", style="dim")
        line.append(_format_value(value), style="green")
        console.print(line)


def _print_deletions(before: dict, console: Console):
    """Print all attributes as deletions."""
    for key, value in sorted(before.items()):
        if value is None:
            continue
        line = Text()
        line.append("- ", style="red")
        line.append(f"{key:20} = ", style="dim")
        line.append(_format_value(value), style="red")
        console.print(line)


def _print_modifications(change: ResourceChange, console: Console):
    """Print modifications with before/after diff."""
    all_keys = set(change.before.keys()) | set(change.after.keys())

    for key in sorted(all_keys):
        before_val = change.before.get(key)
        after_val = change.after.get(key)

        if before_val == after_val:
            # Unchanged
            if before_val is not None:
                line = Text()
                line.append("  ", style="dim")
                line.append(f"{key:20} = ", style="dim")
                line.append(_format_value(before_val), style="dim")
                line.append(" (unchanged)", style="dim italic")
                console.print(line)
        elif before_val is None:
            # Added
            line = Text()
            line.append("+ ", style="green")
            line.append(f"{key:20} = ", style="dim")
            line.append(_format_value(after_val), style="green")
            console.print(line)
        elif after_val is None:
            # Removed
            line = Text()
            line.append("- ", style="red")
            line.append(f"{key:20} = ", style="dim")
            line.append(_format_value(before_val), style="red")
            console.print(line)
        else:
            # Changed
            line_before = Text()
            line_before.append("- ", style="red")
            line_before.append(f"{key:20} = ", style="dim")
            line_before.append(_format_value(before_val), style="red")
            console.print(line_before)

            line_after = Text()
            line_after.append("+ ", style="green")
            line_after.append(f"{key:20} = ", style="dim")
            line_after.append(_format_value(after_val), style="green")
            console.print(line_after)


def _format_value(value) -> str:
    """Format a value for display."""
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, dict):
        if len(value) == 0:
            return '{}'
        items = ', '.join(f'{k}={_format_value(v)}' for k, v in list(value.items())[:3])
        if len(value) > 3:
            items += ', ...'
        return '{ ' + items + ' }'
    elif isinstance(value, list):
        if len(value) == 0:
            return '[]'
        items = ', '.join(_format_value(v) for v in value[:3])
        if len(value) > 3:
            items += ', ...'
        return '[ ' + items + ' ]'
    else:
        return str(value)
