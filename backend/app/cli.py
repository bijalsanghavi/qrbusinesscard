import sys
from typing import Optional

from .db import Base, engine


def create_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("[cli] Database tables ensured (create_all)")


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m app.cli <command>")
        print("Commands:\n  create-db   Ensure tables exist (create_all)")
        return 1
    cmd = argv[0]
    if cmd == "create-db":
        create_db()
        return 0
    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

