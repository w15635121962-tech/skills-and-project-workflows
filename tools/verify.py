#!/usr/bin/env python3
"""Verify the snapshot offline; never executes payload scripts or uses network."""

import argparse
import json
import sys
from migration_common import MigrationError, inferred_repo, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(inferred_repo(__file__)), help="Snapshot repository directory")
    args = parser.parse_args()
    try:
        summary, _, _ = validate(args.repo)
    except (MigrationError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(dict(status="verified", **summary), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
