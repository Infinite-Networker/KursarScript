"""
KursarScript CLI - Command-line interface for running .kursar files.

Usage:
    kursarscript script.kursar          # Run a script
    kursarscript -i                     # Interactive REPL
    kursarscript --version              # Show version
    python -m kursarscript script.kursar
"""

import sys
import os
import argparse

def _get_version() -> str:
    try:
        from kursarscript import __version__
        return __version__
    except ImportError:
        return "1.0.0"


def run_file(path: str) -> int:
    """Execute a .kursar file. Returns exit code."""
    if not os.path.isfile(path):
        print(f"kursarscript: file not found: {path}", file=sys.stderr)
        return 2

    with open(path, 'r', encoding='utf-8') as fh:
        source = fh.read()

    from kursarscript import KSPLInterpreter, KSPLRuntimeError
    interpreter = KSPLInterpreter()
    try:
        interpreter.run(source)
        return 0
    except KSPLRuntimeError as exc:
        print(f"[KursarScript RuntimeError] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[KursarScript Error] {exc}", file=sys.stderr)
        return 1


def run_repl() -> None:
    """Start an interactive REPL session."""
    from kursarscript import KSPLInterpreter, KSPLRuntimeError, __version__

    print(f"KursarScript {__version__} Interactive Mode")
    print("Type 'exit' or 'quit' to leave.  Type 'help' for quick reference.\n")

    interpreter = KSPLInterpreter()
    buffer: list = []

    while True:
        prompt = "... " if buffer else ">>> "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting REPL.")
            break

        if line.strip() in ('exit', 'quit'):
            break

        if line.strip() == 'help':
            _print_help()
            continue

        # Accumulate multi-line blocks
        buffer.append(line)
        source = '\n'.join(buffer)

        # Check for unmatched braces → keep accumulating
        if source.count('{') > source.count('}'):
            continue

        try:
            interpreter.run(source)
        except KSPLRuntimeError as exc:
            print(f"RuntimeError: {exc}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error: {exc}")
        finally:
            buffer.clear()


def _print_help() -> None:
    print("""
KursarScript Quick Reference
─────────────────────────────
Variables:   let x = 42
Assignment:  x = 100
Functions:   fn greet(name) { print("Hello", name) }
Classes:     class MyClass { field x = 0  fn init(v) { self.x = v } }
If/else:     if (x > 0) { print("pos") } else { print("non-pos") }
For loop:    for item in list { print(item) }
Print:       print("Hello, World!")
Avatars:     let a = Avatar("Alice", "explorer")
VirtuCard:   a.virtucard = create_virtucard(a, 500.0)
Transfer:    transfer(a.virtucard, b.virtucard, 100.0)
Terminal:    let t = VirtualTerminal("Shop", "general")
Item:        let i = VirtualItem("Sword", "weapon", 150.0)
""")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog='kursarscript',
        description='KursarScript (KSPL) - Virtual Reality Programming Language',
    )
    parser.add_argument('file', nargs='?', help='.kursar script to run')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Start interactive REPL')
    parser.add_argument('-v', '--vr', action='store_true',
                        help='Enable VR simulation mode (future feature)')
    parser.add_argument('--version', action='store_true',
                        help='Show version and exit')

    args = parser.parse_args(argv)

    if args.version:
        print(f"KursarScript {_get_version()}")
        return 0

    if args.interactive or args.file is None:
        run_repl()
        return 0

    return run_file(args.file)


if __name__ == '__main__':
    sys.exit(main())
