"""
e2D CLI entry point — allows `python -m e2D` commands.

Usage:
    py -m e2D -V          Show version
    py -m e2D --version   Show version
    py -m e2D --info      Show version and build info
"""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="e2D",
        description="e2D — High-Performance 2D Graphics and Math Library",
    )
    parser.add_argument(
        "-V", "--version",
        action="store_true",
        help="show e2D version and exit",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="show detailed build/environment info",
    )

    args = parser.parse_args()

    from . import __version__

    if args.version:
        print(f"e2D {__version__}")
        sys.exit(0)

    if args.info:
        print(f"e2D {__version__}")
        print(f"  Python     : {sys.version}")
        print(f"  Platform   : {sys.platform}")
        try:
            from . import _VECTOR_COMPILED
        except Exception:
            _VECTOR_COMPILED = False
        try:
            from . import _COLOR_COMPILED
        except Exception:
            _COLOR_COMPILED = False
        print(f"  Cython vectors : {'yes' if _VECTOR_COMPILED else 'no (pure-Python fallback)'}")
        print(f"  Cython colors  : {'yes' if _COLOR_COMPILED else 'no (pure-Python fallback)'}")
        sys.exit(0)

    # No flags → show help
    parser.print_help()


if __name__ == "__main__":
    main()
