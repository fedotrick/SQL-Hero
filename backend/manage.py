#!/usr/bin/env python3
"""
Management CLI for database operations.
"""
import sys

from app.cli.refresh_leaderboard import main as refresh_leaderboard_main
from app.cli.seed import main as seed_main


def print_help() -> None:
    print("""
Database Management CLI

Usage:
    python manage.py <command>

Commands:
    seed                  Load seed data into the database (idempotent)
    refresh-leaderboard   Refresh the leaderboard cache from users' XP data
    help                  Show this help message

Examples:
    python manage.py seed
    python manage.py refresh-leaderboard
    """)


def main() -> None:
    if len(sys.argv) < 2:
        print("Error: No command specified")
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "seed":
        seed_main()
    elif command == "refresh-leaderboard":
        refresh_leaderboard_main()
    elif command == "help" or command == "--help" or command == "-h":
        print_help()
    else:
        print(f"Error: Unknown command '{command}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
