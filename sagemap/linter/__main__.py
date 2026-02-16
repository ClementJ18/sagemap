"""Command-line interface for the sagemap linter."""

import argparse
import inspect
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Type

from ..map import parse_map_from_path
from . import errors as errors_module
from .errors import LintError, Severity
from .linter import lint_map

if TYPE_CHECKING:
    from .errors import LintError


def format_error(error: "LintError", verbose: bool = False) -> str:
    """Format a lint error for display."""
    severity_colors = {
        Severity.ERROR: "\033[91m",  # Red
        Severity.WARNING: "\033[93m",  # Yellow
        Severity.INFO: "\033[94m",  # Blue
    }
    reset_color = "\033[0m"

    color = severity_colors.get(error.severity, "")
    severity_label = f"{color}{error.severity}{reset_color}"

    if verbose:
        return f"{severity_label} {error}"
    else:
        return str(error)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Lint BFME map files for common issues and best practices.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s map.map
  %(prog)s map.map --exclude MAP-013 MAP-014
  %(prog)s map.map --severity ERROR
  %(prog)s map.map --no-color --quiet
        """,
    )

    parser.add_argument("map_file", type=Path, help="Path to the .map file to lint")

    parser.add_argument(
        "-e", "--exclude", nargs="+", metavar="CODE", help="Error codes to exclude from results (e.g., MAP-013 MAP-014)"
    )

    parser.add_argument(
        "-s", "--severity", choices=["ERROR", "WARNING", "INFO"], help="Only show errors of this severity or higher"
    )

    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    parser.add_argument("-q", "--quiet", action="store_true", help="Only show error count, not individual errors")

    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose error messages")

    parser.add_argument("--list-codes", action="store_true", help="List all possible error codes and exit")

    args = parser.parse_args()

    if args.list_codes:
        print_error_codes()
        return 0

    if not args.map_file.exists():
        print(f"Error: Map file not found: {args.map_file}", file=sys.stderr)
        return 1

    try:
        print(f"Linting {args.map_file}...")
        map_obj = parse_map_from_path(str(args.map_file))
    except Exception as e:
        print(f"Error: Failed to parse map file: {e}", file=sys.stderr)
        return 1

    errors = lint_map(map_obj, exclude_codes=args.exclude)

    if args.severity:
        severity_order = {"INFO": 0, "WARNING": 1, "ERROR": 2}
        min_severity = severity_order[args.severity]
        errors = [err for err in errors if severity_order.get(err.severity, 0) >= min_severity]

    if not args.quiet:
        if errors:
            for error in errors:
                if args.no_color:
                    print(str(error))
                else:
                    print(format_error(error, args.verbose))
        else:
            print("✓ No issues found!")

    error_count = sum(1 for e in errors if e.severity == Severity.ERROR)
    warning_count = sum(1 for e in errors if e.severity == Severity.WARNING)
    info_count = sum(1 for e in errors if e.severity == Severity.INFO)

    print(f"\nSummary: {error_count} error(s), {warning_count} warning(s), {info_count} info")

    return 1 if error_count > 0 else 0


def print_error_codes():
    error_classes: list[Type[LintError]] = []
    for _, obj in inspect.getmembers(errors_module, inspect.isclass):
        if issubclass(obj, LintError) and obj is not LintError:
            error_classes.append(obj)

    codes: list[tuple[str, str, str]] = []
    for error_class in error_classes:
        code = error_class.code
        description = error_class.message_template.split("{")[0].strip()
        if not description:
            description = error_class.message_template
        severity = error_class.severity
        codes.append((code, description, severity))

    codes.sort(key=lambda x: x[0])

    print("Available error codes:\n")
    for code, description, severity in codes:
        severity_label = f"[{severity}]".ljust(10)
        print(f"  {code}: {severity_label} {description}")


if __name__ == "__main__":
    sys.exit(main())
