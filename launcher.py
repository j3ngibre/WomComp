
#!/usr/bin/env python3

import argparse
import sys

import conf_tester


def main():
    parser = argparse.ArgumentParser(
        description=(
            "WomComp - Linux Compliance Scanner for GRC, "
            "SysAdmin, and Blue Team"
        ),
        epilog="Example: python3 launcher.py -b -v",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-f",
        "--file",
        help="YAML file with tests",
    )

    group.add_argument(
        "-b",
        "--basic",
        action="store_true",
        help="Use basic file: bconf.yaml",
    )

    group.add_argument(
        "-c",
        "--complex",
        action="store_true",
        help="Use complex file: cconf.yaml",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed proofs",
    )

    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Silent mode (only show summary)",
    )

    args = parser.parse_args()

    # Select YAML file
    if args.basic:
        yaml_file = "bconf.yaml"
    elif args.complex:
        yaml_file = "cconf.yaml"
    elif args.file:
        yaml_file = args.file
    else:
        yaml_file = "bconf.yaml"

    if not args.silent:
        print("WomComp Starting...")
        print(f"Using test file: {yaml_file}")
        print()

    # Load tests
    try:
        tests = conf_tester.fileLoad(yaml_file)
    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error loading YAML file '{yaml_file}': {exc}", file=sys.stderr)
        sys.exit(1)

    if not tests:
        print(
            "No tests loaded. Please check the YAML file.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run tests
    results = conf_tester.checkTests(tests, args.verbose)

    # Silent mode: show only summary
    if args.silent:
        passed = sum(1 for result in results if result[1])
        total = len(results)

        score = (passed / total * 100) if total else 0.0

        print(
            f"Compliance Score: {passed}/{total} "
            f"passed ({score:.1f}%)"
        )


if __name__ == "__main__":
    main()
